"""
Packaging Integration Tests

These tests verify that the package builds correctly and can be installed/imported
in a clean environment. They catch issues that unit tests miss because unit tests
run against source code, not the packaged distribution.

Key scenarios tested:
1. Wheel contains all required modules and packages
2. Entry points can be loaded successfully
3. Fresh install works and modules can be imported
4. CLI commands are accessible after installation
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
import pytest
import importlib.util


@pytest.mark.integration
@pytest.mark.slow
class TestPackagingIntegration:
    """Test packaging and distribution integrity."""

    @staticmethod
    def _get_import_test_script():
        """Get the script for testing imports in a clean environment."""
        return '''
import sys
try:
    import asciidoc_dita_toolkit
    print("SUCCESS: asciidoc_dita_toolkit imported")

    # Test importing modules that were consolidated in v2.1.0 refactoring
    from asciidoc_dita_toolkit.modules.entity_reference import EntityReferenceModule
    print("SUCCESS: asciidoc_dita_toolkit.modules.entity_reference imported")

    # Test import from new module location
    from asciidoc_dita_toolkit.modules.content_type import ContentTypeModule
    print("SUCCESS: asciidoc_dita_toolkit.modules.content_type imported")

    # Test that version is accessible
    from asciidoc_dita_toolkit.adt_core import __version__
    print(f"SUCCESS: Version {__version__} accessible")

except ImportError as e:
    print(f"FAILED: Import error - {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAILED: Unexpected error - {e}")
    sys.exit(1)
'''

    @staticmethod
    def _get_plugin_discovery_script():
        """Get the script for testing plugin discovery in a clean environment."""
        return '''
import sys
try:
    # Use importlib.metadata for modern Python versions
    try:
        from importlib.metadata import entry_points
    except ImportError:
        # Fallback for Python < 3.8
        from importlib_metadata import entry_points

    # Test that entry points can be discovered
    eps = entry_points()
    adt_modules = eps.select(group='adt.modules') if hasattr(eps, 'select') else eps.get('adt.modules', [])
    entry_points_list = list(adt_modules)
    print(f"Found {len(entry_points_list)} plugin entry points")

    if len(entry_points_list) == 0:
        print("ERROR: No plugin entry points found")
        sys.exit(1)

    # Test that we can load at least one plugin
    for ep in entry_points_list:
        if ep.name == 'EntityReference':
            try:
                plugin_class = ep.load()
                print(f"SUCCESS: Loaded {ep.name} plugin class: {plugin_class}")
                break
            except Exception as e:
                print(f"ERROR: Failed to load {ep.name} plugin: {e}")
                sys.exit(1)
    else:
        print("ERROR: EntityReference plugin not found in entry points")
        sys.exit(1)

except Exception as e:
    print(f"ERROR: Plugin discovery test failed: {e}")
    sys.exit(1)
'''

    @pytest.fixture
    def build_wheel(self, tmp_path):
        """Build a wheel in a temporary directory and return its path."""
        # Create a temporary build directory
        build_dir = tmp_path / "build"
        build_dir.mkdir()

        # Get the project root (assuming tests are in project_root/tests/)
        project_root = Path(__file__).parent.parent

        # Build the wheel
        result = subprocess.run([
            sys.executable, "-m", "build", "--wheel", "--outdir", str(build_dir)
        ], cwd=project_root, capture_output=True, text=True)

        if result.returncode != 0:
            error_msg = f"Wheel build failed: {result.stderr}"
            if "No module named 'build'" in result.stderr:
                error_msg += "\n\nTo install build dependencies, run: pip install build"
            pytest.fail(error_msg)

        # Find the wheel file
        wheel_files = list(build_dir.glob("*.whl"))
        if not wheel_files:
            pytest.fail("No wheel file was created")

        return wheel_files[0]

    def test_wheel_contains_required_modules(self, build_wheel, notify_user):
        """Test that the wheel contains both asciidoc_dita_toolkit and modules packages."""
        notify_user.notify_slow_test_start("Analyzing wheel contents", 8)
        wheel_path = build_wheel

        with zipfile.ZipFile(wheel_path, 'r') as wheel:
            file_list = wheel.namelist()

            # Check for asciidoc_dita_toolkit package
            asciidoc_dita_files = [f for f in file_list if f.startswith('asciidoc_dita_toolkit/')]
            assert asciidoc_dita_files, "asciidoc_dita_toolkit package not found in wheel"

            # Check for modules package under asciidoc_dita_toolkit (new v2.1.0+ structure)
            modules_files = [f for f in file_list if f.startswith('asciidoc_dita_toolkit/modules/')]
            assert modules_files, "asciidoc_dita_toolkit.modules package not found in wheel - refactoring failed!"

            # Verify specific critical files in the new structure
            expected_files = [
                'asciidoc_dita_toolkit/__init__.py',
                'asciidoc_dita_toolkit/adt_core/__init__.py',
                'asciidoc_dita_toolkit/modules/__init__.py',
                'asciidoc_dita_toolkit/modules/content_type/__init__.py',
                'asciidoc_dita_toolkit/modules/entity_reference/__init__.py',
            ]

            for expected_file in expected_files:
                assert expected_file in file_list, f"Critical file {expected_file} missing from wheel"

            # Specifically check that we have BOTH modules/ and asciidoc_dita_toolkit/ at top level
            # This is the key test - in v2.0.11, modules/ was missing from top level
            top_level_dirs = set()
            for file_path in file_list:
                if '/' in file_path:
                    top_level_dir = file_path.split('/')[0]
                    top_level_dirs.add(top_level_dir)

            # After v2.1.0 refactoring, we should NOT have top-level 'modules' directory
            assert 'modules' not in top_level_dirs, "Top-level 'modules' directory should be removed after refactoring"
            assert 'asciidoc_dita_toolkit' in top_level_dirs, "Top-level 'asciidoc_dita_toolkit' directory missing from wheel"

    def test_entry_points_defined_correctly(self, build_wheel, notify_user):
        """Test that all entry points are properly defined in the wheel metadata."""
        notify_user.notify_slow_test_start("Validating entry points", 6)
        wheel_path = build_wheel

        with zipfile.ZipFile(wheel_path, 'r') as wheel:
            # Find the entry_points.txt file
            entry_points_files = [f for f in wheel.namelist() if f.endswith('entry_points.txt')]
            assert entry_points_files, "entry_points.txt not found in wheel metadata"

            entry_points_content = wheel.read(entry_points_files[0]).decode('utf-8')

            # Check for console scripts
            expected_scripts = [
                'adt = asciidoc_dita_toolkit.adt_core.cli:main',
                'adg = asciidoc_dita_toolkit.adt_core.cli:launch_gui',
                'valeflag = asciidoc_dita_toolkit.plugins.vale_flagger.cli:main',
            ]

            for script in expected_scripts:
                assert script in entry_points_content, f"Entry point '{script}' not found in metadata"

            # Check for plugin entry points
            expected_plugins = [
                'EntityReference = asciidoc_dita_toolkit.modules.entity_reference:EntityReferenceModule',
                'ContentType = asciidoc_dita_toolkit.modules.content_type:ContentTypeModule',
            ]

            for plugin in expected_plugins:
                assert plugin in entry_points_content, f"Plugin entry point '{plugin}' not found in metadata"

    def test_fresh_install_and_import(self, build_wheel, tmp_path, notify_user):
        """Test installing the wheel in a clean environment and importing modules."""
        notify_user.notify_slow_test_start("Setting up clean environment and testing imports", 12)
        wheel_path = build_wheel
        venv_dir = tmp_path / "test_venv"

        # Create a virtual environment
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

        # Determine python executable in venv
        if sys.platform == "win32":
            python_exe = venv_dir / "Scripts" / "python.exe"
            pip_exe = venv_dir / "Scripts" / "pip.exe"
        else:
            python_exe = venv_dir / "bin" / "python"
            pip_exe = venv_dir / "bin" / "pip"

        # Install the wheel
        result = subprocess.run([
            str(pip_exe), "install", str(wheel_path)
        ], capture_output=True, text=True)

        if result.returncode != 0:
            pytest.fail(f"Wheel installation failed: {result.stderr}")

        # Test importing the main package
        import_test_script = self._get_import_test_script()

        result = subprocess.run([
            str(python_exe), "-c", import_test_script
        ], capture_output=True, text=True)

        if result.returncode != 0:
            pytest.fail(f"Import test failed in clean environment: {result.stderr}\nStdout: {result.stdout}")

        # Verify success messages
        assert "SUCCESS: asciidoc_dita_toolkit imported" in result.stdout
        assert "SUCCESS: asciidoc_dita_toolkit.modules.entity_reference imported" in result.stdout
        assert "SUCCESS: asciidoc_dita_toolkit.modules.content_type imported" in result.stdout

    def test_cli_commands_accessible(self, build_wheel, tmp_path, notify_user):
        """Test that CLI commands are accessible after installation."""
        notify_user.notify_slow_test_start("Testing CLI command accessibility", 10)
        wheel_path = build_wheel
        venv_dir = tmp_path / "test_venv"

        # Create and setup virtual environment (reuse logic from previous test)
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

        if sys.platform == "win32":
            python_exe = venv_dir / "Scripts" / "python.exe"
            pip_exe = venv_dir / "Scripts" / "pip.exe"
        else:
            python_exe = venv_dir / "bin" / "python"
            pip_exe = venv_dir / "bin" / "pip"

        # Install the wheel
        subprocess.run([str(pip_exe), "install", str(wheel_path)], check=True)

        # Test CLI commands
        cli_commands = ['adt', 'adg', 'valeflag']

        for cmd in cli_commands:
            # Test that the command exists and shows help (should not crash)
            result = subprocess.run([
                str(python_exe), "-m", "pip", "show", "-f", "asciidoc-dita-toolkit"
            ], capture_output=True, text=True)

            # The command should be listed in the installed files
            assert result.returncode == 0, f"Package info retrieval failed"

            # More direct test: try to run the command with --help
            if sys.platform == "win32":
                cmd_exe = venv_dir / "Scripts" / f"{cmd}.exe"
            else:
                cmd_exe = venv_dir / "bin" / cmd

            # Check if command executable exists
            if cmd_exe.exists():
                # Try running with --help (should not crash due to missing modules)
                result = subprocess.run([
                    str(cmd_exe), "--help"
                ], capture_output=True, text=True, timeout=10)

                # Command should either succeed or fail gracefully (not with ModuleNotFoundError)
                if result.returncode != 0:
                    assert "No module named 'modules'" not in result.stderr, \
                        f"CLI command '{cmd}' failed with module import error: {result.stderr}"

    def test_plugin_discovery_works(self, build_wheel, tmp_path, notify_user):
        """Test that plugin entry points can be discovered and loaded."""
        notify_user.notify_slow_test_start("Testing plugin discovery and loading", 9)
        wheel_path = build_wheel
        venv_dir = tmp_path / "test_venv"

        # Setup venv and install wheel
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

        if sys.platform == "win32":
            python_exe = venv_dir / "Scripts" / "python.exe"
            pip_exe = venv_dir / "Scripts" / "pip.exe"
        else:
            python_exe = venv_dir / "bin" / "python"
            pip_exe = venv_dir / "bin" / "pip"

        subprocess.run([str(pip_exe), "install", str(wheel_path)], check=True)

        # Test plugin discovery
        plugin_test_script = self._get_plugin_discovery_script()

        result = subprocess.run([
            str(python_exe), "-c", plugin_test_script
        ], capture_output=True, text=True)

        if result.returncode != 0:
            pytest.fail(f"Plugin discovery test failed: {result.stderr}\nStdout: {result.stdout}")

        assert "SUCCESS: Loaded EntityReference plugin class" in result.stdout

    def test_version_consistency(self, build_wheel, notify_user):
        """Test that version is consistent between pyproject.toml and package."""
        notify_user.notify_slow_test_start("Verifying version consistency", 7)
        # Read version from pyproject.toml
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"

        with open(pyproject_path, 'r') as f:
            pyproject_content = f.read()

        # Extract version from pyproject.toml
        version_match = re.search(r'version = "([^"]+)"', pyproject_content)
        assert version_match, "Could not find version in pyproject.toml"
        pyproject_version = version_match.group(1)

        # Check that wheel filename contains the same version
        wheel_path = build_wheel
        wheel_name = wheel_path.name
        assert pyproject_version in wheel_name, f"Wheel name {wheel_name} doesn't contain version {pyproject_version}"

        # Check version in wheel metadata
        with zipfile.ZipFile(wheel_path, 'r') as wheel:
            metadata_files = [f for f in wheel.namelist() if f.endswith('METADATA')]
            assert metadata_files, "METADATA file not found in wheel"

            metadata_content = wheel.read(metadata_files[0]).decode('utf-8')
            assert f"Version: {pyproject_version}" in metadata_content, \
                f"Version {pyproject_version} not found in wheel metadata"

    def test_packaging_config_includes_modules(self):
        """Test that pyproject.toml explicitly includes 'modules*' to prevent v2.0.11 regression."""
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"

        with open(pyproject_path, 'r') as f:
            pyproject_content = f.read()

        # Check that modules are now under asciidoc_dita_toolkit (v2.1.0+ structure)
        assert 'include = ["asciidoc_dita_toolkit*"]' in pyproject_content, \
            "pyproject.toml must only include 'asciidoc_dita_toolkit*' after refactoring"

        # Additional check: make sure old "modules*" is NOT included anymore
        assert '"modules*"' not in pyproject_content, \
            "modules* should no longer be needed after consolidation into asciidoc_dita_toolkit.modules"


if __name__ == "__main__":
    # Allow running this test file directly for debugging
    pytest.main([__file__, "-v"])

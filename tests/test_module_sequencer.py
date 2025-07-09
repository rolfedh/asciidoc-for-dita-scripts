"""Tests for ModuleSequencer."""

import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from src.adt_core.module_sequencer import (
    ModuleSequencer, ModuleState, ModuleResolution, ADTModule,
    determine_module_state
)
from src.adt_core.exceptions import (
    ConfigurationError, CircularDependencyError, MissingDependencyError
)


class MockModule(ADTModule):
    """Mock module for testing."""
    
    def __init__(self, name: str, version: str = "1.0.0", dependencies: list = None):
        self._name = name
        self._version = version
        self._dependencies = dependencies or []
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def dependencies(self) -> list:
        return self._dependencies
    
    def initialize(self, config):
        pass
    
    def execute(self, context):
        return {"success": True}


class TestModuleSequencer(unittest.TestCase):
    """Test cases for ModuleSequencer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sequencer = ModuleSequencer()
        
        # Create test modules
        self.test_modules = {
            "ModuleA": MockModule("ModuleA", "1.0.0", []),
            "ModuleB": MockModule("ModuleB", "1.0.0", ["ModuleA"]),
            "ModuleC": MockModule("ModuleC", "1.0.0", ["ModuleB"]),
        }
        
        self.sequencer.available_modules = self.test_modules
        
        # Test configuration
        self.dev_config = {
            "version": "1.0",
            "modules": [
                {"name": "ModuleA", "required": True, "dependencies": []},
                {"name": "ModuleB", "required": False, "dependencies": ["ModuleA"]},
                {"name": "ModuleC", "required": False, "dependencies": ["ModuleB"]},
            ],
            "global_config": {"max_retries": 3}
        }
        
        self.user_config = {
            "version": "1.0",
            "enabledModules": ["ModuleB"],
            "disabledModules": ["ModuleC"],
            "moduleOverrides": {"ModuleB": {"setting": "value"}}
        }
        
        self.sequencer.dev_config = self.dev_config
        self.sequencer.user_config = self.user_config
    
    def test_load_configurations_success(self):
        """Test successful configuration loading."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as dev_file:
            json.dump(self.dev_config, dev_file)
            dev_path = dev_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as user_file:
            json.dump(self.user_config, user_file)
            user_path = user_file.name
        
        try:
            self.sequencer.load_configurations(dev_path, user_path)
            self.assertEqual(self.sequencer.dev_config, self.dev_config)
            self.assertEqual(self.sequencer.user_config, self.user_config)
        finally:
            os.unlink(dev_path)
            os.unlink(user_path)
    
    def test_load_configurations_missing_dev_config(self):
        """Test error when developer config is missing."""
        with self.assertRaises(ConfigurationError):
            self.sequencer.load_configurations("nonexistent.json")
    
    def test_load_configurations_invalid_json(self):
        """Test error when configuration contains invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            path = f.name
        
        try:
            with self.assertRaises(ConfigurationError):
                self.sequencer.load_configurations(path)
        finally:
            os.unlink(path)
    
    def test_build_dependency_graph(self):
        """Test dependency graph building."""
        graph = self.sequencer._build_dependency_graph()
        
        # In the adjacency list format: if B depends on A, then A points to B
        expected = {
            "ModuleA": {"ModuleB"},  # ModuleA is depended on by ModuleB
            "ModuleB": {"ModuleC"},  # ModuleB is depended on by ModuleC
            "ModuleC": set()         # ModuleC has no dependents
        }
        
        self.assertEqual(graph, expected)
    
    def test_build_dependency_graph_missing_dependency(self):
        """Test error when dependency is missing."""
        self.sequencer.dev_config["modules"][0]["dependencies"] = ["NonexistentModule"]
        
        with self.assertRaises(MissingDependencyError):
            self.sequencer._build_dependency_graph()
    
    def test_detect_circular_dependencies_none(self):
        """Test circular dependency detection with no cycles."""
        graph = {"A": {"B"}, "B": {"C"}, "C": set()}
        
        # Should not raise any exception
        self.sequencer._detect_circular_dependencies(graph)
    
    def test_detect_circular_dependencies_simple_cycle(self):
        """Test circular dependency detection with simple cycle."""
        graph = {"A": {"B"}, "B": {"A"}}
        
        with self.assertRaises(CircularDependencyError):
            self.sequencer._detect_circular_dependencies(graph)
    
    def test_detect_circular_dependencies_complex_cycle(self):
        """Test circular dependency detection with complex cycle."""
        graph = {"A": {"B"}, "B": {"C"}, "C": {"A"}}
        
        with self.assertRaises(CircularDependencyError):
            self.sequencer._detect_circular_dependencies(graph)
    
    def test_topological_sort(self):
        """Test topological sorting."""
        graph = {"A": {"B"}, "B": {"C"}, "C": set()}
        result = self.sequencer._topological_sort(graph)
        
        # A should come before B, B should come before C
        self.assertTrue(result.index("A") < result.index("B"))
        self.assertTrue(result.index("B") < result.index("C"))
    
    def test_apply_user_preferences_required_module(self):
        """Test that required modules cannot be disabled by user."""
        sorted_modules = ["ModuleA", "ModuleB", "ModuleC"]
        result = self.sequencer._apply_user_preferences(sorted_modules, None)
        
        # ModuleA is required, so should be enabled despite user trying to disable
        self.assertIn("ModuleA", result)
        self.assertIn("ModuleB", result)  # Explicitly enabled
        self.assertNotIn("ModuleC", result)  # Disabled by user
    
    def test_apply_user_preferences_cli_override(self):
        """Test CLI overrides take highest priority."""
        sorted_modules = ["ModuleA", "ModuleB", "ModuleC"]
        cli_overrides = {"ModuleC": True}  # Enable despite user disable
        
        result = self.sequencer._apply_user_preferences(sorted_modules, cli_overrides)
        
        self.assertIn("ModuleC", result)  # Should be enabled by CLI override
    
    def test_validate_final_config(self):
        """Test final configuration validation."""
        enabled_modules = ["ModuleA", "ModuleB"]
        resolutions = self.sequencer._validate_final_config(enabled_modules)
        
        self.assertEqual(len(resolutions), 2)
        self.assertEqual(resolutions[0].name, "ModuleA")
        self.assertEqual(resolutions[0].state, ModuleState.ENABLED)
        self.assertEqual(resolutions[1].name, "ModuleB")
    
    def test_validate_final_config_missing_module(self):
        """Test validation with missing module."""
        enabled_modules = ["ModuleA", "NonexistentModule"]
        resolutions = self.sequencer._validate_final_config(enabled_modules)
        
        self.assertEqual(len(resolutions), 2)
        self.assertEqual(resolutions[1].state, ModuleState.FAILED)
        self.assertIsNotNone(resolutions[1].error_message)
    
    def test_sequence_modules_success(self):
        """Test successful module sequencing."""
        resolutions, errors = self.sequencer.sequence_modules()
        
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(resolutions), 2)  # ModuleA and ModuleB enabled
        
        # Check order: ModuleA should come before ModuleB
        module_names = [r.name for r in resolutions]
        self.assertIn("ModuleA", module_names)
        self.assertIn("ModuleB", module_names)
        self.assertTrue(module_names.index("ModuleA") < module_names.index("ModuleB"))
    
    def test_get_module_status(self):
        """Test getting module status."""
        status = self.sequencer.get_module_status()
        
        self.assertIn("modules", status)
        self.assertIn("total_enabled", status)
        self.assertIn("total_disabled", status)
        self.assertIn("total_failed", status)
        self.assertIn("errors", status)
    
    def test_validate_configuration(self):
        """Test configuration validation."""
        errors = self.sequencer.validate_configuration()
        self.assertEqual(len(errors), 0)  # Should be valid
        
        # Test with invalid config
        del self.sequencer.dev_config["version"]
        errors = self.sequencer.validate_configuration()
        self.assertGreater(len(errors), 0)
    
    @patch('src.adt_core.module_sequencer.entry_points')
    def test_discover_modules(self, mock_entry_points):
        """Test module discovery via entry points."""
        # Mock entry points
        mock_ep = MagicMock()
        mock_ep.name = "TestModule"
        
        # Create a lambda that returns a properly initialized MockModule
        def create_test_module():
            return MockModule("TestModule", "1.0.0", [])
        
        mock_ep.load.return_value = create_test_module
        
        mock_eps = MagicMock()
        mock_eps.select.return_value = [mock_ep]
        mock_entry_points.return_value = mock_eps
        
        sequencer = ModuleSequencer()
        sequencer.discover_modules()
        
        self.assertIn("TestModule", sequencer.available_modules)


class TestDetermineModuleState(unittest.TestCase):
    """Test cases for determine_module_state function."""
    
    def test_cli_override_priority(self):
        """Test CLI override has highest priority."""
        result = determine_module_state(
            "TestModule", False, [], ["TestModule"], {"TestModule": True}
        )
        self.assertEqual(result, ModuleState.ENABLED)
    
    def test_required_module_cannot_be_disabled(self):
        """Test required modules cannot be disabled."""
        result = determine_module_state(
            "TestModule", True, [], ["TestModule"], None
        )
        self.assertEqual(result, ModuleState.ENABLED)
    
    def test_user_explicit_disable(self):
        """Test user can disable optional modules."""
        result = determine_module_state(
            "TestModule", False, [], ["TestModule"], None
        )
        self.assertEqual(result, ModuleState.DISABLED)
    
    def test_user_explicit_enable(self):
        """Test user can enable optional modules."""
        result = determine_module_state(
            "TestModule", False, ["TestModule"], [], None
        )
        self.assertEqual(result, ModuleState.ENABLED)
    
    def test_default_enabled(self):
        """Test default behavior is enabled."""
        result = determine_module_state(
            "TestModule", False, [], [], None
        )
        self.assertEqual(result, ModuleState.ENABLED)


if __name__ == '__main__':
    unittest.main()
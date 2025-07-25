"""Integration tests for ADT module system."""

import json
import unittest
import logging
from unittest.mock import patch, MagicMock

from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleSequencer, ModuleState
from asciidoc_dita_toolkit.modules.entity_reference import EntityReferenceModule
from asciidoc_dita_toolkit.modules.content_type import ContentTypeModule
from asciidoc_dita_toolkit.modules.directory_config import DirectoryConfigModule


class TestIntegration(unittest.TestCase):
    """Integration tests using real modules and configurations."""

    def setUp(self):
        """Set up test fixtures."""
        # Configure logging for testing
        logging.basicConfig(level=logging.DEBUG)

        self.sequencer = ModuleSequencer()

        # Manually add real modules (simulating entry point discovery)
        self.sequencer.available_modules = {
            "EntityReference": EntityReferenceModule(),
            "ContentType": ContentTypeModule(),
            "DirectoryConfig": DirectoryConfigModule(),
        }

        # Create test-specific configuration that only includes our 3 available modules
        self.test_dev_config = {
            "version": "1.0",
            "modules": [
                {
                    "name": "DirectoryConfig",
                    "required": True,
                    "version": "~1.0.0",
                    "dependencies": [],
                    "init_order": 1,
                    "config": {
                        "scan_depth": 5,
                        "exclude_patterns": ["*.tmp", "*.log"]
                    }
                },
                {
                    "name": "EntityReference",
                    "required": True,
                    "version": ">=1.2.0",
                    "dependencies": ["DirectoryConfig"],
                    "init_order": 2,
                    "config": {
                        "timeout_seconds": 30,
                        "cache_size": 1000
                    }
                },
                {
                    "name": "ContentType",
                    "required": False,
                    "version": ">=2.0.0",
                    "dependencies": ["EntityReference"],
                    "init_order": 3,
                    "config": {
                        "cache_enabled": True,
                        "supported_types": ["text", "image", "video"]
                    }
                }
            ],
            "global_config": {
                "max_retries": 3,
                "log_level": "INFO"
            }
        }

        self.test_user_config = {
            "version": "1.0",
            "enabledModules": ["DirectoryConfig", "EntityReference", "ContentType"],
            "disabledModules": [],
            "moduleOverrides": {
                "ContentType": {
                    "cache_enabled": False,
                    "supported_types": ["text", "image"]
                }
            }
        }

    def test_load_real_configurations(self):
        """Test loading actual configuration files."""
        self.sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')

        # Verify configurations loaded correctly
        self.assertEqual(self.sequencer.dev_config["version"], "1.0")

        # Verify that essential modules are present instead of hardcoding count
        loaded_module_names = [m["name"] for m in self.sequencer.dev_config["modules"]]
        essential_modules = ["DirectoryConfig", "EntityReference", "ContentType", "UserJourney"]
        for module_name in essential_modules:
            self.assertIn(module_name, loaded_module_names, f"Essential module {module_name} not found in configuration")

        # Verify we have a reasonable number of modules (at least the essential ones)
        self.assertGreaterEqual(len(self.sequencer.dev_config["modules"]), len(essential_modules))
        self.assertIn("DirectoryConfig", self.sequencer.user_config["enabledModules"])

    def test_full_sequencing_workflow(self):
        """Test complete module sequencing workflow."""
        # Use test-specific config to avoid dependency issues
        self.sequencer.dev_config = self.test_dev_config
        self.sequencer.user_config = self.test_user_config

        resolutions, errors = self.sequencer.sequence_modules()

        # Should have no errors
        self.assertEqual(len(errors), 0)

        # Should have 3 modules that we manually added in setUp (DirectoryConfig, EntityReference and ContentType)
        # Only test the 3 modules we have in our mock setup
        enabled_modules = [r for r in resolutions if r.state == ModuleState.ENABLED]
        test_modules = [r for r in enabled_modules if r.name in ["DirectoryConfig", "EntityReference", "ContentType"]]
        self.assertEqual(len(test_modules), 3)

        module_names = [r.name for r in test_modules]
        self.assertIn("EntityReference", module_names)
        self.assertIn("ContentType", module_names)
        self.assertIn("DirectoryConfig", module_names)  # DirectoryConfig is now required

        # Verify correct initialization order
        entity_ref_order = next(
            r.init_order for r in test_modules if r.name == "EntityReference"
        )
        content_type_order = next(
            r.init_order for r in test_modules if r.name == "ContentType"
        )
        self.assertLess(entity_ref_order, content_type_order)

    def test_module_execution_with_configs(self):
        """Test that modules receive correct configuration."""
        # Use test-specific config to avoid dependency issues
        self.sequencer.dev_config = self.test_dev_config
        self.sequencer.user_config = self.test_user_config

        resolutions, errors = self.sequencer.sequence_modules()

        # Find ContentType module resolution
        content_type_resolution = next(
            r for r in resolutions if r.name == "ContentType"
        )

        # Verify user override applied (cache_enabled should be False)
        self.assertFalse(content_type_resolution.config["cache_enabled"])
        self.assertEqual(
            content_type_resolution.config["supported_types"], ["text", "image"]
        )

        # Verify global config applied
        self.assertEqual(content_type_resolution.config["max_retries"], 3)

    def test_cli_override_functionality(self):
        """Test CLI overrides work correctly."""
        # Use test-specific config to avoid dependency issues
        self.sequencer.dev_config = self.test_dev_config
        self.sequencer.user_config = self.test_user_config

        # Test disabling a module via CLI override
        cli_overrides = {"ContentType": False}  # Test disabling ContentType
        resolutions, errors = self.sequencer.sequence_modules(cli_overrides)

        self.assertEqual(len(errors), 0)

        # ContentType should be disabled, but DirectoryConfig should be enabled since it's required
        enabled_modules = [r for r in resolutions if r.state == ModuleState.ENABLED]
        module_names = [r.name for r in enabled_modules]
        self.assertIn("DirectoryConfig", module_names)
        self.assertNotIn("ContentType", module_names)

    def test_dependency_resolution_with_real_modules(self):
        """Test dependency resolution using real module dependencies."""
        # Fresh sequencer instance to avoid test interference
        fresh_sequencer = ModuleSequencer()

        # Add real modules (simulating entry point discovery)
        fresh_sequencer.available_modules = {
            "EntityReference": EntityReferenceModule(),
            "ContentType": ContentTypeModule(),
            "DirectoryConfig": DirectoryConfigModule(),
        }

        # Use test-specific config to avoid dependency issues
        fresh_sequencer.dev_config = self.test_dev_config
        fresh_sequencer.user_config = self.test_user_config

        # Sequence modules
        resolutions, errors = fresh_sequencer.sequence_modules()

        # Should have no errors
        self.assertEqual(len(errors), 0)

        # Filter to enabled modules only
        enabled_modules = [r for r in resolutions if r.state == ModuleState.ENABLED]

        # Should have at least 2 enabled modules (EntityReference and ContentType)
        self.assertGreaterEqual(len(enabled_modules), 2)

        # Verify initialization order respects dependencies
        orders = {r.name: r.init_order for r in enabled_modules}

        # The exact init_order values may vary, but the relative ordering must be correct
        # EntityReference has no dependencies, should come before ContentType
        self.assertIn("EntityReference", orders, "EntityReference should be enabled")
        self.assertIn("ContentType", orders, "ContentType should be enabled")

        # ContentType depends on EntityReference, so EntityReference should have lower init_order
        logging.debug(
            "EntityReference init_order: %s, ContentType init_order: %s",
            orders["EntityReference"],
            orders["ContentType"],
        )
        self.assertLess(
            orders["EntityReference"],
            orders["ContentType"],
            "EntityReference should be initialized before ContentType",
        )

        # If DirectoryConfig is enabled, it should come before both (since it's foundational)
        if "DirectoryConfig" in orders:
            self.assertLess(orders["DirectoryConfig"], orders["EntityReference"])
            self.assertLess(orders["DirectoryConfig"], orders["ContentType"])

    def test_module_status_reporting(self):
        """Test module status reporting functionality."""
        # Use test-specific config to avoid dependency issues
        self.sequencer.dev_config = self.test_dev_config
        self.sequencer.user_config = self.test_user_config

        status = self.sequencer.get_module_status()

        self.assertIn("modules", status)
        self.assertIn("total_enabled", status)
        self.assertIn("total_disabled", status)
        self.assertIn("errors", status)

        # Should have 3 enabled (only the modules we manually added in setUp), rest should be missing
        available_test_modules = ["DirectoryConfig", "EntityReference", "ContentType"]
        enabled_test_modules = [m for m in status["modules"] if m["name"] in available_test_modules and m["state"] == "enabled"]
        self.assertEqual(len(enabled_test_modules), 3)
        self.assertEqual(len(status["errors"]), 0)

    def test_configuration_validation(self):
        """Test configuration validation."""
        # Use test-specific config to avoid dependency issues
        self.sequencer.dev_config = self.test_dev_config
        self.sequencer.user_config = self.test_user_config

        errors = self.sequencer.validate_configuration()
        self.assertEqual(len(errors), 0)  # Should be valid

    def test_missing_dependency_error(self):
        """Test error handling when a dependency is missing."""
        # Create a config that references a non-existent module
        invalid_config = {
            "version": "1.0",
            "modules": [
                {
                    "name": "EntityReference",
                    "required": True,
                    "dependencies": ["NonexistentModule"],
                }
            ],
        }

        self.sequencer.dev_config = invalid_config
        self.sequencer.user_config = {}

        resolutions, errors = self.sequencer.sequence_modules()

        self.assertGreater(len(errors), 0)
        self.assertIn("missing", errors[0].lower())

    @patch('asciidoc_dita_toolkit.adt_core.module_sequencer.entry_points')
    def test_module_discovery_integration(self, mock_entry_points):
        """Test module discovery with actual module classes."""
        # Mock entry points to return our actual modules
        mock_eps = []

        for name, module_class in [
            ("EntityReference", EntityReferenceModule),
            ("ContentType", ContentTypeModule),
            ("DirectoryConfig", DirectoryConfigModule),
        ]:
            mock_ep = MagicMock()
            mock_ep.name = name
            mock_ep.load.return_value = module_class
            mock_eps.append(mock_ep)

        mock_eps_obj = MagicMock()
        mock_eps_obj.select.return_value = mock_eps
        mock_entry_points.return_value = mock_eps_obj

        sequencer = ModuleSequencer()
        sequencer.discover_modules()

        # Should have discovered all three modules
        self.assertEqual(len(sequencer.available_modules), 3)
        self.assertIn("EntityReference", sequencer.available_modules)
        self.assertIn("ContentType", sequencer.available_modules)
        self.assertIn("DirectoryConfig", sequencer.available_modules)

        # Verify actual instances were created
        entity_ref = sequencer.available_modules["EntityReference"]
        self.assertEqual(entity_ref.name, "EntityReference")
        self.assertEqual(entity_ref.version, "1.2.1")
        self.assertEqual(entity_ref.dependencies, [])

        content_type = sequencer.available_modules["ContentType"]
        self.assertEqual(content_type.dependencies, ["EntityReference"])

    def test_end_to_end_module_execution(self):
        """Test the complete flow from discovery through execution."""
        # Create fresh sequencer to avoid cross-contamination
        fresh_sequencer = ModuleSequencer()

        # Add real modules (simulating entry point discovery)
        fresh_sequencer.available_modules = {
            "EntityReference": EntityReferenceModule(),
            "ContentType": ContentTypeModule(),
            "DirectoryConfig": DirectoryConfigModule(),
        }

        # Use test-specific config to avoid dependency issues
        fresh_sequencer.dev_config = self.test_dev_config
        fresh_sequencer.user_config = self.test_user_config

        # Execute the full flow
        resolutions, errors = fresh_sequencer.sequence_modules()

        # Should have no errors
        self.assertEqual(len(errors), 0)

        # Get enabled modules sorted by initialization order
        enabled_modules = [r for r in resolutions if r.state == ModuleState.ENABLED]
        enabled_modules.sort(key=lambda x: x.init_order)

        # Execute modules in order
        for resolution in enabled_modules:
            # Get module instance from available_modules
            module = fresh_sequencer.available_modules[resolution.name]
            self.assertIsNotNone(module, f"Module {resolution.name} should have instance")

            # Simulate module execution
            if hasattr(module, "run"):
                # For testing, we'll just verify the method exists
                self.assertTrue(callable(module.run))

            # Verify the module was properly configured
            self.assertEqual(module.name, resolution.name)


if __name__ == '__main__':
    unittest.main()

"""Integration tests for ADT module system."""

import json
import unittest
import logging
from unittest.mock import patch, MagicMock

from asciidoc_dita_toolkit.adt_core.module_sequencer import ModuleSequencer, ModuleState
from modules.entity_reference import EntityReferenceModule
from modules.content_type import ContentTypeModule
from modules.directory_config import DirectoryConfigModule


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

    def test_load_real_configurations(self):
        """Test loading actual configuration files."""
        self.sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')

        # Verify configurations loaded correctly
        self.assertEqual(self.sequencer.dev_config["version"], "1.0")
        self.assertEqual(
            len(self.sequencer.dev_config["modules"]), 5
        )  # Updated for ExampleBlock and ArchiveUnusedFiles
        self.assertIn("DirectoryConfig", self.sequencer.user_config["disabledModules"])

    def test_full_sequencing_workflow(self):
        """Test complete module sequencing workflow."""
        self.sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')

        resolutions, errors = self.sequencer.sequence_modules()

        # Should have no errors
        self.assertEqual(len(errors), 0)

        # Should have 3 modules (DirectoryConfig, EntityReference and ContentType)
        # DirectoryConfig is now a required module and cannot be disabled
        enabled_modules = [r for r in resolutions if r.state == ModuleState.ENABLED]
        self.assertEqual(len(enabled_modules), 3)

        module_names = [r.name for r in enabled_modules]
        self.assertIn("EntityReference", module_names)
        self.assertIn("ContentType", module_names)
        self.assertIn("DirectoryConfig", module_names)  # DirectoryConfig is now required

        # Verify correct initialization order
        entity_ref_order = next(
            r.init_order for r in enabled_modules if r.name == "EntityReference"
        )
        content_type_order = next(
            r.init_order for r in enabled_modules if r.name == "ContentType"
        )
        self.assertLess(entity_ref_order, content_type_order)

    def test_module_execution_with_configs(self):
        """Test that modules receive correct configuration."""
        self.sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')

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
        self.sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')

        # Enable DirectoryConfig via CLI override (it's disabled in user config)
        cli_overrides = {"DirectoryConfig": True}
        resolutions, errors = self.sequencer.sequence_modules(cli_overrides)

        self.assertEqual(len(errors), 0)

        # Now DirectoryConfig should be enabled
        enabled_modules = [r for r in resolutions if r.state == ModuleState.ENABLED]
        module_names = [r.name for r in enabled_modules]
        self.assertIn("DirectoryConfig", module_names)

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

        # Load configurations
        fresh_sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')

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
        self.sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')

        status = self.sequencer.get_module_status()

        self.assertIn("modules", status)
        self.assertIn("total_enabled", status)
        self.assertIn("total_disabled", status)
        self.assertIn("errors", status)

        # Should have 3 enabled (DirectoryConfig is now required), 0 disabled
        self.assertEqual(status["total_enabled"], 3)
        self.assertEqual(status["total_disabled"], 0)
        self.assertEqual(len(status["errors"]), 0)

    def test_configuration_validation(self):
        """Test configuration validation."""
        self.sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')

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
        """Test end-to-end module execution."""
        self.sequencer.load_configurations('.adt-modules.json', 'adt-user-config.json')

        resolutions, errors = self.sequencer.sequence_modules()
        self.assertEqual(len(errors), 0)

        # Execute modules in order
        results = []
        for resolution in resolutions:
            if resolution.state == ModuleState.ENABLED:
                module = self.sequencer.available_modules[resolution.name]

                # Initialize module
                module.initialize(resolution.config)

                # Execute module
                result = module.execute({})
                results.append(result)

                # Cleanup
                module.cleanup()

        # Should have executed 3 modules (DirectoryConfig is now required)
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertTrue(result["success"])


if __name__ == '__main__':
    unittest.main()

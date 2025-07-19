# ADT Plugin Creation Template for Claude Sonnet 4

This template is optimized for creating ADT plugins using GitHub Copilot with Claude Sonnet 4. Feed these instructions in the specified chunks to maintain context and ensure successful implementation.

---

## CHUNK 1: Initial Setup and Architecture

### Plugin Overview
Create a new ADT plugin named `[PLUGIN_NAME]` that follows the established asciidoc-dita-toolkit patterns.

### Required Files Structure
```
modules/[plugin_name_snake_case].py                    # ADTModule wrapper
asciidoc_dita_toolkit/asciidoc_dita/plugins/[PluginNameCamelCase].py  # Core logic
tests/fixtures/[PluginNameCamelCase]/                   # Test fixtures
├── ignore_*.adoc                                       # Cases to ignore
├── ignore_*.expected                                   # Expected output (no changes)
├── report_*.adoc                                       # Cases to fix
└── report_*.expected                                   # Expected output (with fixes)
```

### Architecture Pattern
Follow the ContentType plugin pattern:
1. **ADTModule wrapper** in `modules/` - provides clean interface
2. **Core plugin** in `asciidoc_dita_toolkit/asciidoc_dita/plugins/` - implements logic
3. **Detector/Processor separation** - enables testability
4. **Test fixtures** - drive development

### Key Implementation Classes
```python
# Detector class - finds violations
class [PluginName]Detector:
    def find_[violation_type](self, content: str) -> List[ViolationBlock]
    def is_in_main_body(self, block: ViolationBlock, content: str) -> bool
    def is_in_list(self, block: ViolationBlock, content: str) -> bool
    def is_in_block(self, block: ViolationBlock, content: str) -> bool

# Processor class - fixes violations
class [PluginName]Processor:
    def __init__(self, detector: [PluginName]Detector, interactive: bool = True)
    def process_content(self, content: str) -> Tuple[str, List[Issue]]
```

---

## CHUNK 2: Detection Logic Implementation

### Critical Detection Patterns
When implementing detection logic, avoid these common pitfalls:

1. **Delimiter Pairing**: Process opening and closing delimiters (`====`, `----`, etc.) as pairs, not individual lines
2. **Context Propagation**: Look backward through empty lines and continuation markers (`+`) to find context
3. **Nested Structures**: Track delimiter nesting to determine if inside code blocks or other structures
4. **Comment Handling**: Properly detect single-line (`//`) and multi-line (`////`) comments

### Essential Detection Methods
```python
def _is_in_code_block_or_comment(self, lines: List[str], line_num: int) -> bool:
    # Check both code blocks AND comments - don't forget either!
    
def _is_in_admonition_context(self, lines: List[str], line_num: int) -> bool:
    # Look backward through empty lines and '+' markers
    # Check for [NOTE], [TIP], [IMPORTANT], [WARNING], [CAUTION]
    
def _find_section_level(self, lines: List[str], line_num: int) -> int:
    # Return 0 for main body, 1+ for section levels
```

### Detection Logic Checklist
- [ ] Handle delimiter pairs correctly (don't count opening/closing separately)
- [ ] Check all contexts: code blocks, comments, admonitions
- [ ] Use consistent logic for both delimited and style blocks
- [ ] Track section levels and document structure
- [ ] Properly handle empty lines and continuation markers

---

## CHUNK 3: Violation Processing and User Interaction

### Violation Detection Logic
**CRITICAL**: Detection and processing must be aligned. Use ALL detection methods:

```python
# In process_content method:
if not self.detector.is_in_main_body(block, content) or \
   self.detector.is_in_list(block, content) or \
   self.detector.is_in_block(block, content):
    # This is a violation - process it
```

### User Interaction Pattern
Model after ContentType plugin:
```python
options = {
    '1-9': 'Specific placement choices (context-dependent)',
    'M': 'Move to main body',
    'L': 'Leave as-is and insert comment',
    'S': 'Skip this block',
    'Q': 'Skip plugin'
}
```

### Comment Template
When automatic fixes aren't possible:
```adoc
//
// ADT [PluginName]: [Specific guidance for DITA compliance]
// [Additional context or instructions]
//
```

### Processing Strategy
1. **Automatic mode** (`interactive=False`): Add comments at violations
2. **Interactive mode** (`interactive=True`): Present user choices
3. **Main body marker**: Add comment showing correct placement location

---

## CHUNK 4: Test-Driven Development

### Testing Architecture
Use dual testing approach for comprehensive coverage:

1. **Deterministic Testing** (for CI/CD):
   - Use `interactive=False`
   - Expected files show comment-adding behavior
   - Ensures consistent automated testing

2. **Interactive Testing** (optional):
   - Use `interactive=True` with mocked input
   - Test specific user scenarios
   - Validate block movement logic

### Test Implementation Pattern
```python
def test_[scenario_name](self):
    # Load fixture
    input_path = self.fixtures_dir / '[scenario].adoc'
    expected_path = self.fixtures_dir / '[scenario].expected'
    
    # Process with non-interactive mode for deterministic results
    processor = [PluginName]Processor(detector, interactive=False)
    result, issues = processor.process_content(content)
    
    # Compare with expected
    assert result == expected_content
```

### Test Fixture Categories
- `ignore_*.adoc`: Cases where plugin should detect 0 violations
- `report_*.adoc`: Cases with violations to fix
- Update `.expected` files to show actual fixes (not identical to source!)

---

## CHUNK 5: Integration and Debugging

### ADT System Integration
1. **Update `pyproject.toml`**:
   ```toml
   [project.entry-points."adt.modules"]
   [plugin_name] = "modules.[plugin_name_snake_case]:[PluginName]Module"
   ```

2. **Module Configuration** in `.adt-modules.json`:
   ```json
   {
     "name": "[PluginName]",
     "required": false,
     "init_order": [appropriate_number],
     "dependencies": [],
     "config": {
       "interactive": true,
       "verbose": false
     }
   }
   ```

### Debug Utilities
Create `debug_[plugin_name].py` for development:
```python
def debug_detection(fixture_name):
    detector = [PluginName]Detector()
    blocks = detector.find_violations(content)
    print(f"Found {len(blocks)} violations")
    for block in blocks:
        print(f"  Line {block.line_num}: {block.type}")
```

### Common Implementation Issues
1. **False Positives**: Check delimiter pairing and context detection
2. **Missing Violations**: Ensure all detection methods are used in processing
3. **Test Failures**: Verify expected files show actual fixes
4. **Integration Issues**: Check entry points and module configuration

---

## CHUNK 6: Implementation Checklist

### Development Process
1. [ ] Create module wrapper following `modules/content_type.py` pattern
2. [ ] Implement detector class with all required methods
3. [ ] Implement processor class with interactive/non-interactive modes
4. [ ] Create test fixtures for all scenarios
5. [ ] Update expected files with actual transformations
6. [ ] Add debug utilities for development
7. [ ] Integrate with ADT system via entry points
8. [ ] Test CLI integration with `adt` command

### Quality Checklist
- [ ] All `ignore_*` tests detect 0 violations
- [ ] All `report_*` tests detect correct number of violations
- [ ] Non-interactive mode produces deterministic results
- [ ] Comments provide clear compliance guidance
- [ ] Plugin integrates seamlessly with ADT CLI
- [ ] Comprehensive test coverage for edge cases

### Key Success Factors
1. **Delimiter Handling**: Process pairs, not individual lines
2. **Context Awareness**: Check all contexts (code, comments, admonitions)
3. **Consistent Logic**: Apply same checks to all block types
4. **Aligned Detection/Processing**: Use all detection methods in processor
5. **Deterministic Testing**: Use non-interactive mode for CI/CD

---

## Usage Instructions

1. Replace all `[PLUGIN_NAME]`, `[plugin_name]`, `[PluginName]` placeholders
2. Feed chunks sequentially to maintain context
3. Start with CHUNK 1-2 for initial implementation
4. Use CHUNK 3-4 for processing and testing
5. Apply CHUNK 5-6 for integration and quality assurance
6. Refer back to specific chunks when debugging issues

This template captures the critical lessons learned from ExampleBlock implementation to streamline creation of the
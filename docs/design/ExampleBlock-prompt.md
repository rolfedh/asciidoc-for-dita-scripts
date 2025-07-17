# Create ExampleBlock Plugin for asciidoc-dita-toolkit

## Problem Statement
DITA 1.3 requires `<example>` elements to appear only in the main body of topics. AsciiDoc example blocks (delimited by `====` or marked with `[example]`) violate this when placed within sections, other blocks, or lists.

## Plugin Requirements

### Architecture
- **Language**: Python
- **Integration**: Follow the pattern used by `modules/content_type.py` and `asciidoc_dita_toolkit/asciidoc_dita/plugins/ContentType.py`
- **Module structure**: Create both a module wrapper and core plugin implementation

### Detection Patterns
Detect and flag these invalid example block patterns:
- `====` delimited blocks within sections, other blocks, or lists
- `[example]` blocks within sections, other blocks, or lists
- **Main body definition**: Content before the first section header (`== Section`)

### Processing Logic
1. **Automatic fixes**: Move example blocks to main body when possible
2. **User interaction**: Present options when automatic fixes aren't optimal
3. **Fallback**: Insert explanatory comments when no clear solution exists

### User Interface
Model after ContentType plugin's CLI pattern with options:
- **1-9**: Specific placement choices (context-dependent)
- **M**: Move to main body 
- **L**: Leave as-is and insert comment
- **S**: Skip this block
- **Q**: Skip plugin

### Test-Driven Development
Use existing fixtures in `tests/fixtures/ExampleBlock/`:
- `ignore_*.adoc` → `ignore_*.expected` (no changes)
- `report_*.adoc` → `report_*.expected` (show fixes)

**CRITICAL**: The current `report_*.expected` files are identical to their `report_*.adoc` counterparts and need to be updated to show the actual fixes. The plugin should first analyze the fixtures to understand the expected transformations.

### Comment Template
When automatic fixes aren't possible:
```adoc
//
// ADT ExampleBlock: Move this example block to the main body of the topic 
// (before the first section header) for DITA 1.3 compliance.
//
```

### Automatic Fix Strategy
1. **First priority**: Move example blocks to end of main body (before first section header)
2. **If context allows**: Place example blocks near related content in main body
3. **If impossible**: Insert comment explaining the issue

## Implementation Tasks
1. Analyze existing ContentType plugin structure
5. Implement AsciiDoc parsing to detect example blocks and document structure


## Implementation Requirements

### Phase 1: Foundation Analysis
1. **Examine ContentType Plugin**: Analyze the existing `ContentType.py` plugin structure, CLI interaction patterns, and integration approach
2. **Define Automatic Fix Strategy**: Create a clear strategy for where to place moved example blocks in the main body
3. **Update Test Fixtures**: Modify the `.expected` files to show the actual fixes that should be applied

### Phase 2: Core Implementation  
4. **Create Module Structure**: Implement both the ADTModule wrapper and core plugin following the established patterns such as:
  * Create `modules/example_block.py` (ADTModule wrapper)
  * Create `asciidoc_dita_toolkit/asciidoc_dita/plugins/ExampleBlock.py` (core logic)
5. **Implement Detection Logic**: Build AsciiDoc parsing to identify example blocks and document structure
6. **Add User Interaction**: Create CLI prompts for cases requiring user decisions
7. **Ensure Test Coverage**: Validate all fixtures pass and edge cases are handled

### Success Criteria
- All `report_*.expected` files show proper fixes (not identical to source)
- Plugin integrates seamlessly with existing ADT architecture
- User interaction follows established CLI patterns
- Comprehensive test coverage with all fixtures passing

## Appendix: Implementation Insights

### A. Detection Logic Refinements
Based on initial implementation, the detection logic requires sophisticated pattern matching:

**False Positive Patterns to Avoid:**
- `====` blocks preceded by `[NOTE]`, `[TIP]`, `[IMPORTANT]`, `[WARNING]`, `[CAUTION]` (admonitions)
- `====` blocks inside `----`, `....`, ```````` delimited code blocks
- `[example]` inside comment blocks (`//` or `////`)
- `====` blocks with empty lines and continuation markers (`+`) between admonition markers

**Critical Detection Challenges:**
1. **Admonition Context**: Must look backwards through empty lines and continuation markers to find admonition markers
2. **Code Block Nesting**: Track delimiter pairs to determine if inside code blocks
3. **List Continuation**: Distinguish between list-embedded blocks and main body blocks

### B. Test-Driven Development Process
The fixture-based approach revealed important implementation details:

**Current Test Status (as of implementation):**
- ✅ `ignore_comments`: Correctly ignores example blocks in comments
- ✅ `ignore_valid_examples`: Correctly ignores valid main body examples  
- ❌ `ignore_admonitions`: Falsely detects 9 blocks (should be 0)
- ❌ `ignore_code_blocks`: Falsely detects blocks in code samples
- ❌ `report_*`: Output format needs alignment with expected files

**Iterative Process Required:**
1. Debug detection logic with specific fixture content
2. Refine filtering algorithms based on AsciiDoc spec
3. Collaborate on expected file content definition
4. Validate automatic fix placement strategy

### C. Architecture Lessons
The plugin structure should follow these patterns discovered during implementation:

**Module Integration:**
- ADTModule wrapper in `modules/example_block.py` provides clean interface
- Core logic in `asciidoc_dita_toolkit/asciidoc_dita/plugins/ExampleBlock.py`
- Processor/detector separation enables testability

**Processing Strategy:**
- Line-based parsing more reliable than regex for complex AsciiDoc structures
- Context tracking essential for nested block detection
- Batch vs. interactive modes require different user interaction patterns

### D. Recommended Implementation Approach

**Phase 1: Perfect Detection Logic**
```python
# Test each ignore file individually
detector = ExampleBlockDetector()
blocks = detector.find_example_blocks(content)
# Should return 0 blocks for all ignore_*.adoc files
```

**Phase 2: Validate Automatic Fixes**
```python
# Test moving blocks to main body
processor = ExampleBlockProcessor(detector, interactive=True)
modified_content, issues = processor.process_content(content)
# Compare with expected output
```

**Phase 3: Collaborative Expected File Definition**
- Run plugin on `report_*.adoc` files
- Review actual output vs. intended behavior
- Update `.expected` files to match desired fixes
- Iterate until all tests pass

### E. Key Implementation Files Created
- `modules/example_block.py` - ADTModule wrapper
- `asciidoc_dita_toolkit/asciidoc_dita/plugins/ExampleBlock.py` - Core plugin
- `test_example_block.py` - Test harness
- `debug_detection.py` - Debug utilities

This appendix should guide future development iterations and help identify remaining implementation gaps.

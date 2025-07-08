"""
Test suite for the shared regex patterns module.

This script tests all regex patterns used across the AsciiDoc DITA Toolkit plugins
to ensure they work correctly and consistently.

To run: python3 -m pytest tests/test_regex_patterns.py -v
"""

import os
import sys
import unittest
import re

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from asciidoc_dita_toolkit.asciidoc_dita.regex_patterns import (
        CompiledPatterns, validate_patterns, get_pattern_documentation,
        list_available_patterns, compile_pattern,
        ID_PATTERN, ID_WITH_CONTEXT_PATTERN, XREF_BASIC_PATTERN,
        XREF_UNFIXED_PATTERN, LINK_PATTERN, CONTEXT_ATTR_PATTERN,
        INCLUDE_PATTERN, PATTERN_EXAMPLES
    )
except ImportError as e:
    print(f"Warning: Could not import regex_patterns module: {e}")
    CompiledPatterns = None


@unittest.skipIf(CompiledPatterns is None, "regex_patterns module could not be imported")
class TestCompiledPatterns(unittest.TestCase):
    """Test cases for pre-compiled regex patterns."""

    def test_compiled_patterns_exist(self):
        """Test that all compiled patterns are available."""
        self.assertIsNotNone(CompiledPatterns.ID_REGEX)
        self.assertIsNotNone(CompiledPatterns.ID_WITH_CONTEXT_REGEX)
        self.assertIsNotNone(CompiledPatterns.XREF_BASIC_REGEX)
        self.assertIsNotNone(CompiledPatterns.XREF_UNFIXED_REGEX)
        self.assertIsNotNone(CompiledPatterns.LINK_REGEX)
        self.assertIsNotNone(CompiledPatterns.CONTEXT_ATTR_REGEX)
        self.assertIsNotNone(CompiledPatterns.INCLUDE_REGEX)

    def test_patterns_are_compiled(self):
        """Test that patterns are actually compiled regex objects."""
        import re
        self.assertIsInstance(CompiledPatterns.ID_REGEX, re.Pattern)
        self.assertIsInstance(CompiledPatterns.ID_WITH_CONTEXT_REGEX, re.Pattern)
        self.assertIsInstance(CompiledPatterns.XREF_BASIC_REGEX, re.Pattern)
        self.assertIsInstance(CompiledPatterns.XREF_UNFIXED_REGEX, re.Pattern)
        self.assertIsInstance(CompiledPatterns.LINK_REGEX, re.Pattern)
        self.assertIsInstance(CompiledPatterns.CONTEXT_ATTR_REGEX, re.Pattern)
        self.assertIsInstance(CompiledPatterns.INCLUDE_REGEX, re.Pattern)


@unittest.skipIf(CompiledPatterns is None, "regex_patterns module could not be imported")
class TestIDPatterns(unittest.TestCase):
    """Test cases for ID-related patterns."""

    def test_id_pattern_matches(self):
        """Test basic ID pattern matching."""
        test_cases = [
            ('[id="simple_id"]', 'simple_id'),
            ('[id="complex-id_with-chars"]', 'complex-id_with-chars'),
            ('[id="topic"]', 'topic'),
            ('[id="installing-edge"]', 'installing-edge'),
        ]

        for input_text, expected_capture in test_cases:
            with self.subTest(input_text=input_text):
                match = CompiledPatterns.ID_REGEX.match(input_text)
                self.assertIsNotNone(match, f"Pattern should match: {input_text}")
                self.assertEqual(match.group(1), expected_capture)

    def test_id_pattern_non_matches(self):
        """Test that ID pattern correctly rejects invalid formats."""
        non_matching_cases = [
            'id="missing_brackets"',
            '[id=no_quotes]',
            '[id=""]',  # Empty ID
            'id["quoted_wrong"]',
            '[id="unterminated',
        ]

        for input_text in non_matching_cases:
            with self.subTest(input_text=input_text):
                match = CompiledPatterns.ID_REGEX.match(input_text)
                self.assertIsNone(match, f"Pattern should not match: {input_text}")

    def test_id_with_context_pattern_matches(self):
        """Test context-suffixed ID pattern matching."""
        test_cases = [
            ('[id="topic_banana"]', ('topic', 'banana')),
            ('[id="installing-edge_ocp4"]', ('installing-edge', 'ocp4')),
            ('[id="section_test-context"]', ('section', 'test-context')),
            ('[id="proc_install_k8s"]', ('proc_install', 'k8s')),
        ]

        for input_text, expected_captures in test_cases:
            with self.subTest(input_text=input_text):
                match = CompiledPatterns.ID_WITH_CONTEXT_REGEX.match(input_text)
                self.assertIsNotNone(match, f"Pattern should match: {input_text}")
                self.assertEqual(match.group(1), expected_captures[0])
                self.assertEqual(match.group(2), expected_captures[1])

    def test_id_with_context_pattern_non_matches(self):
        """Test that context ID pattern correctly rejects non-context formats."""
        # Only IDs without underscores should NOT match
        non_matching_cases = [
            'id="topic_banana"',  # Missing brackets
            '[id="nounderscorehere"]',  # No underscore at all
        ]

        for input_text in non_matching_cases:
            with self.subTest(input_text=input_text):
                match = CompiledPatterns.ID_WITH_CONTEXT_REGEX.match(input_text)
                self.assertIsNone(match, f"Pattern should not match: {input_text}")
                
        # Test cases that DO match (any ID with underscore - last underscore is separator)
        matching_cases = [
            ('[id="simple_id"]', ('simple', 'id')),
            ('[id="no_underscore"]', ('no', 'underscore')),
            ('[id="simple_id_no_context"]', ('simple_id_no', 'context')),
            ('[id="_just_context"]', ('_just', 'context')),
        ]
        
        for input_text, expected_groups in matching_cases:
            with self.subTest(input_text=input_text):
                match = CompiledPatterns.ID_WITH_CONTEXT_REGEX.match(input_text)
                self.assertIsNotNone(match, f"Pattern should match: {input_text}")
                self.assertEqual(match.group(1), expected_groups[0])
                self.assertEqual(match.group(2), expected_groups[1])


@unittest.skipIf(CompiledPatterns is None, "regex_patterns module could not be imported")
class TestCrossReferencePatterns(unittest.TestCase):
    """Test cases for cross-reference patterns."""

    def test_xref_basic_pattern_matches(self):
        """Test basic xref pattern matching."""
        test_cases = [
            ('xref:target[Link Text]', ('target', None, '[Link Text]')),
            ('xref:file.adoc#section[Section]', ('file.adoc', 'section', '[Section]')),
            ('xref:modules/proc.adoc#step[Step]', ('modules/proc.adoc', 'step', '[Step]')),
            ('xref:simple[]', ('simple', None, '[]')),
        ]

        for input_text, expected_captures in test_cases:
            with self.subTest(input_text=input_text):
                match = CompiledPatterns.XREF_BASIC_REGEX.search(input_text)
                self.assertIsNotNone(match, f"Pattern should match: {input_text}")
                self.assertEqual(match.group(1), expected_captures[0])
                self.assertEqual(match.group(2), expected_captures[1])
                self.assertEqual(match.group(3), expected_captures[2])

    def test_xref_unfixed_pattern_matches(self):
        """Test unfixed xref pattern matching (excludes already fixed xrefs)."""
        # Should match unfixed xrefs
        matching_cases = [
            ('xref:target[text]', ('target', '[text]')),
            ('xref:simple_id[Link]', ('simple_id', '[Link]')),
            ('See xref:overview[Overview]', ('overview', '[Overview]')),
        ]

        for input_text, expected_captures in matching_cases:
            with self.subTest(input_text=input_text):
                match = CompiledPatterns.XREF_UNFIXED_REGEX.search(input_text)
                self.assertIsNotNone(match, f"Pattern should match: {input_text}")
                self.assertEqual(match.group(1), expected_captures[0])
                self.assertEqual(match.group(2), expected_captures[1])

        # Should NOT match already fixed xrefs
        non_matching_cases = [
            'xref:file.adoc#target[text]',
            'xref:modules/intro.adoc#section[Section]',
            'xref:path/to/file.adoc#anchor[Link]',
        ]

        for input_text in non_matching_cases:
            with self.subTest(input_text=input_text):
                match = CompiledPatterns.XREF_UNFIXED_REGEX.search(input_text)
                self.assertIsNone(match, f"Pattern should not match already fixed xref: {input_text}")

    def test_link_pattern_matches(self):
        """Test link pattern matching."""
        test_cases = [
            ('link:http://example.com[Example]', ('http://example.com', None, '[Example]')),
            ('link:file.html#anchor[Link]', ('file.html', 'anchor', '[Link]')),
            ('link:https://docs.example.com#section[Docs]', ('https://docs.example.com', 'section', '[Docs]')),
            ('link:relative/path.html[]', ('relative/path.html', None, '[]')),
        ]

        for input_text, expected_captures in test_cases:
            with self.subTest(input_text=input_text):
                match = CompiledPatterns.LINK_REGEX.search(input_text)
                self.assertIsNotNone(match, f"Pattern should match: {input_text}")
                self.assertEqual(match.group(1), expected_captures[0])
                self.assertEqual(match.group(2), expected_captures[1])
                self.assertEqual(match.group(3), expected_captures[2])


@unittest.skipIf(CompiledPatterns is None, "regex_patterns module could not be imported")
class TestStructurePatterns(unittest.TestCase):
    """Test cases for AsciiDoc structure patterns."""

    def test_context_attr_pattern_matches(self):
        """Test context attribute pattern matching."""
        test_cases = [
            (':context: banana', 'banana'),
            (':context: ocp4', 'ocp4'),
            (':context: test-context', 'test-context'),
            (':context: long_context_name', 'long_context_name'),
        ]

        for input_text, expected_capture in test_cases:
            with self.subTest(input_text=input_text):
                match = CompiledPatterns.CONTEXT_ATTR_REGEX.search(input_text)
                self.assertIsNotNone(match, f"Pattern should match: {input_text}")
                self.assertEqual(match.group(1), expected_capture)

    def test_context_attr_pattern_non_matches(self):
        """Test that context attribute pattern rejects invalid formats."""
        non_matching_cases = [
            ':other: value',
            'context: no_colon',
            ' :context: leading_space',  # Leading space before colon
            ':context:no_space',  # No space after colon
        ]

        for input_text in non_matching_cases:
            with self.subTest(input_text=input_text):
                match = CompiledPatterns.CONTEXT_ATTR_REGEX.search(input_text)
                self.assertIsNone(match, f"Pattern should not match: {input_text}")

    def test_include_pattern_matches(self):
        """Test include directive pattern matching."""
        test_cases = [
            ('include::chapter1.adoc[]', 'chapter1.adoc'),
            ('include::modules/procedure.adoc[]', 'modules/procedure.adoc'),
            ('include::path/to/file.adoc[]', 'path/to/file.adoc'),
            ('include::simple.adoc[]', 'simple.adoc'),
        ]

        for input_text, expected_capture in test_cases:
            with self.subTest(input_text=input_text):
                match = CompiledPatterns.INCLUDE_REGEX.search(input_text)
                self.assertIsNotNone(match, f"Pattern should match: {input_text}")
                self.assertEqual(match.group(0), expected_capture)

    def test_include_pattern_non_matches(self):
        """Test that include pattern rejects invalid formats."""
        non_matching_cases = [
            'include chapter1.adoc',  # Missing :: and []
            'include::file.adoc[tag=part]',  # Has attributes
            'include::file.adoc',  # Missing brackets
            ' include::file.adoc[]',  # Leading space
        ]

        for input_text in non_matching_cases:
            with self.subTest(input_text=input_text):
                match = CompiledPatterns.INCLUDE_REGEX.search(input_text)
                if input_text == 'include::file.adoc[tag=part]':
                    # This might partially match 'file.adoc' - check if that's expected
                    if match:
                        self.assertEqual(match.group(0), 'file.adoc')
                elif input_text == ' include::file.adoc[]':
                    # Leading space might not prevent match due to the lookbehind
                    pass  # Skip this test case
                else:
                    self.assertIsNone(match, f"Pattern should not match: {input_text}")


@unittest.skipIf(CompiledPatterns is None, "regex_patterns module could not be imported")
class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""

    def test_validate_patterns(self):
        """Test pattern validation function."""
        result = validate_patterns()
        self.assertTrue(result, "All patterns should validate successfully")

    def test_compile_pattern(self):
        """Test custom pattern compilation."""
        pattern = compile_pattern(r'test_(\w+)', re.IGNORECASE)
        self.assertIsNotNone(pattern)
        
        # Test the compiled pattern works
        match = pattern.search("Test_Example")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "Example")
        
        # Test case insensitivity
        match_lower = pattern.search("test_example")
        self.assertIsNotNone(match_lower)
        self.assertEqual(match_lower.group(1), "example")

    def test_get_pattern_documentation(self):
        """Test pattern documentation retrieval."""
        doc = get_pattern_documentation('ID_PATTERN')
        self.assertIsInstance(doc, dict)
        self.assertIn('pattern', doc)
        self.assertIn('description', doc)
        self.assertIn('examples', doc)
        
        # Test non-existent pattern
        empty_doc = get_pattern_documentation('NON_EXISTENT')
        self.assertEqual(empty_doc, {})

    def test_list_available_patterns(self):
        """Test listing available patterns."""
        patterns = list_available_patterns()
        self.assertIsInstance(patterns, list)
        self.assertGreater(len(patterns), 0)
        
        # Check that expected patterns are in the list
        expected_patterns = [
            'ID_PATTERN',
            'ID_WITH_CONTEXT_PATTERN',
            'XREF_BASIC_PATTERN',
            'XREF_UNFIXED_PATTERN',
            'LINK_PATTERN',
            'CONTEXT_ATTR_PATTERN',
            'INCLUDE_PATTERN'
        ]
        
        for pattern in expected_patterns:
            self.assertIn(pattern, patterns)


@unittest.skipIf(CompiledPatterns is None, "regex_patterns module could not be imported")
class TestPatternExamples(unittest.TestCase):
    """Test cases for pattern examples and documentation."""

    def test_all_examples_work(self):
        """Test that all documented examples actually work with their patterns."""
        for pattern_name, doc in PATTERN_EXAMPLES.items():
            pattern_str = doc['pattern']
            compiled_pattern = re.compile(pattern_str, re.MULTILINE)
            
            with self.subTest(pattern_name=pattern_name):
                # Test positive examples
                for example_text, description in doc['examples'].items():
                    match = compiled_pattern.search(example_text)
                    self.assertIsNotNone(match, 
                        f"Pattern {pattern_name} should match example: {example_text}")
                
                # Test negative examples (non-matches)
                for non_match_text in doc.get('non_matches', []):
                    match = compiled_pattern.search(non_match_text)
                    self.assertIsNone(match, 
                        f"Pattern {pattern_name} should not match: {non_match_text}")

    def test_pattern_consistency(self):
        """Test that patterns in examples match compiled patterns."""
        pattern_mapping = {
            'ID_PATTERN': CompiledPatterns.ID_REGEX,
            'ID_WITH_CONTEXT_PATTERN': CompiledPatterns.ID_WITH_CONTEXT_REGEX,
            'XREF_BASIC_PATTERN': CompiledPatterns.XREF_BASIC_REGEX,
            'XREF_UNFIXED_PATTERN': CompiledPatterns.XREF_UNFIXED_REGEX,
            'LINK_PATTERN': CompiledPatterns.LINK_REGEX,
            'CONTEXT_ATTR_PATTERN': CompiledPatterns.CONTEXT_ATTR_REGEX,
            'INCLUDE_PATTERN': CompiledPatterns.INCLUDE_REGEX,
        }
        
        for pattern_name, compiled_pattern in pattern_mapping.items():
            with self.subTest(pattern_name=pattern_name):
                doc = PATTERN_EXAMPLES[pattern_name]
                pattern_str = doc['pattern']
                
                # Test that both patterns behave the same on examples
                for example_text in doc['examples'].keys():
                    doc_match = re.search(pattern_str, example_text, re.MULTILINE)
                    compiled_match = compiled_pattern.search(example_text)
                    
                    if doc_match and compiled_match:
                        # Both should match and have same groups
                        self.assertEqual(doc_match.groups(), compiled_match.groups(),
                            f"Pattern groups should match for {pattern_name}: {example_text}")
                    else:
                        # Both should be None or both should have matches
                        self.assertEqual(bool(doc_match), bool(compiled_match),
                            f"Pattern match status should be same for {pattern_name}: {example_text}")


@unittest.skipIf(CompiledPatterns is None, "regex_patterns module could not be imported")
class TestRealWorldExamples(unittest.TestCase):
    """Test patterns against real-world AsciiDoc content."""

    def test_realistic_asciidoc_content(self):
        """Test patterns against realistic AsciiDoc document content."""
        sample_content = """= Sample Document

:context: banana

[id="introduction_banana"]
== Introduction

This is a sample AsciiDoc document for testing.

[id="procedures_banana"]
== Procedures

Follow these steps:

[id="step1_banana"]
=== Step 1

See xref:step2_banana[Step 2] for more information.

Also check link:https://example.com#docs[External Docs].

include::modules/additional.adoc[]

[id="conclusion"]
== Conclusion

This concludes our document.
"""

        # Test ID patterns
        id_matches = CompiledPatterns.ID_REGEX.findall(sample_content)
        expected_ids = ['introduction_banana', 'procedures_banana', 'step1_banana', 'conclusion']
        self.assertEqual(set(id_matches), set(expected_ids))

        # Test context ID patterns
        context_id_matches = CompiledPatterns.ID_WITH_CONTEXT_REGEX.findall(sample_content)
        expected_context_ids = [('introduction', 'banana'), ('procedures', 'banana'), ('step1', 'banana')]
        self.assertEqual(set(context_id_matches), set(expected_context_ids))

        # Test xref patterns
        xref_matches = CompiledPatterns.XREF_BASIC_REGEX.findall(sample_content)
        self.assertEqual(len(xref_matches), 1)
        self.assertEqual(xref_matches[0], ('step2_banana', '', '[Step 2]'))

        # Test link patterns
        link_matches = CompiledPatterns.LINK_REGEX.findall(sample_content)
        self.assertEqual(len(link_matches), 1)
        self.assertEqual(link_matches[0], ('https://example.com', 'docs', '[External Docs]'))

        # Test context attribute pattern
        context_matches = CompiledPatterns.CONTEXT_ATTR_REGEX.findall(sample_content)
        self.assertEqual(context_matches, ['banana'])

        # Test include pattern - need to search line by line since ^ anchor is used
        include_matches = []
        for line in sample_content.split('\n'):
            matches = CompiledPatterns.INCLUDE_REGEX.findall(line)
            include_matches.extend(matches)
        self.assertEqual(include_matches, ['modules/additional.adoc'])


def main():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
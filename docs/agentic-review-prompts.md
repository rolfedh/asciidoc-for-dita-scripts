# Agentic Code Review Prompts

This document contains a collection of prompts to guide AI-assisted code review and optimization for the `asciidoc-dita-toolkit` project. Use these prompts with GitHub Copilot or other AI coding assistants to ensure thorough, professional code review.

## Quick Review Commands

### Basic Review
```
Please perform a comprehensive code review of the current branch/PR focusing on:
1. Code quality and Python best practices
2. Potential bugs or runtime errors
3. Breaking changes and backwards compatibility
4. Documentation accuracy and completeness
5. Test coverage gaps
```

### Detailed Architecture Review
```
Act as a senior software architect and review this code for:
- Design patterns and architectural consistency
- SOLID principles adherence
- Code organization and module separation
- API design and usability
- Performance implications
- Security considerations
- Maintainability and extensibility
```

## Specific Review Categories

### 🐛 Bug Detection and Error Handling
```
Analyze the code for potential issues:
- Missing imports or circular dependencies
- Unhandled exceptions and error cases
- Type mismatches and runtime errors
- Resource leaks (file handles, memory)
- Edge cases in input validation
- Null/None pointer issues
- Logic errors in conditional statements

For each issue found, provide:
- File name and line number
- Specific problem description
- Suggested fix with code example
- Severity level (critical/high/medium/low)
```

### 🔄 Refactoring Opportunities
```
Identify refactoring opportunities:
- Code duplication (DRY principle violations)
- Functions/classes that are too large or complex
- Poor naming conventions
- Magic numbers and hardcoded values
- Nested conditional complexity
- Opportunities for extraction of reusable components
- Dead code elimination

Suggest specific refactoring steps with before/after examples.
```

### 📚 Documentation and Type Safety
```
Review documentation and type safety:
- Missing or inaccurate docstrings
- Unclear function/class descriptions
- Missing type hints
- Inconsistent documentation style
- Example code in docstrings
- README and user-facing documentation accuracy
- Code comments that explain "why" not just "what"

Suggest improvements with proper Python docstring format examples.
```

### 🧪 Testing and Quality Assurance
```
Evaluate testing coverage and quality:
- Missing test cases for new functionality
- Edge cases that should be tested
- Test code quality and maintainability
- Mock usage appropriateness
- Integration vs unit test balance
- Test naming conventions
- Setup/teardown patterns

Suggest specific test cases that should be added.
```

### ⚡ Performance and Optimization
```
Analyze for performance issues:
- Inefficient algorithms or data structures
- Unnecessary loops or redundant operations
- Memory usage patterns
- I/O operations that could be optimized
- Caching opportunities
- Lazy loading possibilities
- Database query optimization (if applicable)

Provide performance improvement suggestions with estimated impact.
```

### 🔒 Security Review
```
Conduct a security-focused review:
- Input validation and sanitization
- Path traversal vulnerabilities
- Command injection possibilities
- File access permissions
- Error message information leakage
- Dependency security considerations
- Secrets handling

Flag potential security issues with mitigation strategies.
```

### 🏗️ API Design and Usability
```
Evaluate API design and developer experience:
- Function signature clarity and consistency
- Parameter naming and ordering
- Return value patterns
- Error handling approaches
- Breaking changes in public APIs
- Backwards compatibility maintenance
- CLI interface usability
- Configuration file handling

Suggest improvements for better developer experience.
```

## Comprehensive Review Template

### Full Feature Branch Review
```
Please conduct a thorough code review as a senior developer would, covering:

**Code Quality (25%)**
- Python best practices and PEP 8 compliance
- Naming conventions and code readability
- Function/class size and complexity
- Code organization and module structure

**Functionality (25%)**
- Feature completeness and correctness
- Edge case handling
- Error conditions and recovery
- Input validation and sanitization

**Architecture (20%)**
- Design pattern usage
- SOLID principles adherence
- Module coupling and cohesion
- Extensibility and maintainability

**Testing (15%)**
- Test coverage adequacy
- Test quality and maintainability
- Missing test scenarios
- Integration test considerations

**Documentation (10%)**
- Code documentation quality
- User-facing documentation accuracy
- API documentation completeness
- Example usage clarity

**Security & Performance (5%)**
- Security vulnerability assessment
- Performance bottleneck identification
- Resource usage optimization
- Scalability considerations

For each issue found, provide:
1. **File:Line** - Exact location
2. **Severity** - Critical/High/Medium/Low
3. **Category** - Bug/Design/Performance/Security/Documentation
4. **Description** - Clear problem statement
5. **Solution** - Specific fix with code example
6. **Impact** - Why this matters

Format findings as actionable code review comments suitable for GitHub PR reviews.
```

## Specialized Domain Reviews

### Plugin Architecture Review
```
Review the plugin system specifically:
- Plugin discovery and loading mechanism
- Plugin interface consistency
- Error handling in plugin loading
- Plugin isolation and dependencies
- Configuration and customization options
- Plugin documentation and examples
- Backwards compatibility for plugin API
```

### CLI Tool Review
```
Evaluate the command-line interface:
- Argument parsing consistency
- Help message clarity and completeness
- Error message quality and actionability
- Exit code conventions
- Configuration file handling
- Environment variable support
- User experience and discoverability
```

### File Processing Review
```
Analyze file processing functionality:
- File encoding handling
- Path traversal safety
- Large file processing efficiency
- Concurrent file processing safety
- Backup and recovery mechanisms
- Progress reporting and cancellation
- Cross-platform compatibility
```

## Post-Review Actions

### Implementation Priority
```
After identifying issues, help prioritize them:
1. **Must Fix Before Merge** - Critical bugs, security issues, breaking changes
2. **Should Fix Soon** - Performance issues, significant design problems
3. **Nice to Have** - Minor refactoring, documentation improvements
4. **Future Consideration** - Major architectural changes, new features

Provide a prioritized action plan with estimated effort for each item.
```

### Regression Prevention
```
Suggest strategies to prevent similar issues in the future:
- Additional automated checks (linting, type checking)
- Code review checklist items
- Testing patterns and practices
- Documentation standards
- Development workflow improvements
```

## Usage Instructions

1. **Copy relevant prompt sections** based on your review needs
2. **Customize for specific features** being reviewed
3. **Paste into your AI coding assistant** along with the code context
4. **Review the suggestions** and adapt to your project's specific needs
5. **Create actionable GitHub review comments** from the findings

## Example Usage

```
@agent I'm working on PR #42 which adds a new EntityReference plugin. 
Please use the "Full Feature Branch Review" template above to review my changes, 
paying special attention to the "Plugin Architecture Review" aspects.
```

---

*This document is a living resource - update it as you discover new review patterns and needs for your project.*

# ContentType Plugin Minimalist Interface Proposal

## Startup Options
```
ContentType Plugin - Press Ctrl+Q for quiet mode (auto-assigns TBD), or any other key to continue
```

## Successful Operations
```
File: installing_docker.adoc — Updated: PROCEDURE
File: what_is_containerization.adoc — Updated: CONCEPT
File: docker_guide_assembly.adoc — Updated: ASSEMBLY
```

## Files Needing Input
```
File: installing_docker.adoc — Missing content type
Analysis: PROCEDURE (found numbered steps)
Type: **A**SSEMBLY, **C**ONCEPT, **P**ROCEDURE, **R**EFERENCE, **S**NIPPET, **T**BD
Suggestion: PROCEDURE.
Press: Enter to accept; the first letter of a type; Ctrl+C to quit; or Ctrl+S to skip

File: what_is_containerization.adoc — Missing content type  
Analysis: CONCEPT (explanatory title)
Type: **A**SSEMBLY, **C**ONCEPT, **P**ROCEDURE, **R**EFERENCE, **S**NIPPET, **T**BD
Suggestion: CONCEPT.
Press: Enter to accept; the first letter of a type; Ctrl+C to quit; or Ctrl+S to skip

File: docker_commands.adoc — Missing content type
Analysis: REFERENCE (found tables and reference title)
Type: **A**SSEMBLY, **C**ONCEPT, **P**ROCEDURE, **R**EFERENCE, **S**NIPPET, **T**BD
Suggestion: REFERENCE.
Press: Enter to accept; the first letter of a type; Ctrl+C to quit; or Ctrl+S to skip

File: empty_content_type.adoc — Missing content type
Analysis: CONCEPT (default)
Type: **A**SSEMBLY, **C**ONCEPT, **P**ROCEDURE, **R**EFERENCE, **S**NIPPET, **T**BD
Suggestion: CONCEPT.
Press: Enter to accept; the first letter of a type; Ctrl+C to quit; or Ctrl+S to skip

File: complex_file.adoc — Missing content type
Analysis: TBD (content analysis failed)
Type: **A**SSEMBLY, **C**ONCEPT, **P**ROCEDURE, **R**EFERENCE, **S**NIPPET, **T**BD
Suggestion: TBD.
Press: Enter to accept; the first letter of a type; Ctrl+C to quit; or Ctrl+S to skip
```

## Quiet Mode Output
```
File: installing_docker.adoc — Auto-assigned: TBD
File: what_is_containerization.adoc — Auto-assigned: TBD
File: docker_commands.adoc — Auto-assigned: TBD
File: empty_content_type.adoc — Auto-assigned: TBD
File: complex_file.adoc — Auto-assigned: TBD
```

## Error Cases
```
File: installing_docker.adoc — Input error
Error: Unable to read user input

File: corrupted_file.adoc — Processing error  
Error: Unable to read file content
```

## Interface Elements

### Status Messages
- **Success**: `File: [filename] — Updated: [TYPE]`
- **Conversion**: `File: [filename] — Converted: [OLD_TYPE] → [NEW_TYPE]`
- **Auto-detected**: `File: [filename] — Detected: [TYPE]`
- **Quiet mode**: `File: [filename] — Auto-assigned: TBD`

### Interactive Prompts
- **File header**: `File: [filename] — [problem description]`
- **Analysis line**: `Analysis: [TYPE] ([brief reasoning])` or `Analysis: TBD (content analysis failed)`
- **Type menu**: `Type: **A**SSEMBLY, **C**ONCEPT, **P**ROCEDURE, **R**EFERENCE, **S**NIPPET, **T**BD`
- **Suggestion**: `Suggestion: [TYPE].`
- **Controls**: `Press: Enter to accept; the first letter of a type; Ctrl+C to quit; or Ctrl+S to skip`

### Error Messages
- **Processing error**: `File: [filename] — Processing error`
- **Input error**: `File: [filename] — Input error`
- **Error detail**: `Error: [brief error message]`

### Navigation
- **Default processing**: Process all files automatically, prompt only when content type is missing or unclear
- **Quiet mode**: `Ctrl+Q` at startup to process all files without prompts, defaults to TBD when type is unknown
- **Skip files**: Continue to next file without changes

## Key Design Principles

1. **Minimal text**: Remove emojis, verbose explanations, and decorative elements
2. **Consistent format**: Same structure for all file status messages
3. **Clear hierarchy**: File name first, then status/problem, then details
4. **Brief analysis**: One line explanation of content type suggestion (TBD when analysis fails)
5. **Simple controls**: Enter to accept, first letter to choose type, Ctrl+C to quit, Ctrl+S to skip
6. **Reduced visual noise**: No separators, minimal punctuation
7. **Grouped output**: Successful operations shown together, errors grouped separately
8. **Automatic processing**: Process all files continuously, only prompt when user input is needed
9. **Quiet mode option**: Allow users to process all files without prompts for unattended operation
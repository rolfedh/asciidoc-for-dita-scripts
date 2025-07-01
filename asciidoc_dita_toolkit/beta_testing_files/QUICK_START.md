# Beta Testing Quick Start

## 🚀 Fastest Way to Start Testing

1. **Download test files:**
   ```bash
   curl -L https://github.com/rolfedh/asciidoc-dita-toolkit/archive/refs/heads/main.zip -o test-files.zip
   unzip test-files.zip
   cd asciidoc-dita-toolkit-main/beta-testing/
   ```

2. **Test with Docker (no installation needed):**
   ```bash
   # Review mode - see what would be fixed
   docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:beta \
     ContentType --mode review --directory /workspace

   # Interactive mode - try fixing files
   docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:beta \
     ContentType --mode interactive --file missing_content_type.adoc
   ```

3. **Or install locally:**
   ```bash
   pip install asciidoc-dita-toolkit==0.1.8b1
   asciidoc-dita-toolkit ContentType --mode review --directory .
   ```

## 📋 Test Files Included

- `missing_content_type.adoc` - No content type (should be detected)
- `empty_content_type.adoc` - Empty content type value (should be detected)
- `commented_content_type.adoc` - Commented out content type (should be detected)
- `wrong_content_type.adoc` - Legacy format (should be detected)
- `correct_*.adoc` - Files with proper content types (should be ignored)

## 🎯 What to Test

- Try each mode: `review`, `interactive`, `auto`, `guided`
- Test single files and directories
- Use `--dry-run` to see changes without applying them
- Check that correct files are left unchanged

Happy testing! Report issues at: https://github.com/rolfedh/asciidoc-dita-toolkit/issues

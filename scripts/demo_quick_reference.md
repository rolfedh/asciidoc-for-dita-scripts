# Demo Quick Reference Card

## 🎬 Demo Script Commands
```bash
# 1. Validate your environment before demo
./scripts/pre_demo_check.sh

# 2. Run the full interactive demo
./scripts/demo_v2.sh
```

- The following files are for your preparation and reference only (not to be run):
  - DEMO_PRESENTATION.md (slides)
  - demo_quick_reference.md (this cheat sheet)

## 📝 Key Talking Points

### Section 1: The Problem (30 sec)
- **Old pain points**: Multiple packages, broken installations, support tickets
- **User frustration**: ImportError, missing modules, inconsistent CLI

### Section 2: The Solution (2 min)
- **Single command**: `pip install asciidoc-dita-toolkit`
- **Immediate functionality**: All plugins work out of the box
- **Professional experience**: Clean CLI, proper versioning

### Section 3: The Features (5 min)
- **All 6 plugins working**: ContentType, EntityReference, CrossReference, etc.
- **Real demonstrations**: Live file processing with visible results
- **Seamless integration**: Multiple plugins working together

### Section 4: Developer Experience (2 min)
- **Professional PyPI package**: Rich metadata, proper branding
- **Quality assurance**: 196 tests passing
- **Modern tooling**: pyproject.toml, comprehensive docs

### Section 5: The Impact (1 min)
- **Business value**: Reduced support, professional reputation
- **Technical achievement**: Zero functionality loss, modern standards
- **Future opportunities**: Solid foundation for growth

## 🎯 Demo Highlights to Emphasize

1. **"Watch this"** - Single pip install vs. old fragmented approach
2. **"See the intelligence"** - ContentType auto-detection 
3. **"Look at the transformation"** - EntityReference conversions
4. **"All 6 plugins, one interface"** - Plugin discovery
   - **Legacy plugins**: These are the original, battle-tested tools from previous toolkit versions, now auto-discovered and fully integrated for backward compatibility.
   - **New modules**: These are the modern, unified plugin classes designed for the new architecture, offering improved maintainability and a consistent interface.
5. **"Professional quality"** - PyPI package metadata
6. **"Zero functionality lost"** - All features preserved and enhanced

## 🚨 Potential Questions & Answers

**Q: "What about existing users?"**  
A: Smooth migration path documented, backward compatibility maintained

**Q: "Performance impact?"**  
A: Same performance, better reliability with 196 tests

**Q: "Maintenance burden?"**  
A: Actually reduced - unified codebase easier to maintain

**Q: "Why should we care?"**  
A: Professional reputation, reduced support tickets, happy users

## ⚡ Emergency Fallbacks

If live demo fails:
1. Show static examples in DEMO_PRESENTATION.md
2. Reference PyPI page: https://pypi.org/project/asciidoc-dita-toolkit/
3. Show test results: `make test` output
4. Demonstrate CLI help: `adt --help`

## 🎉 Closing Message

**"This unified package represents our commitment to professional, reliable tools. We've taken a fragmented user experience and created something our team can be proud to recommend. Questions?"**

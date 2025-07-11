# 🎯 AsciiDoc DITA Toolkit v2.0.x Demo Package

Welcome to the comprehensive demo package for the **AsciiDoc DITA Toolkit v2.0.x**! This package contains everything you need to showcase the powerful features of the unified package.

## 📦 What's in This Demo Package

### 1. **Enhanced Live Demo** (`enhanced_demo.py`)
- 🎨 **Colorful CLI output** with progress bars and animations
- 📊 **Real-time statistics** and performance metrics
- 🔄 **Live file processing** demonstrations
- 📈 **Interactive progress tracking**

### 2. **Sample Files** (`sample_files/`)
- 📄 **Realistic .adoc files** that demonstrate each plugin's capabilities
- 🎯 **Before/after examples** showing transformations
- 🧪 **Test scenarios** with various edge cases
- 📝 **Documentation examples** from real-world use cases

### 3. **Static Presentation** (`presentation.md`)
- 📋 **Comprehensive feature overview** with visual examples
- 🏗️ **Architecture diagrams** and plugin relationships
- 📊 **Comparison charts** showing v2.0.x improvements
- 🎬 **Step-by-step walkthrough** for your narration

### 4. **Interactive Web Demo** (`web_demo.html`)
- 🌐 **Browser-based demo** perfect for screen sharing
- 🔄 **Live transformations** with before/after views
- 📱 **Responsive design** for any display size
- 🎨 **Professional styling** with modern UI

## 🚀 Quick Start

### Option A: Enhanced Live Demo (Recommended)
```bash
python demo/enhanced_demo.py
```

### Option B: Static Presentation
```bash
# View the markdown presentation
cat demo/presentation.md

# Or convert to HTML for better viewing
python -m markdown demo/presentation.md > demo/presentation.html
```

### Option C: Web Demo
```bash
# Open in browser
python -m http.server 8000
# Then visit: http://localhost:8000/demo/web_demo.html
```

### Option D: All Together
```bash
# Run the setup script that prepares everything
./demo/setup_demo.sh
```

## 🎭 Demo Features Showcase

### 🔥 Major v2.0.x Highlights
- **Unified Package**: Single `pip install asciidoc-dita-toolkit`
- **Simple CLI**: Just `adt` command for everything
- **Complete Solution**: Core framework + all 6 plugins
- **Container Support**: Docker images for consistency
- **Production Ready**: 196 comprehensive tests

### 🔌 Six Powerful Plugins
1. **EntityReference** - HTML entity replacement
2. **ContentType** - Content type label management
3. **DirectoryConfig** - Directory-based configuration
4. **ContextAnalyzer** - Content context analysis
5. **ContextMigrator** - Context migration utilities
6. **CrossReference** - Cross-reference validation

## 🎬 Demo Scripts

### For Live Presentations
```bash
# Interactive demo with narration pauses
python demo/enhanced_demo.py --interactive

# Automated demo for continuous display
python demo/enhanced_demo.py --auto-play
```

### For Screenshots/Recording
```bash
# Generate static outputs for documentation
python demo/enhanced_demo.py --screenshot-mode
```

## 🔧 Customization

### Modify Sample Files
Edit files in `sample_files/` to demonstrate your specific use cases:
- `sample_files/entity_examples.adoc` - Entity reference examples
- `sample_files/content_type_examples.adoc` - Content type examples
- `sample_files/complex_document.adoc` - Multi-plugin example

### Customize Demo Script
Edit `enhanced_demo.py` to:
- Add your own branding/colors
- Modify timing and pacing
- Add custom demo scenarios
- Include your own sample files

## 📊 Performance Metrics

The demo includes real performance metrics:
- **Processing Speed**: Files per second
- **Memory Usage**: Peak memory consumption
- **Plugin Efficiency**: Individual plugin performance
- **Success Rates**: Processing success percentages

## 🎯 Target Audience

This demo is designed for:
- **Technical Teams** - Showcasing integration capabilities
- **Documentation Teams** - Demonstrating workflow improvements
- **Management** - Highlighting productivity gains
- **New Users** - Onboarding and feature discovery

## 🛠️ Requirements

- Python 3.8+
- AsciiDoc DITA Toolkit v2.0.x
- Optional: Modern web browser for web demo

## 🤝 Demo Tips

1. **Start with the problem** - Show broken .adoc files first
2. **Demonstrate the solution** - Run plugins to fix issues
3. **Show the results** - Display before/after comparisons
4. **Highlight automation** - Emphasize batch processing capabilities
5. **Emphasize v2.0.x benefits** - Unified package, simple CLI

## 📞 Support

Need help customizing the demo?
- 📖 Check the [main README](../README.md)
- 🐛 Report issues on [GitHub](https://github.com/rolfedh/asciidoc-dita-toolkit/issues)
- 💬 Ask questions in discussions

---

**Ready to impress your team?** 🚀

Choose your demo style and let's show them what v2.0.x can do!
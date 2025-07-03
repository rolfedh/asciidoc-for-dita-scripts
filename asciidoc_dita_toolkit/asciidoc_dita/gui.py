"""
GUI Interface for AsciiDoc DITA Toolkit

A simple dialog-based interface for plugin selection, configuration, and operation.
"""

import importlib
import os
import shutil
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path

from .toolkit import discover_plugins
from .file_utils import process_adoc_files


class ToolkitGUI:
    """Main GUI application for the AsciiDoc DITA Toolkit."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AsciiDoc DITA Toolkit")
        self.root.geometry("800x600")
        
        # Create menu bar
        self.create_menu_bar()
        
        # Plugin management
        self.plugins = {}
        self.selected_plugin = None
        self.current_mode = tk.StringVar(value="review")
        self.current_file = tk.StringVar()
        self.current_directory = tk.StringVar()
        self.recursive = tk.BooleanVar()
        self.dry_run = tk.BooleanVar(value=True)
        
        # Load plugins
        self.load_plugins()
        
        # Create UI
        self.create_widgets()
        
        # Start with first plugin selected
        if self.plugins:
            first_plugin = list(self.plugins.keys())[0]
            self.plugin_var.set(first_plugin)
            self.on_plugin_selected()
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
    
    def create_menu_bar(self):
        """Create the menu bar with File and Help menus."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Test Files", command=self.load_test_files, accelerator="Ctrl+L")
        file_menu.add_separator()
        file_menu.add_command(label="Save Results", command=self.save_results, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy Results", command=self.copy_results, accelerator="Ctrl+C")
        edit_menu.add_command(label="Select All", command=self.select_all_results, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear Results", command=self.clear_results, accelerator="Ctrl+R")
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Plugin", command=self.run_plugin, accelerator="F5")
        run_menu.add_separator()
        run_menu.add_command(label="Clear Results", command=self.clear_results, accelerator="Esc")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts_help)
        help_menu.add_command(label="About Plugins", command=self.show_plugins_help)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
    
    def load_plugins(self):
        """Load all available plugins."""
        plugin_names = discover_plugins()
        
        for modname in plugin_names:
            try:
                module = importlib.import_module(
                    f".plugins.{modname}", 
                    package="asciidoc_dita_toolkit.asciidoc_dita"
                )
                desc = getattr(module, "__description__", module.__doc__ or "No description")
                desc = desc.strip().split("\n")[0] if desc else "No description"
                
                self.plugins[modname] = {
                    'module': module,
                    'description': desc,
                    'name': modname
                }
            except Exception as e:
                print(f"Error loading plugin '{modname}': {e}", file=sys.stderr)
    
    def create_widgets(self):
        """Create the main UI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Plugin selection
        ttk.Label(main_frame, text="Plugin:", font=("TkDefaultFont", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.plugin_var = tk.StringVar()
        plugin_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.plugin_var,
            values=list(self.plugins.keys()),
            state="readonly",
            width=30
        )
        plugin_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        plugin_combo.bind('<<ComboboxSelected>>', lambda e: self.on_plugin_selected())
        
        # Plugin description
        self.desc_label = ttk.Label(main_frame, text="", foreground="gray")
        self.desc_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # File/Directory selection
        ttk.Label(config_frame, text="Target:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        target_frame = ttk.Frame(config_frame)
        target_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        target_frame.columnconfigure(0, weight=1)
        
        # File selection
        file_frame = ttk.Frame(target_frame)
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        file_frame.columnconfigure(0, weight=1)
        
        ttk.Label(file_frame, text="File:").grid(row=0, column=0, sticky=tk.W)
        file_entry = ttk.Entry(file_frame, textvariable=self.current_file)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=2)
        
        # Directory selection
        dir_frame = ttk.Frame(target_frame)
        dir_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        dir_frame.columnconfigure(0, weight=1)
        
        ttk.Label(dir_frame, text="Directory:").grid(row=0, column=0, sticky=tk.W)
        dir_entry = ttk.Entry(dir_frame, textvariable=self.current_directory)
        dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).grid(row=0, column=2)
        
        # Mode selection (for ContentType plugin)
        ttk.Label(config_frame, text="Mode:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        mode_frame = ttk.Frame(config_frame)
        mode_frame.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        modes = [("Review (preview only)", "review"), 
                ("Interactive (approve each)", "interactive"),
                ("Auto (apply all)", "auto"), 
                ("Guided (with explanations)", "guided")]
        
        for i, (text, value) in enumerate(modes):
            ttk.Radiobutton(
                mode_frame, 
                text=text, 
                variable=self.current_mode, 
                value=value
            ).grid(row=i//2, column=i%2, sticky=tk.W, padx=(0, 20))
        
        # Options
        options_frame = ttk.Frame(config_frame)
        options_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        ttk.Checkbutton(options_frame, text="Recursive", variable=self.recursive).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="Dry run (preview only)", variable=self.dry_run).grid(row=0, column=1, sticky=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="Load Test Files", command=self.load_test_files).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Run Plugin", command=self.run_plugin).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="Copy Results", command=self.copy_results).grid(row=0, column=3, padx=(0, 10))
        ttk.Button(button_frame, text="Save Results", command=self.save_results).grid(row=0, column=4)
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame, 
            wrap=tk.WORD, 
            height=15,
            font=("Consolas", 9)
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add right-click context menu to results text
        self.create_results_context_menu()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def on_plugin_selected(self):
        """Handle plugin selection change."""
        plugin_name = self.plugin_var.get()
        if plugin_name in self.plugins:
            self.selected_plugin = self.plugins[plugin_name]
            self.desc_label.config(text=self.selected_plugin['description'])
            self.log(f"Selected plugin: {plugin_name}")
    
    def browse_file(self):
        """Browse for a single AsciiDoc file."""
        filename = filedialog.askopenfilename(
            title="Select AsciiDoc file",
            filetypes=[("AsciiDoc files", "*.adoc"), ("All files", "*.*")]
        )
        if filename:
            self.current_file.set(filename)
            self.current_directory.set("")  # Clear directory when file is selected
    
    def browse_directory(self):
        """Browse for a directory."""
        dirname = filedialog.askdirectory(title="Select directory")
        if dirname:
            self.current_directory.set(dirname)
            self.current_file.set("")  # Clear file when directory is selected
    
    def load_test_files(self):
        """Load test files to current directory or selected directory."""
        try:
            # Look for test files in the package
            target_dir = self.current_directory.get() or os.getcwd()
            copied_count = 0
            
            # Get the root of the package
            try:
                package_root = Path(__file__).parent.parent.parent
                
                test_files_patterns = [
                    "tests/fixtures/ContentType/*.adoc",
                    "tests/fixtures/EntityReference/*.adoc"
                ]
                
                for pattern in test_files_patterns:
                    test_files = list(package_root.glob(pattern))
                    for test_file in test_files:
                        if test_file.is_file():
                            dest_path = Path(target_dir) / test_file.name
                            shutil.copy2(test_file, dest_path)
                            copied_count += 1
                            self.log(f"Copied: {test_file.name}")
                
                if copied_count == 0:
                    # Fallback: create sample test files
                    self._create_sample_test_files(target_dir)
                    copied_count = 5
                
                self.log(f"Total files copied: {copied_count} to {target_dir}")
                
                # Set directory to target if not already set
                if not self.current_directory.get():
                    self.current_directory.set(target_dir)
                    
            except Exception as e:
                self.log(f"Error finding test files, creating samples instead: {e}")
                self._create_sample_test_files(target_dir)
                copied_count = 5
                self.log(f"Created 5 sample test files in {target_dir}")
                
        except Exception as e:
            self.log(f"Error loading test files: {e}")
            messagebox.showerror("Error", f"Failed to load test files: {e}")
    
    def _create_sample_test_files(self, target_dir):
        """Create sample test files for testing."""
        sample_files = {
            "missing_content_type.adoc": """= Sample Procedure

This file is missing a content type attribute.

== Step 1

Do something.

== Step 2

Do something else.
""",
            "empty_content_type.adoc": """:_mod-docs-content-type:
= Sample Concept

This file has an empty content type attribute.

This is a concept that explains something important.
""",
            "commented_content_type.adoc": """//:_mod-docs-content-type: PROCEDURE
= Sample Procedure

This file has a commented-out content type attribute.

== Prerequisites

Before you begin...

== Step 1

Do the first thing.
""",
            "correct_procedure.adoc": """:_mod-docs-content-type: PROCEDURE
= Correct Procedure

This file has the correct content type attribute.

== Prerequisites

You need these things.

== Step 1

First step description.
""",
            "with_entities.adoc": """:_mod-docs-content-type: REFERENCE
= Reference with Entities

This file contains HTML entities like &copy; and &mdash; that should be converted.

Also has some &quot;quoted text&quot; and other entities like &bull; for bullets.
"""
        }
        
        for filename, content in sample_files.items():
            file_path = Path(target_dir) / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def run_plugin(self):
        """Run the selected plugin with current configuration."""
        if not self.selected_plugin:
            messagebox.showerror("Error", "No plugin selected")
            return
        
        file_path = self.current_file.get().strip()
        dir_path = self.current_directory.get().strip()
        
        if not file_path and not dir_path:
            messagebox.showerror("Error", "Please select a file or directory")
            return
        
        # Run in a separate thread to avoid blocking the UI
        thread = threading.Thread(target=self._run_plugin_thread)
        thread.daemon = True
        thread.start()
    
    def _run_plugin_thread(self):
        """Run plugin in a separate thread."""
        try:
            self.status_var.set("Running plugin...")
            
            plugin_name = self.plugin_var.get()
            file_path = self.current_file.get().strip()
            dir_path = self.current_directory.get().strip()
            
            self.log(f"\n{'='*60}")
            self.log(f"Running plugin: {plugin_name}")
            self.log(f"Mode: {self.current_mode.get()}")
            self.log(f"Dry run: {self.dry_run.get()}")
            self.log(f"Recursive: {self.recursive.get()}")
            
            if file_path:
                self.log(f"File: {file_path}")
            if dir_path:
                self.log(f"Directory: {dir_path}")
            
            self.log(f"{'='*60}\n")
            
            # Simulate plugin execution
            # In a real implementation, you would call the actual plugin functions
            if plugin_name == "ContentType":
                self._run_contenttype_plugin(file_path, dir_path)
            elif plugin_name == "EntityReference":
                self._run_entityreference_plugin(file_path, dir_path)
            else:
                self.log(f"Plugin '{plugin_name}' execution not implemented in GUI yet")
            
            self.status_var.set("Plugin execution completed")
            
        except Exception as e:
            self.log(f"Error running plugin: {e}")
            self.status_var.set("Error occurred")
    
    def _run_contenttype_plugin(self, file_path, dir_path):
        """Run the ContentType plugin."""
        try:
            # Import the plugin module
            module = self.selected_plugin['module']
            
            # Create a mock args object similar to what argparse would create
            class MockArgs:
                def __init__(self, file_path, dir_path, recursive_flag):
                    self.file = file_path if file_path else None
                    self.directory = dir_path if dir_path else None
                    self.recursive = recursive_flag
                    # Note: Current ContentType plugin doesn't support modes or dry_run
                    # These are for future compatibility
                    
            args = MockArgs(file_path, dir_path, self.recursive.get())
            
            # Add some logging about the mode (even though current plugin doesn't use it)
            mode = self.current_mode.get()
            dry_run = self.dry_run.get()
            
            if dry_run:
                self.log(f"Note: Dry run mode selected, but current ContentType plugin doesn't support it.")
                self.log(f"Plugin will modify files directly. Consider backing up your files first.")
            
            if mode != "auto":
                self.log(f"Note: '{mode}' mode selected, but current ContentType plugin doesn't support interactive modes.")
                self.log(f"Plugin will run in automatic mode.")
            
            # Redirect stdout to capture output
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                if hasattr(module, 'main'):
                    module.main(args)
                else:
                    self.log("Plugin main function not found")
            
            # Display captured output
            stdout_content = output_buffer.getvalue()
            stderr_content = error_buffer.getvalue()
            
            if stdout_content:
                self.log("Output:")
                self.log(stdout_content)
            else:
                self.log("Plugin completed successfully (no output)")
            
            if stderr_content:
                self.log("Errors/Warnings:")
                self.log(stderr_content)
                
        except Exception as e:
            self.log(f"Error executing ContentType plugin: {e}")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}")
    
    def _run_entityreference_plugin(self, file_path, dir_path):
        """Run the EntityReference plugin."""
        try:
            # Import the plugin module
            module = self.selected_plugin['module']
            
            # Create a mock args object
            class MockArgs:
                def __init__(self, file_path, dir_path, recursive_flag):
                    self.file = file_path if file_path else None
                    self.directory = dir_path if dir_path else None
                    self.recursive = recursive_flag
                    # Note: Current EntityReference plugin doesn't support modes or dry_run
            
            args = MockArgs(file_path, dir_path, self.recursive.get())
            
            # Add some logging about the mode/dry_run (even though current plugin doesn't use it)
            dry_run = self.dry_run.get()
            
            if dry_run:
                self.log(f"Note: Dry run mode selected, but current EntityReference plugin doesn't support it.")
                self.log(f"Plugin will modify files directly. Consider backing up your files first.")
            
            # Redirect output
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                if hasattr(module, 'main'):
                    module.main(args)
                else:
                    self.log("Plugin main function not found")
            
            # Display output
            stdout_content = output_buffer.getvalue()
            stderr_content = error_buffer.getvalue()
            
            if stdout_content:
                self.log("Output:")
                self.log(stdout_content)
            else:
                self.log("Plugin completed successfully (no output)")
            
            if stderr_content:
                self.log("Errors/Warnings:")
                self.log(stderr_content)
                
        except Exception as e:
            self.log(f"Error executing EntityReference plugin: {e}")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}")
    
    def clear_results(self):
        """Clear the results text area."""
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("Results cleared")
    
    def copy_results(self):
        """Copy the results text to clipboard."""
        try:
            results_content = self.results_text.get(1.0, tk.END)
            if results_content.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(results_content)
                self.root.update()  # Required to finalize clipboard operation
                self.status_var.set("Results copied to clipboard")
                messagebox.showinfo("Copy Results", "Results have been copied to clipboard.")
            else:
                messagebox.showwarning("Copy Results", "No results to copy. Run a plugin first.")
        except Exception as e:
            self.log(f"Error copying to clipboard: {e}")
            messagebox.showerror("Copy Error", f"Failed to copy results: {e}")
    
    def save_results(self):
        """Save the results text to a file."""
        try:
            results_content = self.results_text.get(1.0, tk.END)
            if not results_content.strip():
                messagebox.showwarning("Save Results", "No results to save. Run a plugin first.")
                return
            
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                title="Save Results",
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("Log files", "*.log"),
                    ("Markdown files", "*.md"),
                    ("All files", "*.*")
                ],
                initialname=f"asciidoc-dita-results-{self._get_timestamp()}.txt"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    # Add header with metadata
                    f.write(f"AsciiDoc DITA Toolkit Results\n")
                    f.write(f"Generated: {self._get_timestamp(include_date=True)}\n")
                    f.write(f"Plugin: {self.plugin_var.get()}\n")
                    f.write(f"Mode: {self.current_mode.get()}\n")
                    f.write(f"Target File: {self.current_file.get()}\n")
                    f.write(f"Target Directory: {self.current_directory.get()}\n")
                    f.write(f"Recursive: {self.recursive.get()}\n")
                    f.write(f"Dry Run: {self.dry_run.get()}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(results_content)
                
                self.status_var.set(f"Results saved to {filename}")
                messagebox.showinfo("Save Results", f"Results saved successfully to:\n{filename}")
                
        except Exception as e:
            self.log(f"Error saving results: {e}")
            messagebox.showerror("Save Error", f"Failed to save results: {e}")
    
    def _get_timestamp(self, include_date=False):
        """Get current timestamp for filenames."""
        import datetime
        now = datetime.datetime.now()
        if include_date:
            return now.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return now.strftime("%Y%m%d-%H%M%S")
    
    def run(self):
        """Start the GUI application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
    
    def create_results_context_menu(self):
        """Create right-click context menu for results text area."""
        self.results_context_menu = tk.Menu(self.root, tearoff=0)
        self.results_context_menu.add_command(label="Copy All", command=self.copy_results)
        self.results_context_menu.add_command(label="Copy Selection", command=self.copy_selection)
        self.results_context_menu.add_separator()
        self.results_context_menu.add_command(label="Save Results", command=self.save_results)
        self.results_context_menu.add_separator()
        self.results_context_menu.add_command(label="Clear Results", command=self.clear_results)
        self.results_context_menu.add_command(label="Select All", command=self.select_all_results)
        
        # Bind right-click to show context menu
        self.results_text.bind("<Button-3>", self.show_results_context_menu)  # Right-click on Linux/Windows
        self.results_text.bind("<Button-2>", self.show_results_context_menu)  # Middle-click on some systems
        self.results_text.bind("<Control-Button-1>", self.show_results_context_menu)  # Ctrl+click on macOS
    
    def show_results_context_menu(self, event):
        """Show the context menu at cursor position."""
        try:
            self.results_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.results_context_menu.grab_release()
    
    def copy_selection(self):
        """Copy the selected text from results area."""
        try:
            # Check if there's a selection
            if self.results_text.tag_ranges(tk.SEL):
                selected_text = self.results_text.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                self.root.update()
                self.status_var.set("Selection copied to clipboard")
            else:
                messagebox.showinfo("Copy Selection", "No text selected. Select text first or use 'Copy All'.")
        except tk.TclError:
            # No selection
            messagebox.showinfo("Copy Selection", "No text selected. Select text first or use 'Copy All'.")
        except Exception as e:
            self.log(f"Error copying selection: {e}")
            messagebox.showerror("Copy Error", f"Failed to copy selection: {e}")
    
    def select_all_results(self):
        """Select all text in the results area."""
        self.results_text.tag_add(tk.SEL, "1.0", tk.END)
        self.results_text.mark_set(tk.INSERT, "1.0")
        self.results_text.see(tk.INSERT)
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common operations."""
        # Ctrl+C for copy results
        self.root.bind("<Control-c>", lambda e: self.copy_results_if_focused())
        # Ctrl+S for save results
        self.root.bind("<Control-s>", lambda e: self.save_results())
        # Ctrl+A for select all in results
        self.results_text.bind("<Control-a>", lambda e: self.select_all_results())
        # F5 for run plugin
        self.root.bind("<F5>", lambda e: self.run_plugin())
        # Ctrl+L for load test files
        self.root.bind("<Control-l>", lambda e: self.load_test_files())
        # Ctrl+R for clear results
        self.root.bind("<Control-r>", lambda e: self.clear_results())
        # Escape to clear results
        self.root.bind("<Escape>", lambda e: self.clear_results())
    
    def copy_results_if_focused(self):
        """Copy results if the results text area has focus, otherwise do nothing."""
        focused_widget = self.root.focus_get()
        if focused_widget == self.results_text:
            # Check if there's a selection first
            try:
                if self.results_text.tag_ranges(tk.SEL):
                    self.copy_selection()
                else:
                    self.copy_results()
            except tk.TclError:
                self.copy_results()
    
    def show_shortcuts_help(self):
        """Show keyboard shortcuts help dialog."""
        shortcuts_text = """Keyboard Shortcuts:

File Operations:
  Ctrl+L          Load Test Files
  Ctrl+S          Save Results
  Alt+F4          Exit

Edit Operations:
  Ctrl+C          Copy Results (or Selection if text is selected)
  Ctrl+A          Select All Results
  Ctrl+R          Clear Results

Plugin Operations:
  F5              Run Plugin
  Esc             Clear Results

Mouse Operations:
  Right-click     Context menu in Results area
"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def show_plugins_help(self):
        """Show information about available plugins."""
        if not self.plugins:
            messagebox.showinfo("Plugins", "No plugins are currently loaded.")
            return
        
        help_text = "Available Plugins:\n\n"
        for name, plugin_info in self.plugins.items():
            help_text += f"• {name}\n"
            help_text += f"  {plugin_info['description']}\n\n"
        
        help_text += "Usage Tips:\n"
        help_text += "• Use 'Load Test Files' to get sample files for testing\n"
        help_text += "• Select either a single file or a directory (not both)\n"
        help_text += "• Check 'Recursive' to process subdirectories\n"
        help_text += "• Current plugins run in automatic mode\n"
        help_text += "• Interactive modes planned for future versions"
        
        messagebox.showinfo("About Plugins", help_text)
    
    def show_about(self):
        """Show about dialog."""
        about_text = """AsciiDoc DITA Toolkit GUI
Version 0.1.9b2

A graphical interface for processing AsciiDoc files 
for DITA publishing workflows.

Features:
• Plugin-based architecture
• Visual configuration
• Real-time results display
• Copy and save functionality
• Keyboard shortcuts
• Test file generation

GitHub: github.com/rolfedh/asciidoc-dita-toolkit
PyPI: pypi.org/project/asciidoc-dita-toolkit

© 2025 - MIT License"""
        
        messagebox.showinfo("About AsciiDoc DITA Toolkit", about_text)

    def log(self, message):
        """Add a message to the results area."""
        def _log():
            self.results_text.insert(tk.END, str(message) + "\n")
            self.results_text.see(tk.END)
            self.root.update_idletasks()
        
        # Ensure we're on the main thread
        if threading.current_thread() == threading.main_thread():
            _log()
        else:
            self.root.after(0, _log)
def main():
    """Entry point for GUI application."""
    try:
        app = ToolkitGUI()
        app.run()
    except Exception as e:
        print(f"Error starting GUI: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

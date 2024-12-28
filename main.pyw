#####################################
# HTMLeditor v1.0.5 - Source
#####################################


#####################################
# Import necessary libraries
#####################################
win = False  # Windows flag is set to false

try:
    from tkinter import *
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import Toplevel, Text, WORD, END, Button
    import tkinter.font as tkfont
    from tkinter import ttk
    import re
    import sys
    import os
    import webbrowser

    if os.name == "nt":  # If system is win32, import ctypes and set flag to true
        import ctypes

        win = True

except Exception as e:
    print(f"Error importing modules: {e}")
    try:
        from tkinter import messagebox

        messagebox.showerror("Error", f"Error importing modules: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error importing modules: {e}")
        sys.exit(1)

try:
    from PIL import Image, ImageTk  # Try to import Pillow modules
    pillow_imported = True
except ImportError:
    pillow_imported = False


#####################################
# Set up appId
#####################################
if win:  # If win flag true, set up id
    appid = "tkdev.htmleditor.he.1-0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)


#####################################
# Main class
#####################################


class HTMLEditor:

    #####################################
    # Init tkinter, set up main window
    #####################################
    def init():
        "Starter function of the editor."
        root = Tk()
        editor = HTMLEditor(root)
        root.protocol("WM_DELETE_WINDOW", editor.confirm_exit)  # Bind close event
        root.mainloop()

    def __init__(self, root):
        "Main init function of the editor"
        self.root = root
        self.root.title(f"HTML Editor - Untitled Document")  # Default
        self.root.geometry("800x600")
        self.root.config(bg="#2B2B2B")
        self.root.resizable(True, True)
        self.mode = "dark"  # Default
        self.unsaved_changes = False  # Track changes
        self.safe_mode = False  # Track if safe mode is enabled
        self.auto_save_enabled = False  # Flag for auto-save status
        self.current_file_path = None  # Initialize current_file_path
        self.set_icon()  # Init icon function

        #####################################
        # Bind keys on functions
        #####################################

        self.root.bind(
            "<Control-s>", lambda event: self.save_changes()
        )  # CTRL_S         >   Save
        self.root.bind(
            "<Control-S>", lambda event: self.save_document()
        )  # CTRL_SHIFT_S   >   Save as
        self.root.bind(
            "<Control-n>", lambda event: self.new_document()
        )  # CTRL_N         >   New Document
        self.root.bind(
            "<Control-r>", lambda event: self.open_document_in_browser()
        )  # CTRL_R         >   "Run" Document
        self.root.bind(
            "<Control-o>", lambda event: self.open_document()
        )  # CTRL_O         >   Open Document
        self.root.bind(
            "<Control-u>", lambda event: self.change_zoom()
        )  # CTRL_U         >   Zoom window
        self.root.bind(
            "<Control-plus>", lambda event: self.increase_font_size()
        )  # CTRL_+         >   Zoom +
        self.root.bind(
            "<Control-minus>", lambda event: self.decrease_font_size()
        )  # CTRL_-         >   Zoom -
        self.root.bind(
            "<Control-f>", lambda event: self.find_replace()
        )  # CTRL_F         >   Find and Replace

        #####################################
        # Init widgets, set up text area
        #####################################

        self.menu_area = Frame(self.root, width=100, height=50, bg="#4d4d4d")
        self.menu_area.pack(side=TOP)

        self.infoButton = Button(
            self.menu_area,
            width=17,
            height=2,
            text="HTML Editor 1.0",
            bg="#ffff00",
            fg="#000000",
            command=self.info_window,
        )
        self.infoButton.pack(side=LEFT)
        self.newButton = Button(
            self.menu_area,
            width=10,
            height=2,
            text="New",
            bg="#ffcc00",
            fg="#000000",
            command=self.new_document,
        )
        self.newButton.pack(side=LEFT)
        self.saveAsButton = Button(
            self.menu_area,
            width=10,
            height=2,
            text="Save as",
            bg="#3366cc",
            fg="#f0f0f0",
            command=self.save_document,
        )
        self.saveAsButton.pack(side=LEFT)
        self.saveButton = Button(
            self.menu_area,
            width=10,
            height=2,
            text="Save",
            bg="#3366cc",
            fg="#f0f0f0",
            command=self.save_changes,
        )
        self.saveButton.pack(side=LEFT)
        self.openButton = Button(
            self.menu_area,
            width=10,
            height=2,
            text="Open",
            bg="#ff0066",
            fg="#f0f0f0",
            command=self.open_document,
        )
        self.openButton.pack(side=LEFT)
        self.runButton = Button(
            self.menu_area,
            width=10,
            height=2,
            text="Run",
            bg="#ff6600",
            command=self.open_document_in_browser,
        )
        self.runButton.pack(side=LEFT)
        self.viewButton = Button(
            self.menu_area,
            width=10,
            height=2,
            text="Zoom",
            bg="#339933",
            command=self.change_zoom,
        )
        self.viewButton.pack(side=LEFT)
        self.frButton = Button(
            self.menu_area,
            width=10,
            height=2,
            text="Find/Replace",
            bg="#ff33cc",
            command=self.find_replace,
        )
        self.frButton.pack(side=LEFT)
        self.settingsbutton = Button(
            self.menu_area,
            width=10,
            height=2,
            text="Settings",
            bg="#4d4d4d",
            fg="#ffffff",
            command=self.settings_window,
        )
        self.settingsbutton.pack(side=LEFT)

        self.text_area = Text(
            self.root,
            width=100,
            height=50,
            font=("Consolas", 13),
            bg="#333333",
            fg="#f0f0f0",
            insertbackground="#f0f0f0",
            undo=True,
            autoseparators=True,
            wrap=WORD,
        )
        self.text_area.pack(fill=BOTH, expand=True)
        font = tkfont.Font(font=self.text_area["font"])
        tab_size = font.measure("       ")  # Edit this to change tab size to your needs
        self.text_area.config(tabs=tab_size)
        self.text_area.bind("<<Modified>>", self.on_text_change)  # Track changes

        self.update_syntax_highlighting()  # Init syntax highlighting
        self.auto_save()
        
    def set_icon(self):
        """Sets the application icon."""
        if pillow_imported:
            try:
                icon = Image.open("favicon.ico")
                icon = ImageTk.PhotoImage(icon)
                self.root.iconphoto(True, icon)
            except Exception as e:
                print(f"Error setting icon: {e}")

    #####################################
    # Highlight syntax
    #####################################

    def update_syntax_highlighting(self):
        "Highlights HTML, CSS and JS keywords and tags in the code."
        # Clear previous tags
        self.text_area.tag_remove("html_tag", "1.0", END)
        self.text_area.tag_remove("css_class", "1.0", END)
        self.text_area.tag_remove("css_property", "1.0", END)
        self.text_area.tag_remove("javascript_function", "1.0", END)
        self.text_area.tag_remove("javascript_variable", "1.0", END)
        self.text_area.tag_remove("javascript_keyword", "1.0", END)
        self.text_area.tag_remove("string_literal", "1.0", END)
        self.text_area.tag_remove("html_comment", "1.0", END)
        self.text_area.tag_remove("js_comment", "1.0", END)
        self.text_area.tag_remove("integer", "1.0", END)
        self.text_area.tag_remove("px_value", "1.0", END)

        # Get content of text
        content = self.text_area.get("1.0", END)

        # regex patterns for HTML tags, CSS styles, JavaScript code, string literals, and HTML comments
        html_tag_pattern = r"</?[\w\s=\"\'\-\/]*[^<>]*\/?>"
        html_comment_pattern = r"<!--.*?-->"  # Matches HTML comments

        # CSS patterns
        css_class_pattern = r"\.[\w-]+"  # Matches CSS classes
        css_property_pattern = r"[\w-]+(?=\s*:)"  # Matches CSS properties

        # JavaScript patterns
        javascript_function_pattern = r"\b\w+(?=\s*\()"
        javascript_variable_pattern = r"\b(var|let|const)\s+(\w+)"
        javascript_keyword_pattern = r"(?<![a-zA-Z0-9_])\b(var|let|const|function|if|else|for|while|return|switch|case|break|continue|try|catch|finally|async|await|import|export|class|extends|super|this|new|delete|instanceof|typeof|void|with|do|in|of|default|static|get|set|yield|throw|true|false|null|undefined)\b(?![a-zA-Z0-9_])"

        # String literal pattern
        string_literal_pattern = (
            r'(["\'])(?:(?=(\\?))\2.)*?\1'  # Matches strings in double or single quotes
        )

        # Integer pattern (not in a string and not in an HTML tag)
        integer_pattern = r'(?<![<"\'])\b\d+\b(?![>\'"])'  # Matches integers

        # px value pattern (not in a string and not in an HTML tag)
        px_value_pattern = (
            r'(?<![<"\'])\b\d+px\b(?![>\'"])'  # Matches numerals followed by 'px'
        )

        # HTML tags
        for match in re.finditer(html_tag_pattern, content):
            self.text_area.tag_add(
                "html_tag", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars"
            )

        # HTML comments
        for match in re.finditer(html_comment_pattern, content):
            self.text_area.tag_add(
                "html_comment",
                f"1.0 + {match.start()} chars",
                f"1.0 + {match.end()} chars",
            )

        # JavaScript comments
        for match in re.finditer(r"//.*?$", content, re.MULTILINE):
            start_index = match.start()
            if (
                not content[max(0, start_index - 7) : start_index]
                .strip()
                .endswith(("http:", "https:"))
            ):
                self.text_area.tag_add(
                    "js_comment",
                    f"1.0 + {match.start()} chars",
                    f"1.0 + {match.end()} chars",
                )

        # CSS classes
        for match in re.finditer(css_class_pattern, content):
            self.text_area.tag_add(
                "css_class",
                f"1.0 + {match.start()} chars",
                f"1.0 + {match.end()} chars",
            )

        # CSS properties
        for match in re.finditer(css_property_pattern, content):
            self.text_area.tag_add(
                "css_property",
                f"1.0 + {match.start()} chars",
                f"1.0 + {match.end()} chars",
            )

        # JavaScript functions
        for match in re.finditer(javascript_function_pattern, content):
            self.text_area.tag_add(
                "javascript_function",
                f"1.0 + {match.start()} chars",
                f"1.0 + {match.end()} chars",
            )

        # JavaScript variables
        for match in re.finditer(javascript_variable_pattern, content):
            self.text_area.tag_add(
                "javascript_variable",
                f"1.0 + {match.start(2)} chars",
                f"1.0 + {match.end(2)} chars",
            )

        # JavaScript keywords
        for match in re.finditer(javascript_keyword_pattern, content):
            self.text_area.tag_add(
                "javascript_keyword",
                f"1.0 + {match.start()} chars",
                f"1.0 + {match.end()} chars",
            )

        # String literals
        for match in re.finditer(string_literal_pattern, content):
            self.text_area.tag_add(
                "string_literal",
                f"1.0 + {match.start()} chars",
                f"1.0 + {match.end()} chars",
            )

        # Integers
        for match in re.finditer(integer_pattern, content):
            self.text_area.tag_add(
                "integer",
                f"1.0 + {match.start()} chars",
                f"1.0 + {match.end()} chars",
            )

        # px values
        for match in re.finditer(px_value_pattern, content):
            self.text_area.tag_add(
                "px_value",
                f"1.0 + {match.start()} chars",
                f"1.0 + {match.end()} chars",
            )

        # Configure tag colors (Edit this to change colors to your needs)
        if self.mode == "dark":
            self.text_area.tag_config("html_tag", foreground="#66e0ff")  # Light blue
            self.text_area.tag_config(
                "html_comment", foreground="#009900"
            )  # Dark green
            self.text_area.tag_config("js_comment", foreground="#009900")  # Dark green
            self.text_area.tag_config("css_class", foreground="#ff00ff")  # Pink
            self.text_area.tag_config(
                "css_property", foreground="#00ffaa"
            )  # Light green
            self.text_area.tag_config(
                "javascript_function", foreground="#ffcc00"
            )  # Yellow orange
            self.text_area.tag_config(
                "javascript_variable", foreground="#00ff00"
            )  # Lime
            self.text_area.tag_config("javascript_keyword", foreground="#ff0066")  # Red
            self.text_area.tag_config("string_literal", foreground="#ff9933")  # Orange
            self.text_area.tag_config("integer", foreground="#ffcc00")  # Yellow orange
            self.text_area.tag_config("px_value", foreground="#ffcc00")  # Yellow orange

        if self.mode == "light":
            self.text_area.tag_config("html_tag", foreground="#003399")  # Dark blue
            self.text_area.tag_config("html_comment", foreground="#008000")  # Green
            self.text_area.tag_config("js_comment", foreground="#008000")  # Green
            self.text_area.tag_config("css_class", foreground="#800080")  # Purple
            self.text_area.tag_config("css_property", foreground="#003399")  # Dark blue
            self.text_area.tag_config(
                "javascript_function", foreground="#ff8c00"
            )  # Dark orange
            self.text_area.tag_config(
                "javascript_variable", foreground="#0000ff"
            )  # Blue
            self.text_area.tag_config("javascript_keyword", foreground="#ff0000")  # Red
            self.text_area.tag_config("string_literal", foreground="#cc6600")  # Brown
            self.text_area.tag_config("integer", foreground="#0000ff")  # Blue
            self.text_area.tag_config("px_value", foreground="#0000ff")  # Blue

        if self.mode == "high_contrast":
            self.text_area.tag_config("html_tag", foreground="#66e0ff")  # Light
            self.text_area.tag_config(
                "html_comment", foreground="#009900"
            )  # Dark green
            self.text_area.tag_config("js_comment", foreground="#009900")  # Dark green
            self.text_area.tag_config("css_class", foreground="#ff3399")  # Pink
            self.text_area.tag_config(
                "css_property", foreground="#00ffaa"
            )  # Light green
            self.text_area.tag_config(
                "javascript_function", foreground="#ffcc00"
            )  # Yellow orange
            self.text_area.tag_config(
                "javascript_variable", foreground="#00ff00"
            )  # Lime
            self.text_area.tag_config("javascript_keyword", foreground="#ff0066")  # Red
            self.text_area.tag_config("string_literal", foreground="#ff9933")  # Orange
            self.text_area.tag_config("integer", foreground="#ffcc00")  # Yellow orange
            self.text_area.tag_config("px_value", foreground="#ffcc00")  # Yellow orange

        if self.mode == "black_white":
            self.text_area.tag_config("html_tag", foreground="#666666")
            self.text_area.tag_config("html_comment", foreground="#000000")
            self.text_area.tag_config("js_comment", foreground="#000000")
            self.text_area.tag_config("css_class", foreground="#666666")
            self.text_area.tag_config("css_property", foreground="#666666")
            self.text_area.tag_config("javascript_function", foreground="#666666")
            self.text_area.tag_config("javascript_variable", foreground="#666666")
            self.text_area.tag_config("javascript_keyword", foreground="#666666")
            self.text_area.tag_config("string_literal", foreground="#000000")
            self.text_area.tag_config("integer", foreground="#000000")
            self.text_area.tag_config("px_value", foreground="#000000")

        # Schedule next update
        self.root.after(100, self.update_syntax_highlighting)

    #####################################
    # Save, open, autosave functions, title bar update
    #####################################

    def new_document(self):
        "Creates a new instance of HTMLEditor for a new window"
        new_root = Tk()  # Create a new root window
        new_editor = HTMLEditor(new_root)  # Initialize the HTMLEditor with the new root
        new_editor.set_icon()  # Set the icon for the new window
        new_root.mainloop()  # Start the main loop for the new window

    def toggle_safe_mode(self):
        """Toggles safe mode on and off."""
        self.safe_mode = not self.safe_mode  # Toggle the safe mode flag
        self.text_area.config(
            state=DISABLED if self.safe_mode else NORMAL
        )  # Enable/disable editing
        if self.safe_mode:
            messagebox.showinfo(
                "Safe Mode", "Safe mode is now enabled. You cannot edit the document."
            )
        else:
            messagebox.showinfo(
                "Safe Mode", "Safe mode is now disabled. You can edit the document."
            )

    def on_text_change(self, event):
        """Gets called if the text area is modified. Calls update functions."""
        self.unsaved_changes = True
        self.text_area.edit_modified(False)  # Reset the modified flag
        self.update_title()  # Update the title to reflect unsaved changes

    def save_document(self):
        """Saves the current document to a new filepath"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[
                    ("HTML Sites", "*.html"),
                    ("Cascading Style Sheets", "*.css"),
                    ("JavaScript Scripts", "*.js"),
                    ("Standard Text Files", "*.txt"),
                    ("All Files", "*.*"),
                ],
                initialfile="untitled.html",
            )
            if file_path:
                with open(file_path, "w") as file:
                    file.write(self.text_area.get("1.0", "end-1c"))
                    self.current_file_path = file_path
                    self.unsaved_changes = False  # Reset unsaved changes flag
                    self.update_title()  # Update title
            else:
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save document: {str(e)}")

    def save_changes(self):
        """Saves the current document to a file"""
        try:
            with open(self.current_file_path, "w") as file:
                file.write(self.text_area.get("1.0", "end-1c"))
                self.unsaved_changes = False  # Reset unsaved changes flag
                self.update_title()  # Update title
        except:
            self.save_document()

    def open_document(self):
        """Opens a document from a file"""
        try:
            file_path = filedialog.askopenfilename(
                defaultextension=".html",
                filetypes=[
                    ("HTML Sites", "*.html"),
                    ("Cascading Style Sheets", "*.css"),
                    ("JavaScript Scripts", "*.js"),
                    ("Standard Text Files", "*.txt"),
                    ("All Files", "*.*"),
                ],
            )
            if file_path:
                with open(file_path, "r") as file:
                    text = file.read()
                    self.file_name = os.path.basename(file_path)
                    self.text_area.delete("1.0", END)
                    self.text_area.insert("1.0", text)
                    self.current_file_path = file_path
                    self.unsaved_changes = False  # Reset unsaved changes flag
                    self.update_title()  # Update title
                    self.text_area.config(
                        state=DISABLED if self.safe_mode else NORMAL
                    )  # Disable editing if in safe mode
            else:
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open document: {str(e)}")

    def update_title(self):
        """Updates the title of the window based on the current file path and unsaved changes status"""
        if self.current_file_path:  # Check if current_file_path is set
            if self.unsaved_changes:
                self.root.title(
                    f"HTML Editor - {os.path.basename(self.current_file_path)}*"
                )
            else:
                self.root.title(
                    f"HTML Editor - {os.path.basename(self.current_file_path)}"
                )
        else:
            self.root.title(
                "HTML Editor - Untitled Document"
            )  # Default title if no file is opened

    def auto_save(self):
        """Saves the current document automatically at regular intervals if enabled."""
        if self.auto_save_enabled:  # Check if auto-save is enabled
            self.save_changes()  # Call the save_changes method to save the document
        self.root.after(10000, self.auto_save)  # Schedule next auto-save

    def toggle_auto_save(self):
        """Toggles auto-save on and off."""
        self.auto_save_enabled = not self.auto_save_enabled  # Toggle the flag
        status = "enabled" if self.auto_save_enabled else "disabled"
        messagebox.showinfo("Auto Save", f"Auto save is now {status}.")
    #####################################
    # Open file in browser
    #####################################

    def open_document_in_browser(self):
        """Opens the document in a new tab, automatically reloads page when saved"""
        try:
            if self.current_file_path:  # Use the current file path
                webbrowser.open(self.current_file_path)
            else:
                messagebox.showerror("Error", "No file selected")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open document: {str(e)}")

    #####################################
    # Font size (zoom)
    #####################################

    def change_zoom(self):
        """Creates a window to change the font size (zoom)"""
        top = Toplevel(self.root)
        top.geometry("300x100")
        top.title("Change Font Size")
        Label(top, text="Font Size:").pack()
        self.slider = Scale(
            top,
            from_=1,
            to=100,
            length=300,
            orient=HORIZONTAL,
            command=self.update_zoom,
        )
        self.slider.set(13)
        self.slider.pack()
        Button(top, text="Close", command=top.destroy).pack()

    def update_zoom(self, value):
        """Updates the font size (zoom) of the text area"""
        self.text_area.config(font=("Consolas", int(value)))

    def increase_font_size(self):
        """Increases the font size (zoom) of the text area by 1 point"""
        current_font = tkfont.Font(font=self.text_area.cget("font"))
        new_size = current_font.actual("size") + 1
        self.text_area.config(font=("Consolas", new_size))

    def decrease_font_size(self):
        """Decreases the font size (zoom) of the text area by 1 point"""
        current_font = tkfont.Font(font=self.text_area.cget("font"))
        new_size = max(
            1, current_font.actual("size") - 1
        )  # Prevents font size from going below 1
        self.text_area.config(font=("Consolas", new_size))

    #####################################
    # Information, settings window
    #####################################

    def info_window(self):
        """Creates a window with information about the application"""
        top = Toplevel(self.root)
        top.title("About")
        top.geometry("300x150")
        top.config(bg="#333333")
        top.resizable(False, False)
        # Load and resize the logo
        logo = Image.open("logo.png")
        logo = logo.resize((50, 50))  # Resize to 100x100 pixels
        logo = ImageTk.PhotoImage(logo)

        logo_label = Label(top, image=logo)
        logo_label.image = logo  # Keep a reference to avoid garbage collection
        logo_label.pack()

        Label(top, text="HTML Editor", fg="#ffffff", bg="#333333").pack()
        Label(top, text="Version 1.0", fg="#ffffff", bg="#333333").pack()
        Label(top, text="Copyright 2024", fg="#ffffff", bg="#333333").pack()
        Label(top, text="Author: Tobias Kisling", fg="#ffffff", bg="#333333").pack()

    def license_window(self):
        """Creates a toplevel window with the license"""
        top = Toplevel(self.root)
        top.title("License")
        top.geometry("600x600")
        top.config(bg="#333333")
        top.resizable(False, False)
        Label(
            top,
            font=("TkDefaultFont", 20),
            text="MIT License",
            fg="#ffffff",
            bg="#333333",
        ).pack()
        Label(
            top,
            text="Copyright (c) 2024 Tobias Kisling (hasderhi)",
            fg="#ffffff",
            bg="#333333",
        ).pack()
        Label(
            top,
            fg="#ffffff",
            bg="#333333",
            text="Permission is hereby granted, free of charge, \nto any person obtaining a copy of this software and associated\ndocumentation files (the 'Software'),\nto deal in the Software without restriction, including without limitation the rights to use,\ncopy, modify, merge, publish, distribute, sublicense,\nand/or sell copies of the Software, and to permit persons to\nwhom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be\nincluded in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED 'AS IS',\nWITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,\nINCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.\nIN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,\nDAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,\nARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR\nTHE USE OR OTHER DEALINGS IN THE SOFTWARE.\n\nHTML5 Logo by <https://www.w3.org/>",
        ).pack()

    def settings_window(self):
        """Creates a toplevel window with settings"""
        top = Toplevel(self.root)
        top.title("Settings")
        top.geometry("600x600")
        top.config(bg="#333333")
        top.resizable(False, False)

        # Create a canvas
        canvas = Canvas(top, bg="#333333")
        scrollable_frame = Frame(canvas, bg="#333333")

        # Configure the canvas
        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Pack the canvas
        canvas.pack(side="left", fill="both", expand=True)

        # Add mouse wheel scrolling
        def on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # For Windows
        canvas.bind_all(
            "<Button-4>", lambda event: canvas.yview_scroll(-1, "units")
        )  # For Linux
        canvas.bind_all(
            "<Button-5>", lambda event: canvas.yview_scroll(1, "units")
        )  # For Linux

        # Add your settings content here
        Label(
            scrollable_frame,
            text="Settings",
            font=("TkDefaultFont", 20),
            fg="#ffffff",
            bg="#333333",
        ).pack(pady=10, anchor="center")
        ttk.Separator(scrollable_frame, orient="horizontal").pack(
            fill="x", padx=10, pady=10
        )
        Label(
            scrollable_frame,
            text="Appearance",
            font=("TkDefaultFont", 15),
            fg="#ffffff",
            bg="#333333",
        ).pack(anchor="center")

        button_frame1 = Frame(scrollable_frame, width=200, height=20, bg="#333333")
        button_frame1.pack(pady=10)

        Button(
            button_frame1,
            text="Light mode",
            font=("TkDefaultFont"),
            fg="#ffffff",
            bg="#333333",
            command=self.change_to_light_mode,
        ).pack(side=LEFT, padx=5)
        Button(
            button_frame1,
            text="Dark mode",
            font=("TkDefaultFont"),
            fg="#ffffff",
            bg="#333333",
            command=self.change_to_dark_mode,
        ).pack(side=LEFT, padx=5)
        Button(
            button_frame1,
            text="High contrast mode",
            font=("TkDefaultFont"),
            fg="#ffffff",
            bg="#333333",
            command=self.change_to_high_contrast_mode,
        ).pack(side=LEFT, padx=5)
        Button(
            button_frame1,
            text="Black/White mode",
            font=("TkDefaultFont"),
            fg="#ffffff",
            bg="#333333",
            command=self.change_to_black_white_mode,
        ).pack(side=LEFT, padx=5)

        ttk.Separator(scrollable_frame, orient="horizontal").pack(
            fill="x", padx=10, pady=10
        )
        Label(
            scrollable_frame,
            text="Safe Mode",
            font=("TkDefaultFont", 15),
            fg="#ffffff",
            bg="#333333",
        ).pack(anchor="center")
        Label(
            scrollable_frame,
            text="When safe mode is activated, the current document\ncannot be edited. This mode is intended for safe code browsing.\nPlease note that when this mode is activated, other documents cannot be opened\nuntil safe mode is disabled again.",
            font=("TkDefaultFont"),
            fg="#ffffff",
            bg="#333333",
        ).pack(anchor="center")

        button_frame2 = Frame(scrollable_frame, width=200, height=20, bg="#333333")
        button_frame2.pack(pady=10)
        Button(
            button_frame2,
            text="Toggle Safe Mode",
            bg="#ffcc00",
            fg="#000000",
            command=self.toggle_safe_mode,
        ).pack(side=LEFT, padx=5)

        ttk.Separator(scrollable_frame, orient="horizontal").pack(
            fill="x", padx=10, pady=10
        )
        Label(
            scrollable_frame,
            text="Auto Save",
            font=("TkDefaultFont", 15),
            fg="#ffffff",
            bg="#333333",
        ).pack(anchor="center")
        Label(
            scrollable_frame,
            text=" When auto save is activated, the current document\nis saved every 10 seconds. Please note that the\n auto save can only be disabled by restarting.\n The developer will fix this soon!",
            font=("TkDefaultFont"),
            fg="#ffffff",
            bg="#333333",
        ).pack(anchor="center")

        button_frame3 = Frame(scrollable_frame, width=200, height=20, bg="#333333")
        button_frame3.pack(pady=10)
        Button(scrollable_frame, text="Toggle Auto Save", bg="#0099cc", fg="#f0f0f0", command=self.toggle_auto_save).pack(pady=10)

        ttk.Separator(scrollable_frame, orient="horizontal").pack(
            fill="x", padx=10, pady=10
        )
        Label(
            scrollable_frame,
            text="About and licensing",
            font=("TkDefaultFont", 15),
            fg="#ffffff",
            bg="#333333",
        ).pack(anchor="center")

        button_frame4 = Frame(scrollable_frame, width=200, height=20, bg="#333333")
        button_frame4.pack(pady=10)
        Button(
            button_frame4,
            text="About HTML editor",
            font=("TkDefaultFont"),
            fg="#ffffff",
            bg="#333333",
            command=self.info_window,
        ).pack(side=LEFT, padx=5)
        Button(
            button_frame4,
            text="Show license",
            font=("TkDefaultFont"),
            fg="#ffffff",
            bg="#333333",
            command=self.license_window,
        ).pack(side=LEFT, padx=5)

    #####################################
    # Find/Replace
    #####################################

    def find_replace(self):
        """Find and replace engine for HTMLEditor"""
        find_replace_window = Toplevel(self.root)
        find_replace_window.title("Find and Replace")
        find_replace_window.geometry("400x200")
        find_replace_window.config(bg="#333333")

        # Create labels and entry fields
        Label(find_replace_window, text="Find:", bg="#333333", fg="#ffffff").pack(
            pady=10
        )
        find_entry = Entry(find_replace_window, width=40)
        find_entry.pack(pady=5)

        Label(
            find_replace_window, text="Replace with:", bg="#333333", fg="#ffffff"
        ).pack(pady=10)
        replace_entry = Entry(find_replace_window, width=40)
        replace_entry.pack(pady=5)

        # Function to perform find and replace
        def perform_find_replace():
            find_text = find_entry.get()
            replace_text = replace_entry.get()

            # Check if the find_text is empty
            if not find_text:
                messagebox.showwarning("Input Error", "Please enter text to find.")
                return  # Exit the function if no text is provided

            content = self.text_area.get("1.0", END)

            # Clear previous highlights
            self.text_area.tag_remove("highlight", "1.0", END)

            # Search for the text and highlight matches
            start_index = 0
            matches = 0

            while True:
                start_index = content.find(find_text, start_index)
                if start_index == -1:
                    break
                matches += 1
                end_index = start_index + len(find_text)
                self.text_area.tag_add(
                    "highlight",
                    f"1.0 + {start_index} chars",
                    f"1.0 + {end_index} chars",
                )
                start_index += len(find_text)  # Move past the last found match

            # Update the text area to reflect the highlights
            self.text_area.tag_config(
                "highlight", background="#ffcc00"
            )  # Highlight color
            self.text_area.mark_set("insert", "1.0")  # Reset cursor position
            self.text_area.see("1.0")  # Scroll to the top

            # Show number of matches found
            messagebox.showinfo("Find Results", f"Found {matches} match(es).")

            # Replace text if any matches were found
            if matches > 0 and replace_text:
                new_content = content.replace(find_text, replace_text)
                self.text_area.delete("1.0", END)
                self.text_area.insert("1.0", new_content)

        # Function to clear highlights when the window is closed
        def clear_highlights():
            self.text_area.tag_remove("highlight", "1.0", END)

        # Bind the clear_highlights function to the window's destroy event
        find_replace_window.protocol(
            "WM_DELETE_WINDOW",
            lambda: (clear_highlights(), find_replace_window.destroy()),
        )

        # Create a button to execute the find and replace
        replace_button = Button(
            find_replace_window,
            text="Find and Replace",
            command=perform_find_replace,
            bg="#0099cc",
            fg="#ffffff",
        )
        replace_button.pack(pady=20)

        # Create a button to close the window
        close_button = Button(
            find_replace_window,
            text="Close",
            command=lambda: (clear_highlights(), find_replace_window.destroy()),
            bg="#ff0066",
            fg="#ffffff",
        )
        close_button.pack(pady=5)

    #####################################
    # Appearance modes
    #####################################

    def change_to_light_mode(self):
        """Changes to light mode"""
        self.mode = "light"  # Set mode
        # Change root window bg/fg
        self.root.config(bg="#ffffff")
        self.text_area.config(bg="#ffffff", fg="#000000", insertbackground="#000000")

        # Menu area button colors
        self.infoButton.config(bg="#ffff00", fg="#4d4d4d")
        self.autoSaveEnableButton.config(bg="#0099cc", fg="#f0f0f0")
        self.saveAsButton.config(bg="#3366cc", fg="#f0f0f0")
        self.saveButton.config(bg="#3366cc", fg="#f0f0f0")
        self.openButton.config(bg="#ff0066", fg="#f0f0f0")
        self.runButton.config(bg="#ff6600")
        self.viewButton.config(bg="#339933")
        self.frButton.config(bg="#ff33cc")
        self.settingsbutton.config(bg="#333333", fg="#f0f0f0")

    def change_to_dark_mode(self):
        """Changes to dark mode"""
        self.mode = "dark"  # Set mode
        # Change root window bg/fg
        self.root.config(bg="#2B2B2B")
        self.text_area.config(bg="#333333", fg="#f0f0f0", insertbackground="#f0f0f0")

        # Menu area button colors
        self.infoButton.config(bg="#ffff00", fg="#4d4d4d")
        self.autoSaveEnableButton.config(bg="#0099cc", fg="#f0f0f0")
        self.saveAsButton.config(bg="#3366cc", fg="#f0f0f0")
        self.saveButton.config(bg="#3366cc", fg="#f0f0f0")
        self.openButton.config(bg="#ff0066", fg="#f0f0f0")
        self.runButton.config(bg="#ff6600")
        self.viewButton.config(bg="#339933")
        self.frButton.config(bg="#ff33cc")
        self.settingsbutton.config(bg="#333333", fg="#f0f0f0")

    def change_to_high_contrast_mode(self):
        """Changes to high contrast mode"""
        self.mode = "high_contrast"  # Set mode
        # Change root window bg/fg
        self.root.config(bg="#000000")
        self.text_area.config(bg="#000000", fg="#ffffff", insertbackground="#ffffff")

        # Menu area button colors
        self.infoButton.config(bg="#ffffff", fg="#000000")
        self.autoSaveEnableButton.config(bg="#0099cc", fg="#ffffff")
        self.saveAsButton.config(bg="#3366cc", fg="#ffffff")
        self.saveButton.config(bg="#3366cc", fg="#ffffff")
        self.openButton.config(bg="#ff0066", fg="#ffffff")
        self.runButton.config(bg="#ff6600")
        self.viewButton.config(bg="#00ff00")
        self.frButton.config(bg="#ff33cc")
        self.settingsbutton.config(bg="#333333", fg="#f0f0f0")

    def change_to_black_white_mode(self):
        """Changes to black and white mode"""
        self.mode = "black_white"  # Set mode
        # Change root window bg/fg
        self.root.config(bg="#ffffff")
        self.text_area.config(bg="#ffffff", fg="#000000", insertbackground="#000000")

        # Menu area button colors
        self.infoButton.config(bg="#ffffff", fg="#000000")
        self.autoSaveEnableButton.config(bg="#ffffff", fg="#000000")
        self.saveAsButton.config(bg="#ffffff", fg="#000000")
        self.saveButton.config(bg="#ffffff", fg="#000000")
        self.openButton.config(bg="#ffffff", fg="#000000")
        self.runButton.config(bg="#ffffff", fg="#000000")
        self.viewButton.config(bg="#ffffff", fg="#000000")
        self.frButton.config(bg="#ffffff", fg="#000000")
        self.settingsbutton.config(bg="#ffffff", fg="#000000")

    #####################################
    # Add exit confirmation method
    #####################################

    def confirm_exit(self):
        """Confirms exit of the application"""
        if self.unsaved_changes:  # Check if there are unsaved changes
            response = messagebox.askyesno(
                "Confirm Exit", "You have unsaved changes. Do you really want to exit?"
            )
            if response:  # If user confirms, exit the application
                self.root.destroy()
        else:
            self.root.destroy()  # Exit without confirmation if no unsaved changes


#####################################
# Init main class
#####################################

HTMLEditor.init()

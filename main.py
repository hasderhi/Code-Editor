#####################################
# Import necessary libraries
#####################################

win = False # Windows flag is set to false

try:
    from tkinter import *
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import Toplevel, Text, WORD, END, Button
    import tkinter.font as tkfont
    import re
    import sys
    import os
    import webbrowser
    if os.name == 'nt': # If system is win32, import ctypes and set flag to true
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
if win: # If win flag true, set up id
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
        root = Tk()
        HTMLEditor(root)
        root.mainloop()

    def __init__(self, root):
        self.root = root
        self.root.title("HTML Editor")
        self.root.geometry("800x600")
        self.root.config(bg="#2B2B2B")
        self.root.resizable(True, True)

        if pillow_imported:
            icon = Image.open("favicon.ico")
            icon = ImageTk.PhotoImage(icon)
            self.root.iconphoto(True, icon)

        #####################################
        # Init widgets, set up text area
        #####################################

        self.menu_area = Frame(self.root, width=100, height=50, bg="#4d4d4d")
        self.menu_area.pack(side=TOP)

        self.infoButton = Button(
            self.menu_area,
            width=20,
            height=2,
            text="HTML Editor 1.0",
            bg="#ffff00",
            fg="#000000",
            command=self.info_window,
        )
        self.infoButton.pack(side=LEFT)
        self.autoSaveEnableButton = Button(
            self.menu_area,
            width=15,
            height=2,
            text="Enable autosave",
            bg="#0099cc",
            fg="#f0f0f0",
            command=self.auto_save,
        )
        self.autoSaveEnableButton.pack(side=LEFT)
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
            command=self.change_font_size,
        )
        self.viewButton.pack(side=LEFT)

        self.text_area = Text(
            self.root,
            width=100,
            height=50,
            font=("Consolas", 17),
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

        self.update_syntax_highlighting()  # Init syntax highlighting

    #####################################
    # Highlight syntax
    #####################################

    def update_syntax_highlighting(self):
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
        string_literal_pattern = r'(["\'])(?:(?=(\\?))\2.)*?\1'  # Matches strings in double or single quotes

        # Integer pattern (not in a string and not in an HTML tag)
        integer_pattern = r'(?<![<"\'])\b\d+\b(?![>\'"])'  # Matches integers

        # px value pattern (not in a string and not in an HTML tag)
        px_value_pattern = r'(?<![<"\'])\b\d+px\b(?![>\'"])'  # Matches numerals followed by 'px'

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
            if not content[max(0, start_index - 7):start_index].strip().endswith(('http:', 'https:')):
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
        self.text_area.tag_config("html_tag", foreground="#66e0ff")                 # Light blue
        self.text_area.tag_config("html_comment", foreground="#006622")             # Dark green
        self.text_area.tag_config("js_comment", foreground="#006622")               # Dark green
        self.text_area.tag_config("css_class", foreground="#ff00ff")                # Pink
        self.text_area.tag_config("css_property", foreground="#00ffaa")             # Light green
        self.text_area.tag_config("javascript_function", foreground="#ffcc00")      # Yellow orange 
        self.text_area.tag_config("javascript_variable", foreground="#00ff00")      # Lime
        self.text_area.tag_config("javascript_keyword", foreground="#ff0066")       # Red
        self.text_area.tag_config("string_literal", foreground="#ff9933")           # Orange
        self.text_area.tag_config("integer", foreground="#ffcc00")                  # Yellow orange
        self.text_area.tag_config("px_value", foreground="#ffcc00")                 # Yellow orange

        # Schedule next update
        self.root.after(100, self.update_syntax_highlighting)

    #####################################
    # Save, open, autosave functions
    #####################################

    def save_document(self):
        # Save the current document to a file
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[
                    ("HTML sites", "*.html"),
                    ("Cascading Style Sheets", "*.css"),
                    ("JavaScript scripts", "*.js"),
                    ("Standard Text Files", "*.txt"),
                    ("All Files", "*.*"),
                ],
                initialfile="untitled.html",
            )
            if file_path:
                with open(file_path, "w") as file:
                    file.write(self.text_area.get("1.0", "end-1c"))
                    self.current_file_path = file_path
            else:
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save document: {str(e)}")

    def save_changes(self):
        # Save the current document to a file
        try:
            with open(self.current_file_path, "w") as file:
                file.write(self.text_area.get("1.0", "end-1c"))
        except:
            self.save_document()

    def open_document(self):
        try:
            file_path = filedialog.askopenfilename(
                defaultextension=".html",
                filetypes=[
                    ("HTML sites", "*.html"),
                    ("Cascading Style Sheets", "*.css"),
                    ("JavaScript scripts", "*.js"),
                    ("Standard Text Files", "*.txt"),
                    ("All Files", "*.*"),
                ],
            )
            if file_path:
                with open(file_path, "r") as file:
                    text = file.read()
                    self.file_name = os.path.basename(file_path)
                    self.text_area.delete("1.0", END)
                    # Insert the file contents into the text area
                    self.text_area.insert("1.0", text)
                    self.current_file_path = file_path
            else:
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open document: {str(e)}")

    def auto_save(self):
        self.save_changes()
        self.root.after(
            10000, self.auto_save
        )  # Save document every 10 seconds, edit this to change to your needs

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

    def change_font_size(self):
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
            command=self.update_font_size,
        )
        self.slider.set(17)
        self.slider.pack()
        Button(top, text="OK", command=top.destroy).pack()

    def update_font_size(self, value):
        self.text_area.config(font=("Consolas", int(value)))

    #####################################
    # Information window
    #####################################

    def info_window(self):
        top = Toplevel(self.root)
        top.title("About")
        top.geometry("300x100")
        top.config(bg="#333333")
        top.resizable(False, False)
        Label(top, text="HTML Editor", fg="#ffffff", bg="#333333").pack()
        Label(top, text="Version 1.0", fg="#ffffff", bg="#333333").pack()
        Label(top, text="Copyright 2024", fg="#ffffff", bg="#333333").pack()
        Label(top, text="Author: Tobias Kisling", fg="#ffffff", bg="#333333").pack()


#####################################
# Init main class
#####################################

HTMLEditor.init()

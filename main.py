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
        editor = HTMLEditor(root)
        root.protocol("WM_DELETE_WINDOW", editor.confirm_exit)  # Bind the close event
        root.mainloop()

    def __init__(self, root):
        self.root = root
        self.root.title(f"HTML Editor - Untitled Document")
        self.root.geometry("800x600")
        self.root.config(bg="#2B2B2B")
        self.root.resizable(True, True)
        self.unsaved_changes = False  # Track changes
        self.current_file_path = None  # Initialize current_file_path
        self.root.bind('<Control-s>', lambda event: self.save_changes())
        self.root.bind('<Control-S>', lambda event: self.save_document())
        self.root.bind('<Control-r>', lambda event: self.open_document_in_browser())
        self.root.bind('<Control-o>', lambda event: self.open_document())
        self.root.bind('<Control-u>', lambda event: self.change_font_size())
        self.root.bind('<Control-plus>', lambda event: self.increase_font_size())
        self.root.bind('<Control-minus>', lambda event: self.decrease_font_size())
        self.root.bind('<Control-f>', lambda event: self.find_replace())
        


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
        self.frButton = Button(
            self.menu_area,
            width=10,
            height=2,
            text="Find/Replace",
            bg="#ff33cc",
            command=self.find_replace,
        )
        self.frButton.pack(side=LEFT)

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
        self.text_area.bind("<<Modified>>", self.on_text_change)
        
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

    def on_text_change(self, event):
        self.unsaved_changes = True
        self.text_area.edit_modified(False)  # Reset the modified flag
        self.update_title()  # Update the title to reflect unsaved changes

    def save_document(self):
        # Save the current document to a file
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
        # Save the current document to a file
        try:
            with open(self.current_file_path, "w") as file:
                file.write(self.text_area.get("1.0", "end-1c"))
                self.unsaved_changes = False  # Reset unsaved changes flag
                self.update_title()  # Update title
        except:
            self.save_document()

    def open_document(self):
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
            else:
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open document: {str(e)}")



    def update_title(self):
        if self.current_file_path:  # Check if current_file_path is set
            if self.unsaved_changes:
                self.root.title(f"HTML Editor - {os.path.basename(self.current_file_path)}*")
            else:
                self.root.title(f"HTML Editor - {os.path.basename(self.current_file_path)}")
        else:
            self.root.title("HTML Editor - Untitled Document")  # Default title if no file is opened






    
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
        self.slider.set(13)
        self.slider.pack()
        Button(top, text="Close", command=top.destroy).pack()

    def update_font_size(self, value):
        self.text_area.config(font=("Consolas", int(value)))

    def increase_font_size(self):
        current_font = tkfont.Font(font=self.text_area.cget("font"))
        new_size = current_font.actual("size") + 1
        self.text_area.config(font=("Consolas", new_size))

    def decrease_font_size(self):
        current_font = tkfont.Font(font=self.text_area.cget("font"))
        new_size = max(1, current_font.actual("size") - 1)  # Prevents font size from going below 1
        self.text_area.config(font=("Consolas", new_size))



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

    def find_replace(self):
        # Create a Toplevel window for find and replace
        find_replace_window = Toplevel(self.root)
        find_replace_window.title("Find and Replace")
        find_replace_window.geometry("400x200")
        find_replace_window.config(bg="#333333")
        
        # Create labels and entry fields
        Label(find_replace_window, text="Find:", bg="#333333", fg="#ffffff").pack(pady=10)
        find_entry = Entry(find_replace_window, width=40)
        find_entry.pack(pady=5)

        Label(find_replace_window, text="Replace with:", bg="#333333", fg="#ffffff").pack(pady=10)
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
                self.text_area.tag_add("highlight", f"1.0 + {start_index} chars", f"1.0 + {end_index} chars")
                start_index += len(find_text)  # Move past the last found match

            # Update the text area to reflect the highlights
            self.text_area.tag_config("highlight", background="#ffcc00")  # Highlight color
            self.text_area.mark_set("insert", "1.0")  # Reset cursor position
            self.text_area.see("1.0")  # Scroll to the top

            # Show number of matches found
            messagebox.showinfo("Find Results", f"Found {matches} matches.")

            # Replace text if any matches were found
            if matches > 0 and replace_text:
                new_content = content.replace(find_text, replace_text)
                self.text_area.delete("1.0", END)
                self.text_area.insert("1.0", new_content)

        # Function to clear highlights when the window is closed
        def clear_highlights():
            self.text_area.tag_remove("highlight", "1.0", END)

        # Bind the clear_highlights function to the window's destroy event
        find_replace_window.protocol("WM_DELETE_WINDOW", lambda: (clear_highlights(), find_replace_window.destroy()))

        # Create a button to execute the find and replace
        replace_button = Button(find_replace_window, text="Find and Replace", command=perform_find_replace, bg="#0099cc", fg="#ffffff")
        replace_button.pack(pady=20)

        # Create a button to close the window
        close_button = Button(find_replace_window, text="Close", command=lambda: (clear_highlights(), find_replace_window.destroy()), bg="#ff0066", fg="#ffffff")
        close_button.pack(pady=5)


    #####################################
    # Add exit confirmation method
    #####################################

    def confirm_exit(self):
        if self.unsaved_changes:  # Check if there are unsaved changes
            response = messagebox.askyesno("Confirm Exit", "You have unsaved changes. Do you really want to exit?")
            if response:  # If user confirms, exit the application
                self.root.destroy()
        else:
            self.root.destroy()  # Exit without confirmation if no unsaved changes

#####################################
# Init main class
#####################################

HTMLEditor.init()

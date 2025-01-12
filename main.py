"""
# HTMLeditor v1.1.0 main module - Source

This is my HTML, CSS, JavaScript and Markdown editor written in Python. 
Even though it uses just one external library (Pillow for icons), 
it has some functions like syntax highlighting and tag completition 
for HTML, CSS, JavaScript and Markdown code, an autosave function and
a function to run the code with one click directly in the program.


"""

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
    import datetime
    import json

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
# Set up appId, create necessary directories
#####################################
if win:  # If win flag true, set up id
    appid = "tkdev.htmleditor.he.1-0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

try:
    if not os.path.isdir("internal"):
        os.makedirs("internal")
except Exception as e:
    print(f"Error creating internal directory: {e}")
    messagebox.showerror("Error", f"Error creating internal directory. {e}")
    sys.exit(1)
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

        root.config(cursor="watch")

        editor = HTMLEditor(root)
        root.protocol("WM_DELETE_WINDOW", editor.confirm_exit)  # Bind close event
        root.mainloop()

    def __init__(self, root):
        "Main init function of the editor"
        self.root = root
        root.config(cursor="")
        self.root.title(f"HTML Editor - Untitled Document")  # Default
        self.root.geometry("850x600")
        self.root.config(bg="#2B2B2B")
        self.root.resizable(True, True)

        self.mode = "dark"                          # Default
        self.unsaved_changes = False                # Track changes
        self.safe_mode = False                      # Track if safe mode is enabled
        self.auto_save_enabled = False              # Flag for auto-save status
        self.tag_completion_enabled = True          # Flag to track tag completion status
        self.current_file_path = None               # Initialize current_file_path
        self.set_icon()                             # Init icon function

        # Store the after ID for syntax highlighting
        self.after_id = None

        # Bind the window close event to cancel the after call
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
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
            "<Control-O>", lambda event: self.open_recent()
        )  # CTRL_O         >   Open Recent
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
        self.root.bind(
            "<Control-h>", lambda event: self.insert_html_template_01()
            )  # CTRL_H     >   Insert HTML Template 1
        self.root.bind(
            "<Control-H>", lambda event: self.insert_html_template_02()
            )  # CTRL_SHIFT_H     >   Insert HTML Template 2
        self.root.bind(
            "<Control-p>", lambda event: self.insert_html_centered_div()
            )  # CTRL_P    >   Insert HTML Centered Div
        self.root.bind(
            "<Control-t>", lambda event: self.open_template()
        )
        
        self.root.bind(
            ">", lambda event: self.complete_tag(event)
        )  # Bind '>' key for tag completion
        self.root.bind(
            '"', lambda event: self.complete_string(event)
        )  # Bind '"' key for string completion


        #####################################
        # Init widgets, set up text area
        #####################################
        self.menu_area = Frame(self.root, width=100, height=50, bg="#525252")
        self.menu_area.pack(side=TOP)

        self.infoButton = Button(
            self.menu_area,
            relief="flat",
            width=12,
            height=1,  
            text="HTML Editor",
            bg="#ffa600",
            fg="#000000",
            font=("TkDefaultFont", 12, "bold"),  
            command=self.info_window,
        )
        self.infoButton.pack(side=LEFT, padx=5, pady=5)  

        self.newButton = Button(
            self.menu_area,
            relief="flat",
            width=6,
            height=1,  
            text="New",
            bg="#757575",
            fg="#ffffff",
            font=("TkDefaultFont", 12, "bold"),
            command=self.new_document,
        )
        self.newButton.pack(side=LEFT, padx=5, pady=5)

        self.saveAsButton = Button(
            self.menu_area,
            relief="flat",
            width=8,
            height=1,
            text="Save as",
            bg="#757575",
            fg="#ffffff",
            font=("TkDefaultFont", 12, "bold"),
            command=self.save_document,
        )
        self.saveAsButton.pack(side=LEFT, padx=5, pady=5)

        self.saveButton = Button(
            self.menu_area,
            relief="flat",
            width=6,
            height=1,
            text="Save",
            bg="#757575",
            fg="#ffffff",
            font=("TkDefaultFont", 12, "bold"),
            command=self.save_changes,
        )
        self.saveButton.pack(side=LEFT, padx=5, pady=5)

        self.openButton = Button(
            self.menu_area,
            relief="flat",
            width=6,
            height=1,
            text="Open",
            bg="#757575",
            fg="#ffffff",
            font=("TkDefaultFont", 12, "bold"),
            command=self.open_document,
        )
        self.openButton.pack(side=LEFT, padx=5, pady=5)

        self.runButton = Button(
            self.menu_area,
            relief="flat",
            width=6,   
            height=1,   
            text="Run",
            bg="#757575",
            fg="#ffffff",
            font=("TkDefaultFont", 12, "bold"),   
            command=self.open_document_in_browser,
        )
        self.runButton.pack(side=LEFT, padx=5, pady=5)   

        self.viewButton = Button(
            self.menu_area,
            relief="flat",
            width=6,   
            height=1,   
            text="Zoom",
            bg="#757575",
            fg="#ffffff",
            font=("TkDefaultFont", 12, "bold"),   
            command=self.change_zoom,
        )
        self.viewButton.pack(side=LEFT, padx=5, pady=5)   

        self.frButton = Button(
            self.menu_area,
            relief="flat",
            width=10,   
            height=1,   
            text="Find/Replace",
            bg="#757575",
            fg="#ffffff",
            font=("TkDefaultFont", 12, "bold"),   
            command=self.find_replace,
        )
        self.frButton.pack(side=LEFT, padx=5, pady=5)   

        self.settingsbutton = Button(
            self.menu_area,
            relief="flat",
            width=8,   
            height=1,   
            text="Settings",
            bg="#757575",
            fg="#ffffff",
            font=("TkDefaultFont", 12, "bold"),   
            command=self.settings_window,
        )
        self.settingsbutton.pack(side=LEFT, padx=5, pady=5)   

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
        tab_size = font.measure("   ")  # Edit this to change tab size to your needs
        self.text_area.config(tabs=tab_size, selectbackground="#116891", inactiveselectbackground="#719cc4")
        self.text_area.bind("<<Modified>>", self.on_text_change)  # Track changes

        self.update_syntax_highlighting()  # Init syntax highlighting
        self.auto_save() # Init auto save (Not active until toggled)

        root.config(cursor="") # Remove busy cursor from root window (I have no idea why the config function isn't marked...)


    def set_icon(self):
        """Sets the application icon."""
        if pillow_imported:
            try:
                icon = Image.open("internal/icons/favicon.ico")
                icon = icon.resize((250, 250))              # Resize to appropriate icon size
                self.icon_image = ImageTk.PhotoImage(icon)  # Store the reference in the instance
                self.root.iconphoto(True, self.icon_image)  # Set the icon
            except Exception as e:
                pass


    #####################################
    # Highlight syntax
    #####################################
    def update_syntax_highlighting(self):
        "Highlights HTML, CSS, JS, and Markdown syntax in the code."
        # Clear previous tags
        self.text_area.tag_remove("html_tag", "1.0", END)
        self.text_area.tag_remove("html_parameter", "1.0", END)
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
        self.text_area.tag_remove("markdown_header", "1.0", END)
        self.text_area.tag_remove("markdown_bold", "1.0", END)
        self.text_area.tag_remove("markdown_italic", "1.0", END)
        self.text_area.tag_remove("markdown_link", "1.0", END)
        self.text_area.tag_remove("markdown_list", "1.0", END)
        self.text_area.tag_remove("javascript_builtin", "1.0", END)

        # Get content of text
        content = self.text_area.get("1.0", END)

        # Determine if the current file is markdown
        is_markdown = self.current_file_path and self.current_file_path.endswith(".md")

        if is_markdown:
            # Markdown patterns
            header_pattern = (r"(^|\n)(#{1,6})\s*(.*)")     # Matches headers (e.g., # Header)
            bold_pattern = r"\*\*(.*?)\*\*"                 # Matches bold text (e.g., **bold**)
            italic_pattern = r"\*(.*?)\*"                   # Matches italic text (e.g., *italic*)
            link_pattern = r"\[(.*?)\]\((.*?)\)"            # Matches links (e.g., [text](url))
            list_pattern = r"^\s*[-*]\s+(.*)"               # Matches list items (e.g., - item)

            # Highlight markdown headers
            for match in re.finditer(header_pattern, content):
                self.text_area.tag_add(
                    "markdown_header",
                    f"1.0 + {match.start(3)} chars",
                    f"1.0 + {match.end(3)} chars",
                )

            # Highlight bold text
            for match in re.finditer(bold_pattern, content):
                self.text_area.tag_add(
                    "markdown_bold",
                    f"1.0 + {match.start(1)} chars",
                    f"1.0 + {match.end(1)} chars",
                )

            # Highlight italic text
            for match in re.finditer(italic_pattern, content):
                self.text_area.tag_add(
                    "markdown_italic",
                    f"1.0 + {match.start(1)} chars",
                    f"1.0 + {match.end(1)} chars",
                )

            # Highlight links
            for match in re.finditer(link_pattern, content):
                self.text_area.tag_add(
                    "markdown_link",
                    f"1.0 + {match.start(1)} chars",
                    f"1.0 + {match.end(2)} chars",
                )

            # Highlight list items
            for match in re.finditer(list_pattern, content):
                self.text_area.tag_add(
                    "markdown_list",
                    f"1.0 + {match.start(1)} chars",
                    f"1.0 + {match.end(1)} chars",
                )

            # Configure markdown tag colors (Edit this to change colors to your needs)
            if self.mode == "dark":
                self.text_area.tag_config("markdown_header", foreground="#ffcc00")  # Yellow for headers
                self.text_area.tag_config("markdown_bold", foreground="#ff00ff")  # Pink for bold
                self.text_area.tag_config("markdown_italic", foreground="#00ffaa")  # Light green for italic
                self.text_area.tag_config("markdown_link", foreground="#00ff00")  # Green for links
                self.text_area.tag_config("markdown_list", foreground="#339933")  # Dark green for lists

            if self.mode == "high_contrast":
                self.text_area.tag_config("markdown_header", foreground="#ffcc00")  # Yellow for headers
                self.text_area.tag_config("markdown_bold", foreground="#ff00ff")  # Pink for bold
                self.text_area.tag_config("markdown_italic", foreground="#00ffaa")  # Light green for italic
                self.text_area.tag_config("markdown_link", foreground="#00ff00")  # Green for links
                self.text_area.tag_config("markdown_list", foreground="#339933")  # Dark green for lists

            if self.mode == "black_white":
                self.text_area.tag_config("markdown_header", foreground="#737373")
                self.text_area.tag_config("markdown_bold", foreground="#737373")
                self.text_area.tag_config("markdown_italic", foreground="#737373")
                self.text_area.tag_config("markdown_link", foreground="#737373")
                self.text_area.tag_config("markdown_list", foreground="#737373")

            elif self.mode == "light":
                self.text_area.tag_config("markdown_header", foreground="#ff6600")  # Orange for headers
                self.text_area.tag_config("markdown_bold", foreground="#ff00ff")  # Pink for bold
                self.text_area.tag_config("markdown_italic", foreground="#006666")  # Cyan for italic
                self.text_area.tag_config("markdown_link", foreground="#e60073")  # Pink for links
                self.text_area.tag_config("markdown_list", foreground="#339933")  # Dark green for lists

        else:
            # Regex patterns for HTML, CSS, and JavaScript

            declared_variables = set()

            # HTML patterns
            html_tag_pattern = r"</?[\w][\w\-\/]*[^<>]*\/?>"         # Matches HTML tags
            html_comment_pattern = r"<!--.*?-->"                        # Matches HTML comments
            html_parameter_pattern = r"(\s+)(\w+)(=)"                  # Matches HTML parameters (e.g., name="value")

            # CSS patterns
            css_class_pattern = r"(?:^|\s)\.[\w-]+"                     # Matches CSS classes
            css_property_pattern = r"[\w-]+(?=\s*:)"                    # Matches CSS properties

            # JavaScript patterns
            javascript_function_pattern = r"\b\w+\(\s*.*?\s*\)"             # Matches functions
            javascript_variable_pattern = r"\b(var|let|const)\s+(\w+)"      # Matches variables
            javascript_keyword_pattern = r"(?<![a-zA-Z0-9_])\b(var|let|const|function|if|else|for|while|return|switch|case|break|continue|try|catch|finally|async|await|import|export|class|extends|super|this|new|delete|instanceof|typeof|void|with|do|in|of|default|static|get|set|yield|throw|true|false|null|undefined)\b(?![a-zA-Z0-9_])" #Matches keywords
            javascript_builtin_pattern = r"\b(console|Math|Array|String|Object|Number|Date|Promise|JSON|Set|Map|RegExp|Error|Symbol|Function|Boolean|parseInt|parseFloat|isNaN|isFinite|eval|encodeURI|decodeURI|encodeURIComponent|decodeURIComponent)\b"  # Matches built-ins
            javascript_dom_function_pattern = r"\b(document|window)\.(getElementsByClassName|getElementById|getElementsByName|getElementsByTagName|querySelector|querySelectorAll|innerHTML|outerHTML|textContent|style|addEventListener|removeEventListener|dispatchEvent|createElement|createDocumentFragment|createTextNode|appendChild|insertBefore|replaceChild|removeChild|cloneNode|appendChild|insertAdjacentHTML|insertAdjacentText)\b"

            # String literal pattern
            string_literal_pattern = r'(["\'])(?:(?=(\\?))\2.)*?\1'  # Matches strings in double or single quotes

            # Integer pattern (not in a string and not in an HTML tag)
            integer_pattern = r'(?<![<"\'])\b\d+\b(?![>\'"])'  # Matches integers

            # px value pattern (not in a string and not in an HTML tag)
            px_value_pattern = (r'(?<![<"\'])\b\d+px\b(?![>\'"])')  # Matches numerals followed by 'px'

            # Operator and brace pattern
            operator_pattern = r"[+\-\=\(\)\{\}\[\]\*\%\|]"

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

            # HTML tags
            for match in re.finditer(html_tag_pattern, content):
                self.text_area.tag_add(
                    "html_tag",
                    f"1.0 + {match.start()} chars",
                    f"1.0 + {match.end()} chars",
                )

            # HTML parameters
            for match in re.finditer(html_parameter_pattern, content):
                self.text_area.tag_add(
                    "html_parameter",
                    f"1.0 + {match.start(2)} chars",
                    f"1.0 + {match.end(2)} chars",
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
                variable_name = match.group(2)
                declared_variables.add(variable_name)  # Store the variable name
                self.text_area.tag_add(
                    "javascript_variable",
                    f"1.0 + {match.start(2)} chars",
                    f"1.0 + {match.end(2)} chars",
                )

            # Highlight variables later in the code
            for variable_name in declared_variables:
                variable_usage_pattern = rf"\b{variable_name}(?![\w\.])"  # Matches the variable name  # Matches the variable name
                for match in re.finditer(variable_usage_pattern, content):
                    self.text_area.tag_add(
                        "javascript_variable",
                        f"1.0 + {match.start()} chars",
                        f"1.0 + {match.end()} chars",
                    )

            # JavaScript keywords
            for match in re.finditer(javascript_keyword_pattern, content):
                self.text_area.tag_add(
                    "javascript_keyword",
                    f"1.0 + {match.start()} chars",
                    f"1.0 + {match.end()} chars",
                )

            # JavaScript builtins
            for match in re.finditer(javascript_builtin_pattern, content):
                self.text_area.tag_add(
                    "javascript_builtin",
                    f"1.0 + {match.start()} chars",
                    f"1.0 + {match.end()} chars",
                )

            # JavaScript DOM functions
            for match in re.finditer(javascript_dom_function_pattern, content):
                self.text_area.tag_add(
                    "javascript_dom_function",
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

            # Operators
            for match in re.finditer(operator_pattern, content):
                self.text_area.tag_add(
                    "operator",
                    f"1.0 + {match.start()} chars",
                    f"1.0 + {match.end()} chars",
                )

            # Configure tag colors (Edit this to change colors to your needs)
            if self.mode == "dark":
                self.text_area.tag_config("html_tag", foreground="#66e0ff")                 # Light blue
                self.text_area.tag_config("html_parameter", foreground="#ffcc00")           # Yellow orange
                self.text_area.tag_config("html_comment", foreground="#009900")             # Dark green
                self.text_area.tag_config("js_comment", foreground="#009900")               # Dark green
                self.text_area.tag_config("css_class", foreground="#ff00ff")                # Pink
                self.text_area.tag_config("css_property", foreground="#00ffaa")             # Light green
                self.text_area.tag_config("javascript_function", foreground="#ffcc00")      # Yellow orange
                self.text_area.tag_config("javascript_dom_function", foreground="#ffcc00")  # Yellow orange
                self.text_area.tag_config("javascript_variable", foreground="#00ff00")      # Lime
                self.text_area.tag_config("javascript_keyword", foreground="#ff0066")       # Red
                self.text_area.tag_config("javascript_builtin", foreground="#bbff00")       # Light green
                self.text_area.tag_config("string_literal", foreground="#ff9933")           # Orange
                self.text_area.tag_config("integer", foreground="#ffcc00")                  # Yellow orange
                self.text_area.tag_config("px_value", foreground="#ffcc00")                 # Yellow orange
                self.text_area.tag_config("operator", foreground="#00a2ff")                 # Lightblue

            if self.mode == "light":
                self.text_area.tag_config("html_tag", foreground="#31a2e4")                 # Blue
                self.text_area.tag_config("html_parameter", foreground="#b85300")           # Brown
                self.text_area.tag_config("html_comment", foreground="#008000")             # Dark green
                self.text_area.tag_config("js_comment", foreground="#008000")               # Dark green
                self.text_area.tag_config("css_class", foreground="#ca32ca")                # Pink
                self.text_area.tag_config("css_property", foreground="#ac00fc")             # Purple
                self.text_area.tag_config("javascript_function", foreground="#ff5e00")      # Dark orange
                self.text_area.tag_config("javascript_dom_function", foreground="#ff5e00")  # Dark orange
                self.text_area.tag_config("javascript_variable", foreground="#19d677")      # Green
                self.text_area.tag_config("javascript_keyword", foreground="#ff0000")       # Red
                self.text_area.tag_config("javascript_builtin", foreground="#00cc00")       # Green
                self.text_area.tag_config("string_literal", foreground="#cc6600")           # Brown
                self.text_area.tag_config("integer", foreground="#1dbb2a")                  # Green
                self.text_area.tag_config("px_value", foreground="#1dbb2a")                 # Green
                self.text_area.tag_config("operator", foreground="#00a2ff")                 # Lightblue

            if self.mode == "high_contrast":
                self.text_area.tag_config("html_tag", foreground="#66e0ff")                 # Light blue
                self.text_area.tag_config("html_parameter", foreground="#ff0000")           # Red
                self.text_area.tag_config("html_comment", foreground="#009900")             # Dark green
                self.text_area.tag_config("js_comment", foreground="#009900")               # Dark green
                self.text_area.tag_config("css_class", foreground="#ff3399")                # Pink
                self.text_area.tag_config("css_property", foreground="#00ffaa")             # Light green
                self.text_area.tag_config("javascript_function", foreground="#ffcc00")      # Yellow orange
                self.text_area.tag_config("javascript_dom_function", foreground="#ffcc00")  # Yellow orange
                self.text_area.tag_config("javascript_variable", foreground="#00ff00")      # Lime
                self.text_area.tag_config("javascript_keyword", foreground="#ff0066")       # Red
                self.text_area.tag_config("javascript_builtin", foreground="#00cc00")       # Dark green
                self.text_area.tag_config("string_literal", foreground="#ff9933")           # Orange
                self.text_area.tag_config("integer", foreground="#ffcc00")                  # Yellow orange
                self.text_area.tag_config("px_value", foreground="#ffcc00")                 # Yellow orange
                self.text_area.tag_config("operator", foreground="#00a2ff")                 # Lightblue

            if self.mode == "black_white":
                self.text_area.tag_config("html_tag", foreground="#969696")
                self.text_area.tag_config("html_parameter", foreground="#666666")
                self.text_area.tag_config("html_comment", foreground="#585858")
                self.text_area.tag_config("js_comment", foreground="#585858")
                self.text_area.tag_config("css_class", foreground="#666666")
                self.text_area.tag_config("css_property", foreground="#808080")
                self.text_area.tag_config("javascript_function", foreground="#808080")
                self.text_area.tag_config("javascript_dom_function", foreground="#808080")
                self.text_area.tag_config("javascript_variable", foreground="#808080")
                self.text_area.tag_config("javascript_keyword", foreground="#505050")
                self.text_area.tag_config("javascript_builtin", foreground="#808080")
                self.text_area.tag_config("string_literal", foreground="#000000")
                self.text_area.tag_config("integer", foreground="#000000")
                self.text_area.tag_config("px_value", foreground="#000000")
                self.text_area.tag_config("operator", foreground="#808080")

        # Schedule next update
        self.after_id = self.root.after(100, self.update_syntax_highlighting)


    #####################################
    # Tag/String Auto Complete Function
    #####################################
    def toggle_tag_completion(self):
        """Toggles the tag completion feature on and off."""
        self.tag_completion_enabled = not self.tag_completion_enabled
        status = "enabled" if self.tag_completion_enabled else "disabled"
        messagebox.showinfo("Tag Completion", f"Tag completion is now {status}.")

    def complete_tag(self, event):
        """Completes the HTML tag at the cursor position."""
        if not self.tag_completion_enabled:  # Check if tag completion is enabled
            return  # Exit if tag completion is disabled

        # Get the current cursor position
        cursor_index = self.text_area.index(INSERT)
        line_text = self.text_area.get(cursor_index.split('.')[0] + ".0", cursor_index)

        # Define a list of self-closing tags
        self_closing_tags = ["area", "base", "br", "col", "embed", "hr", "img", "input", "keygen", "link", "meta", "param", "source", "track", "wbr"]
        opening_tag_pattern = r"<(\w+)(\s*[^>]*)?>"
        closing_tag_pattern = r"</(\w+)>"

        # Find all opening tags and closing tags in the line
        opening_tags = []
        closing_tags = []

        for match in re.finditer(opening_tag_pattern, line_text):
            opening_tags.append(match.group(1))

        for match in re.finditer(closing_tag_pattern, line_text):
            closing_tags.append(match.group(1))

        # Check for the most recent unclosed opening tag
        for tag in reversed(opening_tags):
            if tag not in self_closing_tags and opening_tags.count(tag) > closing_tags.count(tag):
                # Insert the closing tag at the cursor position
                self.text_area.insert(cursor_index, f"</{tag}>")
                # Move the cursor after the closing tag
                self.text_area.mark_set(INSERT, cursor_index)
                return "break"  # Prevent default behavior of the key event

        return "break"  # Prevent default behavior if no tag is found

    def complete_string(self, event):
        """Completes the double string at the cursor position."""
        # Check if string completion is enabled
        if not self.tag_completion_enabled:
            return  # Exit if string completion is disabled

        # Get the current cursor position
        cursor_index = self.text_area.index(INSERT)
        line_text = self.text_area.get(cursor_index.split('.')[0] + ".0", cursor_index)

        # Check if the last character is a double quote
        if line_text and line_text[-1] == '"':
            # Insert another double quote at the cursor position
            self.text_area.insert(cursor_index, '"')
            # Move the cursor between the quotes
            self.text_area.mark_set(INSERT, cursor_index)
            return "break"  # Prevent default behavior of the key event

        # If the last character is not a double quote, just insert one
        self.text_area.insert(cursor_index, '"')
        # Move the cursor after the inserted quote
        self.text_area.mark_set(INSERT, cursor_index)
        return "break"  # Prevent default behavior if no action is taken


    def insert_html_template_01(self):
        """Inserts a basic HTML template at the cursor position."""
        html_template = """<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
    
    </body>
</html>"""
        
        # Get the current cursor position
        cursor_index = self.text_area.index(INSERT)
        
        # Insert the HTML template at the cursor position
        self.text_area.insert(cursor_index, html_template)


    def insert_html_template_02(self):
        """Inserts a basic HTML template at the cursor position."""
        html_template = """<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/x-icon" href="favicon.ico">
        <link rel="stylesheet" href="styles.css">
        <title>Document</title>
        <meta name="description" content="Description">
    </head>
    <body>
    
    </body>
</html>"""
        
        # Get the current cursor position
        cursor_index = self.text_area.index(INSERT)
        
        # Insert the HTML template at the cursor position
        self.text_area.insert(cursor_index, html_template)


    def insert_html_centered_div(self):
        """Inserts a centered div at the cursor position."""
        html_template = """<div style="max-width: fit-content; margin-left: auto; margin-right: auto;"><div>"""
        
        # Get the current cursor position
        cursor_index = self.text_area.index(INSERT)
        
        # Insert the HTML template at the cursor position
        self.text_area.insert(cursor_index, html_template)

    def open_template(self):
        """Copies a template file into the editor. GUI is using a new concept for creating buttons that should be more efficient"""
        top = Toplevel(self.root)
        top.title("Open Template")
        top.geometry("400x300")
        top.config(bg="#333333")
        top.resizable(False, False)

        title_label = Label(
            top,
            text="Select a Template",
            font=("TkDefaultFont", 18, "bold"),
            fg="#ffffff",
            bg="#333333",
        )
        title_label.pack(pady=10)

        ttk.Separator(top, orient="horizontal").pack(fill="x", padx=10, pady=5)

        button_frame = Frame(top, bg="#333333")
        button_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Define template names and their corresponding colors
        templates = [
            {"name": "Generic Black", "color": "#000000", "file": "generic_black.html"},
            {"name": "Generic Blue", "color": "#0000ff", "file": "generic_blue.html"},
            {"name": "Generic Green", "color": "#00ff00", "file": "generic_green.html"},
            {"name": "Generic Red", "color": "#ff0000", "file": "generic_red.html"},
        ]

        # Function to load and insert a template
        def load_template(template_name):
            try:
                with open(f"internal/templates/{template_name}", "r") as file:
                    template_content = file.read()
                    cursor_index = self.text_area.index(INSERT)
                    self.text_area.insert(cursor_index, template_content)
                    messagebox.showinfo("Success", "Template loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load template: {str(e)}")

        # New approach for creating buttons that should be more efficient
        for template in templates:
            template_button = Button(
                button_frame,
                text=template["name"],
                font=("TkDefaultFont", 12),
                fg="#ffffff",
                bg=template["color"],
                width=20,
                relief="flat",
                command=lambda t=template["file"]: load_template(t),
            )
            template_button.pack(pady=5, padx=10, fill="x")

        close_button = Button(
            top,
            text="Close",
            font=("TkDefaultFont", 12),
            fg="#ffffff",
            bg="#ff0066",
            width=10,
            relief="flat",
            command=top.destroy,
        )
        close_button.pack(pady=10)

        # Center window on the screen
        top.update_idletasks()
        width = top.winfo_width()
        height = top.winfo_height()
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry(f"{width}x{height}+{x}+{y}")


    #####################################
    # Save, open, autosave functions, title bar update, safe mode, text modfied detector
    #####################################
    def new_document(self):
        "Creates a new instance of HTMLEditor for a new window"
        new_root = Tk()
        new_editor = HTMLEditor(new_root)
        new_editor.set_icon()
        new_root.mainloop()

    def toggle_safe_mode(self):
        """Toggles safe mode on and off."""
        self.safe_mode = not self.safe_mode                                     # Toggle the safe mode flag
        self.text_area.config(state=DISABLED if self.safe_mode else NORMAL)     # Enable/disable editing
        if self.safe_mode:
            messagebox.showinfo("Safe Mode", "Safe mode is now enabled. You cannot edit the document.")
        else:
            messagebox.showinfo("Safe Mode", "Safe mode is now disabled. You can edit the document.")

    def on_text_change(self, event):
        """Gets called if the text area is modified. Calls update functions."""
        self.unsaved_changes = True
        self.text_area.edit_modified(False)  # Reset modified flag
        self.update_title()  # Update the title

    def save_document(self):
        """Saves the current document to a new filepath"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[
                    ("HTML Sites", "*.html"),
                    ("HTML Sites", "*.htm"),
                    ("Cascading Style Sheets", "*.css"),
                    ("JavaScript Scripts", "*.js"),
                    ("Markdown Text Files", "*.md"),
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
                    self.add_to_recent_files(file_path)
            else:
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save document: {str(e)}")

    def save_changes(self):
        """Saves the current document to a file"""
        try:
            with open(self.current_file_path, "w") as file:
                file.write(self.text_area.get("1.0", "end-1c"))
                self.unsaved_changes = False    # Reset unsaved changes flag
                self.update_title()             # Update title
        except:
            self.save_document()

    def open_document(self):
        """Opens a document from a file"""
        try:
            file_path = filedialog.askopenfilename(
                defaultextension=".html",
                filetypes=[
                    ("All supported filetypes", "*.html"),
                    ("All supported filetypes", "*.htm"),
                    ("All supported filetypes", "*.css"),
                    ("All supported filetypes", "*.js"),
                    ("All supported filetypes", "*.md"),
                    ("All supported filetypes", "*.txt"),

                    ("HTML Sites", "*.html"),
                    ("HTML Sites", "*.htm"),
                    ("Cascading Style Sheets", "*.css"),
                    ("JavaScript Scripts", "*.js"),
                    ("Markdown Text Files", "*.md"),
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
                    self.add_to_recent_files(file_path)
                    self.text_area.config(state=DISABLED if self.safe_mode else NORMAL)  # Disable editing if in safe mode
            else:
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open document: {str(e)}")

    def update_title(self):
        """Updates the title of the window based on the current file path and unsaved changes status"""
        if self.current_file_path:  # Check if current_file_path is set
            if self.unsaved_changes:
                self.root.title(f"HTML Editor - {os.path.basename(self.current_file_path)} ⚪")
            else:
                self.root.title(f"HTML Editor - {os.path.basename(self.current_file_path)}")
        else:
            self.root.title("HTML Editor - Untitled Document")  # Default title if no file is opened

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

    def open_recent(self):
        """Opens a window to display recently opened files."""
        try:
            with open("internal/recent_store.json", "r") as file:
                recent_files = json.load(file)
        except FileNotFoundError:
            recent_files = []

        top = Toplevel(self.root)
        top.title("Recently Opened Files")
        top.geometry("800x800")
        top.config(bg="#333333")
        top.resizable(True, True)

        title_label = Label(
            top,
            text="Recently Opened Files",
            font=("TkDefaultFont", 18, "bold"),
            fg="#ffffff",
            bg="#333333",
        )
        title_label.pack(pady=10)

        ttk.Separator(top, orient="horizontal").pack(fill="x", padx=10, pady=5)

        frame = Frame(top, bg="#333333")
        frame.pack(pady=10, padx=10, fill="both", expand=True)

        for i, file in enumerate(recent_files):
            file_button = Button(
                frame,
                text=f"{file['filename']} - {file['filepath']}\nOpened at: {file['time']}",
                font=("TkDefaultFont", 12),
                fg="#ffffff",
                bg="#757575",
                width=40,
                relief="flat",
                command=lambda filepath=file['filepath']: self.open_recent_file(filepath, top),
            )
            file_button.pack(pady=5, fill="x")

        close_button = Button(
            top,
            text="Close",
            font=("TkDefaultFont", 12),
            fg="#ffffff",
            bg="#ff0066",
            width=10,
            relief="flat",
            command=top.destroy,
        )
        close_button.pack(pady=10)

    def open_recent_file(self, filepath, top):
        """Opens a recently opened file."""
        self.open_document_from_path(filepath)
        top.destroy()

    def open_document_from_path(self, filepath):
        """Opens a document from a file path."""
        try:
            with open(filepath, "r") as file:
                text = file.read()
                self.file_name = os.path.basename(filepath)
                self.text_area.delete("1.0", END)
                self.text_area.insert("1.0", text)
                self.current_file_path = filepath
                self.unsaved_changes = False  # Reset unsaved changes flag
                self.update_title()  # Update title
                self.text_area.config(state=DISABLED if self.safe_mode else NORMAL)  # Disable editing if in safe mode
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open document: {str(e)}")

    def add_to_recent_files(self, filepath):
        """Adds the opened or saved file to the recent files list."""
        recent_file = {
            "filename": os.path.basename(filepath),
            "filepath": os.path.abspath(filepath),
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        try:
            if os.path.exists("internal/recent_store.json"):
                with open("internal/recent_store.json", "r") as file:
                    recent_files = json.load(file)
            else:
                recent_files = []

            # Remove duplicates and keep the latest entry
            recent_files = [file for file in recent_files if file['filepath'] != recent_file['filepath']]
            recent_files.insert(0, recent_file)  # Add new file at the top

            # Limit to the last 10 recent files
            if len(recent_files) > 10:
                recent_files = recent_files[:10]

            with open("internal/recent_store.json", "w") as file:
                json.dump(recent_files, file, indent=4)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update recent files: {str(e)}")
    #####################################
    # Open file in browser
    #####################################
    def open_document_in_browser(self):
        """Opens the document in a new tab"""
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
        top.geometry("300x120")
        top.config(bg="#333333")
        top.title("Adjust zoom")
        top.resizable(False, False)
        Label(top, text="Adjust zoom", font=("TkDefaultFont", 11,"bold"), fg="#FFFFFF", bg="#333333").pack()
        self.slider = Scale(
            top,
            bg="#333333",
            fg="#FFFFFF",
            relief="flat",
            highlightthickness=0,
            from_=1,
            to=100,
            length=300,
            orient=HORIZONTAL,
            command=self.update_zoom,
        )
        self.slider.set(13)
        self.slider.pack()
        Button(top, text="Close", relief="flat", fg="#FFFFFF", bg="#ff0066", command=top.destroy).pack(pady=10)
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
    # Information, settings, license window
    #####################################
    def info_window(self):
        """Creates a window with information about the application"""
        top = Toplevel(self.root)
        top.title("About")
        top.geometry("300x170")
        top.config(bg="#333333")
        top.resizable(False, False)

        # Load and resize the logo
        try:
            logo = Image.open("internal/icons/logo.png")
            logo = logo.resize((50, 50))  # Resize to 50x50 pixels
            self.logo_image = ImageTk.PhotoImage(logo)  # Store the reference in the instance
            logo_label = Label(top, image=self.logo_image)
            logo_label.image = self.logo_image  # Keep a reference to avoid garbage collection
            logo_label.pack(pady=5)
        except Exception as e:
            Label(top, text="Logo not available", fg="#ffffff", bg="#333333").pack()

        Label(top, text="HTML Editor", font=("TkDefaultFont", 15, "bold"),fg="#ffffff", bg="#333333").pack(pady=5)
        Label(top, text="Version 1.1", fg="#ffffff", bg="#333333").pack()
        Label(top, text="Copyright (c) 2024-2025", fg="#ffffff", bg="#333333").pack()
        Label(top, text="Author: Tobias Kisling", fg="#ffffff", bg="#333333").pack()

    def license_window(self):
        """Creates a toplevel window with the license"""
        top = Toplevel(self.root)
        top.title("License")
        top.geometry("600x400")
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
            text="Copyright (c) 2024-2025 Tobias Kisling (hasderhi)",
            fg="#ffffff",
            bg="#333333",
        ).pack()
        
        Label(
            top,
            fg="#ffffff",
            bg="#333333",
            text=
            """Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
            and associated documentation files (the 'Software'), to deal in the Software without restriction, 
            including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
            and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
            subject to the following conditions:
            
            The above copyright notice and this permission notice shall be
            included in all copies or substantial portions of the Software.
            
            THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, 
            EXPRESS OR IMPLIED,INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
            FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
            OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
            IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING FROM, OUT OF OR IN CONNECTION
            WITH THE SOFTWARE OR\nTHE USE OR OTHER DEALINGS IN THE SOFTWARE.


            HTML5 Logo by <https://www.w3.org/>""",
        ).pack()

    def settings_window(self):
        """Creates a toplevel window with settings"""
        top = Toplevel(self.root)
        top.title("Settings")
        top.geometry("440x500")
        top.config(bg="#333333")
        top.resizable(False, True)

        canvas = Canvas(top, bg="#333333", highlightthickness=0)
        scrollable_frame = Frame(canvas, bg="#333333")

        # Configure scroll
        scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.pack(side="left", fill="both", expand=True)

        # Handle mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # Scroll up/down
        def on_arrow_up(event):
            canvas.yview_scroll(-1, "units")
        def on_arrow_down(event):
            canvas.yview_scroll(1, "units")

        # Bind mouse scroll wheel and arrow keys to the canvas
        mousewheel_binding = canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Up>", on_arrow_up)
        canvas.bind_all("<Down>", on_arrow_down)

        # When settings window is closed, unbind all inputs from the window to prevent errors
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Up>")
            canvas.unbind_all("<Down>")
            top.destroy()

        # Bind close event to on_close function
        top.protocol("WM_DELETE_WINDOW", on_close)

        Label(
            scrollable_frame,
            text="Settings",
            font=("TkDefaultFont", 20, "bold"),
            fg="#ffffff",
            bg="#333333",
        ).pack(pady=10, anchor="center")

        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=10, pady=10)

        Label(
            scrollable_frame,
            text="Appearance",
            font=("TkDefaultFont", 15, "bold"),
            fg="#ffffff",
            bg="#333333",
        ).pack(anchor="center")

        button_frame1 = Frame(scrollable_frame, width=200, height=20, bg="#333333")
        button_frame1.pack(pady=10)

        Button(
            button_frame1,
            relief="flat",
            text="Light mode",
            font=("TkDefaultFont"),
            fg="#333333",
            bg="#fafafa",
            command=self.change_to_light_mode,
        ).pack(side=LEFT, padx=5)
        Button(
            button_frame1,
            text="Dark mode",
            relief="flat",
            font=("TkDefaultFont"),
            fg="#ffffff",
            bg="#7c7c7c",
            command=self.change_to_dark_mode,
        ).pack(side=LEFT, padx=5)
        Button(
            button_frame1,
            text="High contrast mode",
            relief="flat",
            font=("TkDefaultFont"),
            fg="#ffffff",
            bg="#5c5858",
            command=self.change_to_high_contrast_mode,
        ).pack(side=LEFT, padx=5)
        Button(
            button_frame1,
            text="Black/White mode",
            relief="flat",
            font=("TkDefaultFont"),
            fg="#000000",
            bg="#ffffff",
            command=self.change_to_black_white_mode,
        ).pack(side=LEFT, padx=5)

        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=10, pady=10)

        Label(
            scrollable_frame,
            text="Safe Mode",
            font=("TkDefaultFont", 15, "bold"),
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
            relief="flat",
            bg="#ffcc00",
            fg="#000000",
            command=self.toggle_safe_mode,
        ).pack(side=LEFT, padx=5)

        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=10, pady=10)

        Label(
            scrollable_frame,
            text="Auto Save",
            font=("TkDefaultFont", 15, "bold"),
            fg="#ffffff",
            bg="#333333",
        ).pack(anchor="center")
        Label(
            scrollable_frame,
            text=" When auto save is activated, the current document\nis saved every 10 seconds.",
            font=("TkDefaultFont"),
            fg="#ffffff",
            bg="#333333",
        ).pack(anchor="center")

        button_frame3 = Frame(scrollable_frame, width=200, height=20, bg="#333333")
        button_frame3.pack(pady=10)

        Button(
            button_frame3,
            relief="flat",
            text="Toggle Auto Save",
            bg="#0099cc",
            fg="#f0f0f0",
            command=self.toggle_auto_save,
        ).pack(pady=10)

        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=10, pady=10)

        Label(
            scrollable_frame,
            text="Tag completion",
            font=("TkDefaultFont", 15, "bold"),
            fg="#ffffff",
            bg="#333333",
        ).pack(anchor="center")

        button_frame4 = Frame(scrollable_frame, width=200, height=20, bg="#333333")
        button_frame4.pack(pady=10)

        Button(
            button_frame4,
            relief="flat",
            text="Toggle Tag Completion",
            font=("TkDefaultFont"),
            fg="#000000",
            bg="#ff9100",
            command=self.toggle_tag_completion,
        ).pack(side=LEFT, padx=5)

        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=10, pady=10)

        Label(
            scrollable_frame,
            text="Templates",
            font=("TkDefaultFont", 15, "bold"),
            fg="#ffffff",
            bg="#333333",
        ).pack(anchor="center")

        button_frame5 = Frame(scrollable_frame, width=200, height=20, bg="#333333")
        button_frame5.pack(pady=10)

        Button(
            button_frame5,
            relief="flat",
            text="Open template chooser",
            font=("TkDefaultFont"),
            fg="#ffffff",
            bg="#ff0000",
            command=self.open_template,
        ).pack(side=LEFT, padx=5)

        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=10, pady=10)

        Label(
            scrollable_frame,
            text="About and licensing",
            font=("TkDefaultFont", 15, "bold"),
            fg="#ffffff",
            bg="#333333",
        ).pack(anchor="center")

        button_frame6 = Frame(scrollable_frame, width=200, height=20, bg="#333333")
        button_frame6.pack(pady=10)

        Button(
            button_frame6,
            relief="flat",
            text="About HTML editor",
            font=("TkDefaultFont"),
            fg="#000000",
            bg="#ffd900",
            command=self.info_window,
        ).pack(side=LEFT, padx=5)
        Button(
            button_frame6,
            relief="flat",
            text="Show license",
            font=("TkDefaultFont"),
            fg="#000000",
            bg="#ffd900",
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
            relief="flat",
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
        self.text_area.config(bg="#ffffff", fg="#000000", insertbackground="#000000", selectbackground="#6ed1ff", inactiveselectbackground="#afe6ff")

        # Menu area button colors
        self.infoButton.config(bg="#ffa600", fg="#000000")
        self.newButton.config(bg="#f0f0f0", fg="#757575")
        self.saveAsButton.config(bg="#f0f0f0", fg="#757575")
        self.saveButton.config(bg="#f0f0f0", fg="#757575")
        self.openButton.config(bg="#f0f0f0", fg="#757575")
        self.runButton.config(bg="#f0f0f0", fg="#757575")
        self.viewButton.config(bg="#f0f0f0", fg="#757575")
        self.frButton.config(bg="#f0f0f0", fg="#757575")
        self.settingsbutton.config(bg="#f0f0f0", fg="#757575")

    def change_to_dark_mode(self):
        """Changes to dark mode"""
        self.mode = "dark"  # Set mode
        # Change root window bg/fg
        self.root.config(bg="#2B2B2B")
        self.text_area.config(bg="#333333", fg="#f0f0f0", insertbackground="#f0f0f0", selectbackground="#116891", inactiveselectbackground="#719cc4")

        # Menu area button colors
        self.infoButton.config(bg="#ffa600", fg="#000000")
        self.newButton.config(bg="#757575", fg="#f0f0f0")
        self.saveAsButton.config(bg="#757575", fg="#f0f0f0")
        self.saveButton.config(bg="#757575", fg="#f0f0f0")
        self.openButton.config(bg="#757575", fg="#f0f0f0")
        self.runButton.config(bg="#757575", fg="#f0f0f0")
        self.viewButton.config(bg="#757575", fg="#f0f0f0")
        self.frButton.config(bg="#757575", fg="#f0f0f0")
        self.settingsbutton.config(bg="#757575", fg="#f0f0f0")

    def change_to_high_contrast_mode(self):
        """Changes to high contrast mode"""
        self.mode = "high_contrast"  # Set mode
        # Change root window bg/fg
        self.root.config(bg="#000000")
        self.text_area.config(bg="#000000", fg="#ffffff", insertbackground="#ffffff", selectbackground="#0011ff", inactiveselectbackground="#0011ff")

        # Menu area button colors
        self.infoButton.config(bg="#ffc861", fg="#000000")
        self.newButton.config(bg="#757575", fg="#f0f0f0")
        self.saveAsButton.config(bg="#757575", fg="#f0f0f0")
        self.saveButton.config(bg="#757575", fg="#f0f0f0")
        self.openButton.config(bg="#757575", fg="#f0f0f0")
        self.runButton.config(bg="#757575", fg="#f0f0f0")
        self.viewButton.config(bg="#757575", fg="#f0f0f0")
        self.frButton.config(bg="#757575", fg="#f0f0f0")
        self.settingsbutton.config(bg="#757575", fg="#f0f0f0")

    def change_to_black_white_mode(self):
        """Changes to black and white mode"""
        self.mode = "black_white"  # Set mode
        # Change root window bg/fg
        self.root.config(bg="#ffffff")
        self.text_area.config(bg="#ffffff", fg="#000000", insertbackground="#000000", selectbackground="#6ed1ff", inactiveselectbackground="#afe6ff")

        # Menu area button colors
        self.infoButton.config(bg="#ffffff", fg="#000000")
        self.newButton.config(bg="#757575", fg="#f0f0f0")
        self.saveAsButton.config(bg="#757575", fg="#f0f0f0")
        self.saveButton.config(bg="#757575", fg="#f0f0f0")
        self.openButton.config(bg="#757575", fg="#f0f0f0")
        self.runButton.config(bg="#757575", fg="#f0f0f0")
        self.viewButton.config(bg="#757575", fg="#f0f0f0")
        self.frButton.config(bg="#757575", fg="#f0f0f0")
        self.settingsbutton.config(bg="#757575", fg="#f0f0f0")


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

    def on_close(self):
        """Handles the window close event."""
        if self.after_id:
            self.root.after_cancel(self.after_id)  # Cancel the scheduled after call
        self.root.destroy()  # Close the window


#####################################
# Init main class
#####################################
HTMLEditor.init()

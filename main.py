try: 
    from tkinter import *
    from tkinter import filedialog
    from tkinter import colorchooser
    from tkinter import messagebox
    from tkinter import Toplevel, Text, WORD, END, DISABLED, Button
    from tkinter import ttk
    import re
    import os
    import sys
    import pickle
    import threading
    import subprocess
except Exception as e:
    print(f"Error importing modules: {e}")
    try:
        from tkinter import messagebox
        messagebox.showerror("Error", f"Error importing modules: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error importing modules: {e}")
        sys.exit(1)


from tkinter import *
from tkinter import filedialog
from tkinter import colorchooser
from tkinter import messagebox
from tkinter import Toplevel, Text, WORD, END, DISABLED, Button
import re
import os
import sys
import pickle
import threading
import subprocess


class CodeEditor:

    def init():
        root = Tk()
        CodeEditor(root)
        root.mainloop()

    




    def update_syntax_highlighting(self):
        self.dev_mode = True
        # Remove existing tags
        for tag in ['keyword', 'comment', 'string', 'function', 'brace', 'variable', 'default', 'builtin', 'number']:
            self.text_area.tag_remove(tag, '1.0', END)

        # Set default text color to white
        self.text_area.config(fg='white')

        text = self.text_area.get(1.0, END)
        lines = text.split('\n')

        # Find all variable declarations
        variable_declarations = []
        for i, line in enumerate(lines):
            for match in re.finditer(r'\b\w+(?=\s*=\s*)', line):
                variable_declarations.append(match.group())

        # Highlight variables
        for i, line in enumerate(lines):
            # Comments
            for match in re.finditer(r'#.*', line):
                start = f'{i+1}.{match.start()}'
                end = f'{i+1}.{match.end()}'
                self.text_area.tag_add('comment', start, end)

            # Strings
            for match in re.finditer(r'("[^"]*"|\'[^\']*\')', line):
                start = f'{i+1}.{match.start()}'
                end = f'{i+1}.{match.end()}'
                self.text_area.tag_add('string', start, end)

            # Keywords
            keywords = ['and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield']
            for keyword in keywords:
                for match in re.finditer(r'\b' + re.escape(keyword) + r'\b', line):
                    start = f'{i+1}.{match.start()}'
                    end = f'{i+1}.{match.end()}'
                    self.text_area.tag_add('keyword', start, end)

            # Functions
            for match in re.finditer(r'\b\w+(?=\s*\()', line):
                start = f'{i+1}.{match.start()}'
                end = f'{i+1}.{match.end()}'
                self.text_area.tag_add('function', start, end)

            # Variables
            for variable in variable_declarations:
                for match in re.finditer(r'\b' + re.escape(variable) + r'\b', line):
                    start = f'{i+1}.{match.start()}'
                    end = f'{i+1}.{match.end()}'
                    self.text_area.tag_add('variable', start, end)

            # Braces
            for match in re.finditer(r'[\(\)\[\]\{\}]', line):
                start = f'{i+1}.{match.start()}'
                end = f'{i+1}.{match.end()}'
                self.text_area.tag_add('brace', start, end)

            # Builtin types
            builtins = ['int', 'str', 'float', 'dict', 'list', 'None', 'bool']
            for builtin in builtins:
                for match in re.finditer(r'\b' + re.escape(builtin) + r'\b', line):
                    start = f'{i+1}.{match.start()}'
                    end = f'{i+1}.{match.end()}'
                    self.text_area.tag_add('builtin', start, end)

            # Numbers
            for match in re.finditer(r'\b\d+(?:\.\d+)?\b', line):
                start = f'{i+1}.{match.start()}'
                end = f'{i+1}.{match.end()}'
                self.text_area.tag_add('number', start, end)

        # Apply the color configurations
        self.text_area.tag_config('keyword', foreground='#569CD6')  # Light blue
        self.text_area.tag_config('comment', foreground='#608B4E')  # Green
        self.text_area.tag_config('string', foreground='#CE9178')   # Orange
        self.text_area.tag_config('function', foreground='#DCDCAA') # Yellow
        self.text_area.tag_config('variable', foreground='#66CCCC') # Light blue-green
        self.text_area.tag_config('brace', foreground='#D4D4D4')    # Light gray
        self.text_area.tag_config('builtin', foreground='#9A6CD9')  # Purple
        self.text_area.tag_config('number', foreground='#FF69B4')   # Pink

        if self.dev_mode:
            self.root.after(100, self.update_syntax_highlighting)




    def __init__(self, root):
        self.root = root
        self.root.title("Code Editor")
        self.root.geometry("800x600")
        self.root.config(bg="#2B2B2B")
        self.root.resizable(True, True)

        #self.root.iconbitmap("icon.ico")
        #self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        

        self.menu_area = Frame(self.root, width=100, height=50, bg="#4d4d4d")
        self.menu_area.pack(side=TOP)
        
        
        self.saveAsButton = Button(self.menu_area, width=10, height=2, text="Save as", bg="#33ccff")
        self.saveAsButton.pack(side=LEFT)
        self.saveButton = Button(self.menu_area, width=10, height=2, text="Save", bg="#33ccff")
        self.saveButton.pack(side=LEFT)
        self.viewButton = Button(self.menu_area, width=10, height=2, text="View", bg="#339933")
        self.viewButton.pack(side=LEFT)
        self.runButton = Button(self.menu_area, width=10, height=2, text="Run", bg="#cc66ff")
        self.runButton.pack(side=LEFT)
        self.settingsButton = Button(self.menu_area, width=10, height=2, text="Settings")
        self.settingsButton.pack(side=LEFT)
        self.helpButton = Button(self.menu_area, width=10, height=2, text="Help")
        self.helpButton.pack(side=LEFT)






        self.text_area = Text(self.root, width=100, height=50, font=("Arial", 17), bg="#333333", fg="#f0f0f0", insertbackground="#000000", undo=True, autoseparators=True, wrap=WORD)
        self.text_area.pack(fill=BOTH, expand=True)
        self.update_syntax_highlighting()

        
CodeEditor.init()

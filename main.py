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
        self.text_area.tag_remove('keyword', 1.0, END)
        self.text_area.tag_remove('brace', 1.0, END)
        self.text_area.tag_remove('variable', 1.0, END)
        self.text_area.tag_remove('function', 1.0, END)
        self.text_area.tag_remove('string', 1.0, END)

        keywords = ['class', 'def', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'import', 'from', 'in', 'is', 'not', 'and', 'or', 'True', 'False', 'None']
        for keyword in keywords:
            self.text_area.tag_add('keyword', f'1.0', f'end', regexp=f'\\b{keyword}\\b')

        self.text_area.tag_add('brace', 1.0, END, regexp=r'[{}()\[\]]')

        self.text_area.tag_add('string', 1.0, END, regexp=r'\".*?\"')
        self.text_area.tag_add('string', 1.0, END, regexp=r"\'.*?\'")

        self.text_area.tag_add('variable', 1.0, END, regexp=r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')
        self.text_area.tag_add('function', 1.0, END, regexp=r'\b[a-zA-Z_][a-zA-Z0-9_]*\(.*?\)')

        self.root.after(100, self.update_syntax_highlighting)








    def __init__(self, root):
        self.root = root
        self.root.title("Code Editor")
        self.root.geometry("800x600")
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

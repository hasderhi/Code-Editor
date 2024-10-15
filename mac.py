try: 
    from tkinter import *
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import Toplevel, Text, WORD, END, DISABLED, Button
    import tkinter.font as tkfont
    import re
    import sys
    import os
    import subprocess
    import threading

except Exception as e:
    print(f"Error importing modules: {e}")
    try:
        from tkinter import messagebox
        messagebox.showerror("Error", f"Error importing modules: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error importing modules: {e}")
        sys.exit(1)

class CodeEditor:

    def init():
        root = Tk()
        CodeEditor(root)
        root.mainloop()

    
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
        
        self.autoSaveEnableButton = Button(self.menu_area, width=15, height=2, text="Enable autosave", command=self.auto_save)
        self.autoSaveEnableButton.pack(side=LEFT)
        self.saveAsButton = Button(self.menu_area, width=10, height=2, text="Save as", command=self.save_document)
        self.saveAsButton.pack(side=LEFT)
        self.saveButton = Button(self.menu_area, width=10, height=2, text="Save", command=self.save_changes)
        self.saveButton.pack(side=LEFT)
        self.saveButton = Button(self.menu_area, width=10, height=2, text="Open", command=self.open_document)
        self.saveButton.pack(side=LEFT)
        self.viewButton = Button(self.menu_area, width=10, height=2, text="Zoom", command=self.change_font_size)
        self.viewButton.pack(side=LEFT)
        self.runButton = Button(self.menu_area, width=10, height=2, text="Run", command=self.run_document)
        self.runButton.pack(side=LEFT)
        self.settingsButton = Button(self.menu_area, width=10, height=2, text="Settings")
        self.settingsButton.pack(side=LEFT)
        self.helpButton = Button(self.menu_area, width=10, height=2, text="Help")
        self.helpButton.pack(side=LEFT)





        self.text_area = Text(self.root, width=100, height=50, font=("Arial", 17), bg="#333333", fg="#f0f0f0", insertbackground="#f0f0f0", undo=True, autoseparators=True, wrap=WORD)
        self.text_area.pack(fill=BOTH, expand=True)
        font = tkfont.Font(font=self.text_area['font']) 
        tab_size = font.measure('       ') 
        self.text_area.config(tabs=tab_size)




        self.update_syntax_highlighting()



    def update_syntax_highlighting(self):
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
        self.text_area.tag_config('function', foreground='#ffcc00') # Yellow
        self.text_area.tag_config('variable', foreground='#66CCCC') # Light blue-green
        self.text_area.tag_config('brace', foreground='#D4D4D4')    # Light gray
        self.text_area.tag_config('builtin', foreground='#9A6CD9')  # Purple
        self.text_area.tag_config('number', foreground='#FF69B4')   # Pink

        self.root.after(100, self.update_syntax_highlighting)

    def save_document(self):
        # Save the current document to a file
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python scripts", "*.py"), ("Standard Text Files", "*.txt"), ("All Files", "*.*")], initialfile='untitled.py')
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_area.get("1.0", "end-1c"))
                self.current_file_path = file_path
        else:
            return
    
    def save_changes(self):
        # Save the current document to a file
        try:
            with open(self.current_file_path, "w") as file:
                file.write(self.text_area.get("1.0", "end-1c"))
        except:
            self.save_document()
        
    def auto_save(self):
        # Save the current document to a file
        self.save_changes()
        self.root.after(10000, self.auto_save)

    def open_document(self):
        file_path = filedialog.askopenfilename(defaultextension=".py", filetypes=[("Python scripts", "*.py"), ("Standard Text Files", "*.txt"), ("All Files", "*.*")])
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










    def run_document(self):
        if hasattr(self, 'current_file_path') and self.current_file_path:
            file_path = self.current_file_path
            if os.path.exists(file_path) and file_path.endswith('.py'):
                # Create and show the output window
                output_window = Toplevel(self.root)
                output_window.title("Python Output")
                output_text = Text(output_window, wrap=WORD, width=80, height=20)
                output_text.pack(padx=10, pady=10)
                
                stop_button = Button(output_window, text="Stop Execution", command=lambda: stop_execution())
                stop_button.pack(pady=5)

                process = None

                def run_script():
                    nonlocal process
                    try:
                        # Use sys.executable to get the path to the current Python executable
                        process = subprocess.Popen([sys.executable, file_path], 
                                                stdout=subprocess.PIPE, 
                                                stderr=subprocess.PIPE, 
                                                text=True, 
                                                bufsize=1, 
                                                universal_newlines=True)
                        
                        while True:
                            output = process.stdout.readline()
                            if output == '' and process.poll() is not None:
                                break
                            if output:
                                output_text.insert(END, output)
                                output_text.see(END)
                            
                        return_code = process.poll()
                        if return_code != 0:
                            error_output = process.stderr.read()
                            output_text.insert(END, f"\nError Output:\n{error_output}")
                        
                    except Exception as e:
                        output_text.insert(END, f"Error: {str(e)}")
                        
                    finally:
                        stop_button.config(state="disabled")
                        output_text.config(state=DISABLED)

                def stop_execution():
                    nonlocal process
                    if process:
                        process.terminate()

                # Run the script in a separate thread
                threading.Thread(target=run_script, daemon=True).start()

            else:
                messagebox.showerror("Error", "The current file is not a Python file or doesn't exist.")
        else:
            messagebox.showwarning("Warning", "Please save the file as a Python file before running.")






                                               
                                               




    def change_font_size(self):
        # Create toplevel with slider for font size selection between 1 and 100
        top = Toplevel(self.root)
        top.geometry("300x100")
        top.title("Change Font Size")
        Label(top, text="Font Size:").pack()
        self.slider = Scale(top, from_=1, to=100, orient=HORIZONTAL, command=self.update_font_size)
        self.slider.set(17)
        self.slider.pack()
        Button(top, text="OK", command=top.destroy).pack()
    





    def update_font_size(self, value):
        # Update the font size of the text area
        self.text_area.config(font=("Arial", int(value)))







    
        
CodeEditor.init()

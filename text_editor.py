#!/usr/bin/python3
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, simpledialog
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
from pygments.token import Token
import os

class TextEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Text Editor")
        self.geometry("800x600")
        self.font = ('Monospace', 12)
        self.filename = None
        self.modified = False
        self._setup_widgets()
        self._setup_keybindings()
        self._update_line_numbers()
        self._update_status_bar()

    def _setup_widgets(self):
        self.style = ttk.Style(self)
        self.style.theme_use('default')
        self.text_frame = ttk.Frame(self)
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        self.line_numbers = tk.Canvas(self.text_frame, borderwidth=0, highlightthickness=0, width=20, background='#171421')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text = tk.Text(self.text_frame, wrap=tk.NONE, borderwidth=0, highlightthickness=0, background='#171421', foreground='#D0CFCC', selectbackground='#D0CFCC', selectforeground='#171421', insertbackground='#D0CFCC', undo=True, yscrollcommand=self._on_text_scroll_y, font=self.font)
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.bind("<<Modified>>", self._on_modified)
        self.status = ttk.Label(self, anchor='w')
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        self.text.focus_set()

    def _setup_keybindings(self):
        self.bind("<Control-n>", lambda e: self._new_file())
        self.bind("<Control-e>", lambda e: self._open_file())
        self.bind("<Control-s>", lambda e: self._save_file())
        self.bind("<Control-S>", lambda e: self._save_file_as())
        self.bind("<Control-q>", lambda e: self.quit())
        self.bind("<Control-f>", lambda e: self._find())
        self.bind("<Control-h>", lambda e: self._replace())
        self.bind("<Control-l>", lambda e: self._goto_line())

    def _on_modified(self, event=None):
        self.modified = self.text.edit_modified()
        self._update_line_numbers()
        self._update_status_bar()
        self.text.edit_modified(False)

    def _on_text_scroll_y(self, *args):
        self.line_numbers.yview_moveto(args[0])
        self._update_line_numbers()

    def _update_line_numbers(self):
        self.line_numbers.delete("all")
        index = self.text.index("@0,0")
        line_count = int(self.text.index('end-1c').split('.')[0])
        digits = len(str(line_count))
        font_str = self.text['font']
        font_obj = tkfont.Font(font=font_str)
        digit_width = font_obj.measure('9')
        new_width = digit_width * digits + 10
        self.line_numbers.config(width=new_width)
        while True:
            dline = self.text.dlineinfo(index)
            if dline is None: break
            y = dline[1]  # vertical pixel position of the line
            line_number = index.split('.')[0]
            self.line_numbers.create_text(
                self.line_numbers.winfo_width() - 4,
                y,
                fill='#D0CFCC',
                anchor="ne",  # north-east to align right
                text=line_number,
                font=self.text['font']
            )
            index = self.text.index(f"{index}+1line")


    def _update_status_bar(self):
        row, col = self.text.index(tk.INSERT).split('.')
        name = os.path.basename(self.filename) if self.filename else "Untitled"
        if self.modified:
            name += "*"
        self.status.config(text=f"{name}    Ln {row}, Col {int(col)+1}", background='black', foreground='white', font=self.font)

    def _new_file(self):
        self.filename = None
        self.text.delete(1.0, tk.END)
        self.modified = False
        self._update_status_bar()

    def _open_file(self):
        path = filedialog.askopenfilename()
        if path:
            with open(path, 'r', encoding='utf-8') as file:
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, file.read())
            self.filename = path
            self.modified = False
            self.text.see('end')
            self.text.mark_set('insert', 'end')
            self.text.focus()
            self._update_status_bar()

    def _save_file(self):
        if self.filename:
            with open(self.filename, 'w', encoding='utf-8') as file:
                file.write(self.text.get(1.0, tk.END))
            self.modified = False
            self._update_status_bar()
        else:
            self._save_file_as()

    def _save_file_as(self):
        path = filedialog.asksaveasfilename()
        if path:
            self.filename = path
            self._save_file()

    def _find(self):
        term = simpledialog.askstring("Find", "Find:")
        if term:
            self.text.tag_remove("found", "1.0", tk.END)
            idx = "1.0"
            while True:
                idx = self.text.search(term, idx, nocase=1, stopindex=tk.END)
                if not idx:
                    break
                lastidx = f"{idx}+{len(term)}c"
                self.text.tag_add("found", idx, lastidx)
                idx = lastidx
            self.text.tag_config("found", background='yellow', foreground="black")

    def _replace(self):
        find = simpledialog.askstring("Replace", "Find:")
        replace = simpledialog.askstring("Replace", "Replace with:")
        if find and replace is not None:
            content = self.text.get(1.0, tk.END)
            content = content.replace(find, replace)
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, content)

    def _goto_line(self):
        line = simpledialog.askinteger("Go to line", "Line number:")
        if line:
            self.text.mark_set(tk.INSERT, f"{line}.0")
            self.text.see(f"{line}.0")

if __name__ == "__main__":
    app = TextEditor()
    app.mainloop()

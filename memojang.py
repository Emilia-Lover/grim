
import tkinter as tk
from tkinter import filedialog, messagebox

def new_file():
    text.delete(1.0, tk.END)
    root.title("메모장")

def open_file():
    path = filedialog.askopenfilename(filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")])
    if path:
        with open(path, "r", encoding="utf-8") as f:
            text.delete(1.0, tk.END)
            text.insert(1.0, f.read())
        
        root.title(f"메모장 - {path}")

def save_file():
    path = filedialog.asksaveasfilename(defaultextension=".txt",
                                         filetypes=[("텍스트 파일", "*.txt")])
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.get(1.0, tk.END))
        root.title(f"메모장 - {path}")

root = tk.Tk()
root.title("메모장")
root.geometry("800x600")


menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="새 파일", accelerator="Ctrl+N", command=new_file)
file_menu.add_command(label="열기", accelerator="Ctrl+O", command=open_file)
file_menu.add_command(label="저장", accelerator="Ctrl+S", command=save_file)

file_menu.add_separator()
file_menu.add_command(label="종료", command=root.quit)
menubar.add_cascade(label="파일", menu=file_menu)
root.config(menu=menubar)

root.bind("<Control-n>", lambda event: new_file())
root.bind("<Control-o>", lambda event: open_file())
root.bind("<Control-s>", lambda event: save_file())

frame = tk.Frame(root)

frame.pack(fill=tk.BOTH, expand=True)
scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text = tk.Text(frame, font=("맑은 고딕", 12), yscrollcommand=scrollbar.set, wrap=tk.WORD)
text.pack(fill=tk.BOTH, expand=True)

scrollbar.config(command=text.yview)


root.mainloop()
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tab2SQL")
        self.geometry("1200x600")

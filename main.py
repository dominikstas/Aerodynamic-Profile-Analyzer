import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.gui import AirfoilGUI

def main():
    try:
        root = tk.Tk()
        
        
        ico = Image.open('gui/ikona.png')
        photo = ImageTk.PhotoImage(ico)
        root.wm_iconphoto(False, photo)
        
        app = AirfoilGUI(root)
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
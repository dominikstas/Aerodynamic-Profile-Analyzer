import sys
import os
import tkinter as tk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui.gui import AirfoilGUI

def test_gui_launch():
    root = tk.Tk()
    app = AirfoilGUI(root)
    assert isinstance(app, AirfoilGUI)
    assert hasattr(app, 'selected_profile')
    root.destroy()

import sys
import os
import customtkinter as ctk
import pywinstyles

# Ensure the root folder is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.main_window import MainWindow

def main():
    ctk.set_appearance_mode("dark")
    
    # Load custom macOS-inspired theme
    theme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "macos_theme.json")
    ctk.set_default_color_theme(theme_path)
    
    app = MainWindow()
    
    # Apply native Windows Mica Dark titlebar for a seamless dark look
    pywinstyles.apply_style(app, "mica")
    app.wm_attributes("-alpha", 0.99)  # Workaround to force Mica render
    
    app.mainloop()

if __name__ == "__main__":
    main()

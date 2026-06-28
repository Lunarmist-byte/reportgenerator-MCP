import webbrowser
import customtkinter as ctk
from src.ui.settings_page import SettingsPage
from src.ui.generator_page import GeneratorPage

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title("Report Studio")
        self.geometry("1100x750")
        self.minsize(900, 600)
        self.configure(fg_color="#171717")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)


        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1e1e1e")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(5, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=20, pady=(28, 8), sticky="ew")
        
        ctk.CTkLabel(
            brand_frame, text="✦", font=ctk.CTkFont(size=22),
            text_color="#0a84ff" 
        ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            brand_frame, text="Report Studio", 
            font=ctk.CTkFont(family="Segoe UI Variable", size=18, weight="bold"),
            text_color="#f5f5f7"
        ).pack(side="left")

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#323232", corner_radius=0).grid(
            row=1, column=0, sticky="ew", padx=20, pady=(16, 20)
        )

        self.nav_buttons = []
        nav_items = [
            ("📝  Studio", self.show_generator),
            ("⚙️  Settings", self.show_settings),
        ]
        for i, (label, cmd) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w",
                fg_color="transparent", hover_color="#2a2a2a",
                text_color="#d1d1d6", font=ctk.CTkFont(size=14, weight="normal"),
                height=38, corner_radius=6, command=cmd
            )
            btn.grid(row=2 + i, column=0, padx=16, pady=4, sticky="ew")
            self.nav_buttons.append(btn)


        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.grid(row=5, column=0, padx=16, pady=(0, 24), sticky="s")
        
        ctk.CTkLabel(
            footer, text="Made by Lunarmist-byte",
            font=ctk.CTkFont(size=12, weight="normal"), text_color="#8e8e93"
        ).pack(pady=(0, 6))
        
        links_frame = ctk.CTkFrame(footer, fg_color="transparent")
        links_frame.pack()
        
        gh_lbl = ctk.CTkLabel(
            links_frame, text="GitHub", font=ctk.CTkFont(size=11, underline=True), 
            text_color="#0a84ff", cursor="hand2"
        )
        gh_lbl.pack(side="left", padx=8)
        gh_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Lunarmist-byte"))
        
        li_lbl = ctk.CTkLabel(
            links_frame, text="LinkedIn", font=ctk.CTkFont(size=11, underline=True), 
            text_color="#0a84ff", cursor="hand2"
        )
        li_lbl.pack(side="left", padx=8)
        li_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://www.linkedin.com/in/amal-s-kumar-ba69a1290/"))


        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="#171717")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.generator_page = GeneratorPage(self.content)
        self.settings_page = SettingsPage(self.content)

        self.show_generator()


    def _select_nav(self, index):
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.configure(fg_color="#323232", text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color="#d1d1d6")

    def show_generator(self):
        self.settings_page.grid_forget()
        self._select_nav(0)
        self.generator_page.grid(row=0, column=0, sticky="nsew", padx=32, pady=32)

    def show_settings(self):
        self.generator_page.grid_forget()
        self._select_nav(1)
        self.settings_page.grid(row=0, column=0, sticky="nsew", padx=32, pady=32)

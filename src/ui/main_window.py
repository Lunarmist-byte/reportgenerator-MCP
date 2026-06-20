import customtkinter as ctk
from src.ui.settings_page import SettingsPage
from src.ui.generator_page import GeneratorPage

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Report Generator")
        self.geometry("1100x750")
        self.minsize(900, 600)

        # Root grid: sidebar | content
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Sidebar ──────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1c1c1e")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(5, weight=1)  # push footer down
        self.sidebar.grid_columnconfigure(0, weight=1)

        # App icon / branding area
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=16, pady=(24, 4), sticky="ew")
        ctk.CTkLabel(
            brand_frame, text="✦", font=ctk.CTkFont(size=22),
            text_color="#0a84ff"
        ).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            brand_frame, text="AI Reports", 
            font=ctk.CTkFont(family="Segoe UI Variable", size=17, weight="bold"),
            text_color="#f5f5f7"
        ).pack(side="left")

        # Divider
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#3a3a3c", corner_radius=0).grid(
            row=1, column=0, sticky="ew", padx=16, pady=(16, 12)
        )

        # Nav buttons
        self.nav_buttons = []
        nav_items = [
            ("📝  Generator", self.show_generator),
            ("⚙️  Settings", self.show_settings),
        ]
        for i, (label, cmd) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w",
                fg_color="transparent", hover_color="#3a3a3c",
                text_color="#f5f5f7", font=ctk.CTkFont(size=14),
                height=36, corner_radius=8, command=cmd
            )
            btn.grid(row=2 + i, column=0, padx=12, pady=2, sticky="ew")
            self.nav_buttons.append(btn)

        # Footer
        ctk.CTkLabel(
            self.sidebar, text="lunarmist-byte\ntinkerhub ce-alappuzha",
            font=ctk.CTkFont(size=10), text_color="#636366", justify="center"
        ).grid(row=5, column=0, padx=16, pady=(0, 16), sticky="s")

        # ── Content area ─────────────────────────────────────
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="#1c1c1e")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Pages
        self.generator_page = GeneratorPage(self.content)
        self.settings_page = SettingsPage(self.content)

        self.show_generator()

    # ── Navigation ────────────────────────────────────────
    def _select_nav(self, index):
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.configure(fg_color="#3a3a3c")
            else:
                btn.configure(fg_color="transparent")

    def show_generator(self):
        self.settings_page.grid_forget()
        self._select_nav(0)
        self.generator_page.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)

    def show_settings(self):
        self.generator_page.grid_forget()
        self._select_nav(1)
        self.settings_page.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)

import customtkinter as ctk
import tkinter.messagebox
from src.core.storage import load_settings, save_settings


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.settings = load_settings()
        self.grid_columnconfigure(0, weight=1)
        self.init_ui()

    def init_ui(self):
        row = 0

        # ── Header ────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Settings",
            font=ctk.CTkFont(family="Segoe UI Variable", size=26, weight="bold"),
            text_color="#f5f5f7"
        ).grid(row=row, column=0, sticky="w", pady=(0, 4)); row += 1

        ctk.CTkLabel(
            self, text="Configure your LLM API keys and default provider.",
            font=ctk.CTkFont(size=13), text_color="#8e8e93"
        ).grid(row=row, column=0, sticky="w", pady=(0, 24)); row += 1

        # ── API Keys Card ─────────────────────────────────
        card = ctk.CTkFrame(self, fg_color="#2c2c2e", corner_radius=12)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 20)); row += 1
        card.grid_columnconfigure(1, weight=1)

        keys_data = [
            ("OpenAI", "openai_api_key"),
            ("Gemini", "gemini_api_key"),
            ("OpenRouter", "openrouter_api_key"),
        ]
        self.key_entries = {}

        for i, (label, key) in enumerate(keys_data):
            ctk.CTkLabel(
                card, text=label, font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#f5f5f7"
            ).grid(row=i, column=0, padx=(20, 12), pady=(16 if i == 0 else 8, 8 if i < len(keys_data)-1 else 16), sticky="w")

            entry = ctk.CTkEntry(card, show="•", placeholder_text=f"Enter {label} API key...")
            entry.insert(0, self.settings.get(key, ""))
            entry.grid(row=i, column=1, padx=(0, 20), pady=(16 if i == 0 else 8, 8 if i < len(keys_data)-1 else 16), sticky="ew")
            self.key_entries[key] = entry

        # ── Provider Card ─────────────────────────────────
        prov_card = ctk.CTkFrame(self, fg_color="#2c2c2e", corner_radius=12)
        prov_card.grid(row=row, column=0, sticky="ew", pady=(0, 28)); row += 1
        prov_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            prov_card, text="Default Provider",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#f5f5f7"
        ).grid(row=0, column=0, padx=(20, 12), pady=16, sticky="w")

        self.model_select = ctk.CTkOptionMenu(
            prov_card, values=["openai", "gemini", "openrouter"], width=200
        )
        self.model_select.set(self.settings.get("default_model", "openai"))
        self.model_select.grid(row=0, column=1, padx=(0, 20), pady=16, sticky="w")

        # ── Save Button ───────────────────────────────────
        ctk.CTkButton(
            self, text="Save Settings", command=self.save_settings,
            height=40, corner_radius=10, font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, sticky="w")

    def save_settings(self):
        for key, entry in self.key_entries.items():
            self.settings[key] = entry.get()
        self.settings["default_model"] = self.model_select.get()
        save_settings(self.settings)
        tkinter.messagebox.showinfo("Success", "Settings saved locally.")

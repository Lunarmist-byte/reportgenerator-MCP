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


        ctk.CTkLabel(
            self, text="Settings",
            font=ctk.CTkFont(family="Segoe UI Variable", size=26, weight="bold"),
            text_color="#f5f5f7"
        ).grid(row=row, column=0, sticky="w", pady=(0, 4)); row += 1

        ctk.CTkLabel(
            self, text="Configure your LLM API keys and default provider.",
            font=ctk.CTkFont(size=13), text_color="#8e8e93"
        ).grid(row=row, column=0, sticky="w", pady=(0, 24)); row += 1


        card = ctk.CTkFrame(self, fg_color="#252526", corner_radius=12)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 20)); row += 1
        card.grid_columnconfigure(1, weight=1)

        keys_data = [
            ("OpenAI", "openai_api_key"),
            ("Gemini", "gemini_api_key"),
            ("OpenRouter", "openrouter_api_key"),
        ]
        self.key_entries = {}
        self.test_btns = {}

        for i, (label, key) in enumerate(keys_data):
            ctk.CTkLabel(
                card, text=label, font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#f5f5f7"
            ).grid(row=i, column=0, padx=(20, 12), pady=(16 if i == 0 else 8, 8 if i < len(keys_data)-1 else 16), sticky="w")

            entry = ctk.CTkEntry(card, show="•", placeholder_text=f"Enter {label} API key...")
            entry.insert(0, self.settings.get(key, ""))
            entry.grid(row=i, column=1, padx=(0, 12), pady=(16 if i == 0 else 8, 8 if i < len(keys_data)-1 else 16), sticky="ew")
            self.key_entries[key] = entry
            
            test_btn = ctk.CTkButton(
                card, text="Test", width=100, height=28,
                fg_color="#323232", hover_color="#454545",
                command=lambda p=label.lower(), k=key: self.test_key(p, k)
            )
            test_btn.grid(row=i, column=2, padx=(0, 20), pady=(16 if i == 0 else 8, 8 if i < len(keys_data)-1 else 16))
            self.test_btns[key] = test_btn


        prov_card = ctk.CTkFrame(self, fg_color="#252526", corner_radius=12)
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
        
        ctk.CTkLabel(
            prov_card, text="OpenRouter Model",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#f5f5f7"
        ).grid(row=1, column=0, padx=(20, 12), pady=(0, 16), sticky="w")
        
        self.or_model_entry = ctk.CTkEntry(prov_card, placeholder_text="e.g. anthropic/claude-3-haiku")
        self.or_model_entry.insert(0, self.settings.get("openrouter_model", "anthropic/claude-3-haiku"))
        self.or_model_entry.grid(row=1, column=1, padx=(0, 20), pady=(0, 16), sticky="ew")


        ctk.CTkButton(
            self, text="Save Settings", command=self.save_settings,
            height=40, corner_radius=10, font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, sticky="w")

    def save_settings(self):
        for key, entry in self.key_entries.items():
            self.settings[key] = entry.get()
        self.settings["default_model"] = self.model_select.get()
        self.settings["openrouter_model"] = self.or_model_entry.get().strip() or "anthropic/claude-3-haiku"
        save_settings(self.settings)
        tkinter.messagebox.showinfo("Success", "Settings saved locally.")

    def test_key(self, provider, key_name):
        entry = self.key_entries[key_name]
        btn = self.test_btns[key_name]
        key_val = entry.get().strip()
        
        if not key_val:
            btn.configure(text="No Key", fg_color="#ff3b30", hover_color="#ff3b30")
            self.after(2000, lambda: btn.configure(text="Test", fg_color="#323232", hover_color="#454545"))
            return
            
        btn.configure(text="Testing...", fg_color="#eab308", hover_color="#ca8a04")
        self.update()
            
        import threading
        from src.core.llm_engine import test_api_key
        
        def run_test():
            success, msg = test_api_key(provider, key_val)
            def update_ui():
                if success:
                    btn.configure(text="✓ Valid API", fg_color="#10b981", hover_color="#059669")
                else:
                    btn.configure(text="✗ Invalid API", fg_color="#ff3b30", hover_color="#dc2626")
                
                self.after(3000, lambda: btn.configure(text="Test", fg_color="#323232", hover_color="#454545"))
            
            self.after(0, update_ui)
                
        threading.Thread(target=run_test, daemon=True).start()

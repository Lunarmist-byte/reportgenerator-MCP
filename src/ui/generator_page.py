import os
import customtkinter as ctk
import tkinter.filedialog
import tkinter.colorchooser
import tkinter.messagebox
from src.ui.calibrator import CalibratorView
from src.core.storage import load_settings
from src.core.llm_engine import generate_report
from src.core.pdf_engine import create_pdf


class GeneratorPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.logo_path = None
        self.picture_paths = []
        self.csv_path = None
        self.text_color = "#ffffff"
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        self.init_ui()

    def init_ui(self):
        # ── LEFT COLUMN ───────────────────────────────────
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(2, weight=1)  # notes expands
        row = 0

        # Header
        ctk.CTkLabel(
            left, text="Report Generator",
            font=ctk.CTkFont(family="Segoe UI Variable", size=26, weight="bold"),
            text_color="#f5f5f7"
        ).grid(row=row, column=0, sticky="w", pady=(0, 4)); row += 1

        ctk.CTkLabel(
            left, text="Enter rough notes and let AI craft a polished PDF.",
            font=ctk.CTkFont(size=13), text_color="#8e8e93"
        ).grid(row=row, column=0, sticky="w", pady=(0, 16)); row += 1

        # Notes textbox
        self.notes_input = ctk.CTkTextbox(left, corner_radius=10)
        self.notes_input.grid(row=row, column=0, sticky="nsew", pady=(0, 16)); row += 1

        # ── Report Type Card ──────────────────────────────
        type_card = ctk.CTkFrame(left, fg_color="#2c2c2e", corner_radius=12)
        type_card.grid(row=row, column=0, sticky="ew", pady=(0, 12)); row += 1
        type_card.grid_columnconfigure((0, 1), weight=1)

        self.report_type_var = ctk.StringVar(value="Standard")

        ctk.CTkRadioButton(
            type_card, text="Standard", variable=self.report_type_var,
            value="Standard", font=ctk.CTkFont(size=13)
        ).grid(row=0, column=0, padx=20, pady=14, sticky="w")

        ctk.CTkRadioButton(
            type_card, text="Financial (Tabular)", variable=self.report_type_var,
            value="Financial", font=ctk.CTkFont(size=13)
        ).grid(row=0, column=1, padx=20, pady=14, sticky="w")

        # ── Typography Card ───────────────────────────────
        typo_card = ctk.CTkFrame(left, fg_color="#2c2c2e", corner_radius=12)
        typo_card.grid(row=row, column=0, sticky="ew", pady=(0, 12)); row += 1

        # Row 0: Format + Font
        ctk.CTkLabel(typo_card, text="Format", font=ctk.CTkFont(size=11), text_color="#8e8e93").grid(
            row=0, column=0, padx=(20, 4), pady=(14, 0), sticky="w"
        )
        self.format_combo = ctk.CTkOptionMenu(
            typo_card, values=["A4", "Letter", "Legal"], width=90,
            command=self.update_page_format
        )
        self.format_combo.grid(row=1, column=0, padx=(20, 12), pady=(4, 14), sticky="w")

        ctk.CTkLabel(typo_card, text="Font", font=ctk.CTkFont(size=11), text_color="#8e8e93").grid(
            row=0, column=1, padx=4, pady=(14, 0), sticky="w"
        )
        self.font_combo = ctk.CTkOptionMenu(
            typo_card, values=["Helvetica", "Times-Roman", "Courier"], width=130
        )
        self.font_combo.grid(row=1, column=1, padx=4, pady=(4, 14), sticky="w")

        ctk.CTkLabel(typo_card, text="Size", font=ctk.CTkFont(size=11), text_color="#8e8e93").grid(
            row=0, column=2, padx=4, pady=(14, 0), sticky="w"
        )
        self.size_combo = ctk.CTkOptionMenu(
            typo_card, values=[str(i) for i in range(8, 25)], width=65
        )
        self.size_combo.set("11")
        self.size_combo.grid(row=1, column=2, padx=4, pady=(4, 14), sticky="w")

        self.color_btn = ctk.CTkButton(
            typo_card, text="● Color", width=80, height=30,
            fg_color="#48484a", hover_color="#636366",
            command=self.select_color, corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.color_btn.grid(row=1, column=3, padx=(4, 20), pady=(4, 14), sticky="w")

        # ── Assets Card ───────────────────────────────────
        asset_card = ctk.CTkFrame(left, fg_color="#2c2c2e", corner_radius=12)
        asset_card.grid(row=row, column=0, sticky="ew", pady=(0, 12)); row += 1

        btn_style = dict(
            fg_color="#48484a", hover_color="#636366", height=32,
            corner_radius=8, font=ctk.CTkFont(size=12)
        )
        btn_frame = ctk.CTkFrame(asset_card, fg_color="transparent")
        btn_frame.grid(row=0, column=0, padx=20, pady=14, sticky="w")

        ctk.CTkButton(btn_frame, text="📎 Logo", command=self.select_logo, width=90, **btn_style).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_frame, text="🖼 Picture", command=self.add_picture, width=100, **btn_style).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_frame, text="📊 CSV", command=self.select_csv, width=90, **btn_style).pack(side="left")

        self.asset_label = ctk.CTkLabel(
            asset_card, text="No assets selected", text_color="#636366",
            font=ctk.CTkFont(size=12)
        )
        self.asset_label.grid(row=1, column=0, padx=20, pady=(0, 14), sticky="w")

        # ── Generate Button ───────────────────────────────
        self.generate_btn = ctk.CTkButton(
            left, text="Generate Report  →", height=44, corner_radius=10,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.generate_report_action
        )
        self.generate_btn.grid(row=row, column=0, sticky="ew", pady=(4, 0))

        # ── RIGHT COLUMN: Calibrator ──────────────────────
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            right, text="Logo Calibrator",
            font=ctk.CTkFont(size=15, weight="bold"), text_color="#f5f5f7"
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))
        ctk.CTkLabel(
            right, text="Drag to position · Scroll to resize",
            font=ctk.CTkFont(size=12), text_color="#636366"
        ).grid(row=0, column=0, sticky="e", pady=(0, 4))

        self.calibrator = CalibratorView(right)
        self.calibrator.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

    # ── Callbacks ─────────────────────────────────────────
    def update_page_format(self, text):
        self.calibrator.set_page_format(text)

    def select_color(self):
        color_code = tkinter.colorchooser.askcolor(title="Choose text color")[1]
        if color_code:
            self.text_color = color_code
            self.color_btn.configure(text=f"● Color", text_color=color_code)

    def select_logo(self):
        path = tkinter.filedialog.askopenfilename(
            title="Select Logo", filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if path:
            self.logo_path = path
            self.calibrator.set_logo(path)
            self._refresh_asset_label()

    def add_picture(self):
        paths = tkinter.filedialog.askopenfilenames(
            title="Add Pictures", filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if paths:
            self.picture_paths.extend(paths)
            self._refresh_asset_label()

    def select_csv(self):
        path = tkinter.filedialog.askopenfilename(
            title="Select CSV", filetypes=[("CSV Files", "*.csv")]
        )
        if path:
            self.csv_path = path
            self._refresh_asset_label()

    def _refresh_asset_label(self):
        parts = []
        if self.logo_path:
            parts.append(f"Logo: {os.path.basename(self.logo_path)}")
        if self.picture_paths:
            parts.append(f"{len(self.picture_paths)} picture(s)")
        if self.csv_path:
            parts.append(f"CSV: {os.path.basename(self.csv_path)}")
        self.asset_label.configure(
            text=" · ".join(parts) if parts else "No assets selected",
            text_color="#aeaeb2" if parts else "#636366"
        )

    # ── PDF Generation ────────────────────────────────────
    def generate_report_action(self):
        notes = self.notes_input.get("1.0", "end-1c").strip()
        if not notes:
            tkinter.messagebox.showwarning("Missing Notes", "Please enter some notes first.")
            return

        settings = load_settings()
        report_type = self.report_type_var.get()

        csv_data = None
        if self.csv_path and os.path.exists(self.csv_path):
            with open(self.csv_path, "r", encoding="utf-8") as f:
                csv_data = f.read()

        self.generate_btn.configure(text="Generating…", state="disabled")
        self.update()

        try:
            report_data = generate_report(settings, notes, report_type, csv_data)
            if not report_data:
                raise Exception("LLM returned no data.")

            save_path = tkinter.filedialog.asksaveasfilename(
                defaultextension=".pdf", title="Save PDF",
                filetypes=[("PDF Files", "*.pdf")]
            )
            if not save_path:
                self.generate_btn.configure(text="Generate Report  →", state="normal")
                return

            font_settings = {
                "family": self.font_combo.get(),
                "size": int(self.size_combo.get()),
                "color": self.text_color,
            }
            create_pdf(
                output_path=save_path,
                report_data=report_data,
                logo_path=self.logo_path,
                logo_coords=self.calibrator.get_pdf_coordinates(),
                logo_scale=self.calibrator.get_logo_scale(),
                picture_paths=self.picture_paths,
                page_format=self.format_combo.get(),
                font_settings=font_settings,
            )
            self.generate_btn.configure(text="Generate Report  →", state="normal")
            tkinter.messagebox.showinfo("Done", f"Report saved to:\n{save_path}")

        except Exception as e:
            self.generate_btn.configure(text="Generate Report  →", state="normal")
            tkinter.messagebox.showerror("Error", str(e))

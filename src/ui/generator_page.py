import os
import threading
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
        self.picture_paths = []
        self.csv_path = None
        self.text_color = "#000000"
        self.custom_font_path = None
        self.custom_page_format = None
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        self.init_ui()

    def init_ui(self):
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(2, weight=1)
        row = 0

        ctk.CTkLabel(
            left, text="Report Studio",
            font=ctk.CTkFont(family="Segoe UI Variable", size=26, weight="bold"),
            text_color="#f5f5f7"
        ).grid(row=row, column=0, sticky="w", pady=(0, 4)); row += 1

        ctk.CTkLabel(
            left, text="Draft your report and customize the layout.",
            font=ctk.CTkFont(size=13), text_color="#8e8e93"
        ).grid(row=row, column=0, sticky="w", pady=(0, 16)); row += 1

        self.notes_input = ctk.CTkTextbox(left, corner_radius=10)
        self.notes_input.grid(row=row, column=0, sticky="nsew", pady=(0, 16)); row += 1

        type_card = ctk.CTkFrame(left, fg_color="#252526", corner_radius=12)
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

        typo_card = ctk.CTkFrame(left, fg_color="#252526", corner_radius=12)
        typo_card.grid(row=row, column=0, sticky="ew", pady=(0, 12)); row += 1

        ctk.CTkLabel(typo_card, text="Format", font=ctk.CTkFont(size=11), text_color="#8e8e93").grid(
            row=0, column=0, padx=(20, 4), pady=(14, 0), sticky="w"
        )
        self.format_combo = ctk.CTkOptionMenu(
            typo_card, values=["A4", "Letter", "Legal", "Custom..."], width=90,
            command=self.update_page_format
        )
        self.format_combo.grid(row=1, column=0, padx=(20, 12), pady=(4, 14), sticky="w")

        ctk.CTkLabel(typo_card, text="Font", font=ctk.CTkFont(size=11), text_color="#8e8e93").grid(
            row=0, column=1, padx=4, pady=(14, 0), sticky="w"
        )
        self.font_combo = ctk.CTkOptionMenu(
            typo_card, values=["Helvetica", "Times-Roman", "Courier", "Custom..."], width=130,
            command=self.update_font
        )
        self.font_combo.grid(row=1, column=1, padx=4, pady=(4, 14), sticky="w")

        ctk.CTkLabel(typo_card, text="Size", font=ctk.CTkFont(size=11), text_color="#8e8e93").grid(
            row=0, column=2, padx=4, pady=(14, 0), sticky="w"
        )
        self.size_combo = ctk.CTkOptionMenu(
            typo_card, values=[str(i) for i in range(8, 25)], width=65,
            command=self.update_size
        )
        self.size_combo.set("11")
        self.size_combo.grid(row=1, column=2, padx=4, pady=(4, 14), sticky="w")

        self.color_btn = ctk.CTkButton(
            typo_card, text="● Color", width=80, height=30,
            fg_color="#323232", hover_color="#454545",
            command=self.select_color, corner_radius=8,
            font=ctk.CTkFont(size=12), text_color="#000000"
        )
        self.color_btn.grid(row=1, column=3, padx=(4, 20), pady=(4, 14), sticky="w")

        asset_card = ctk.CTkFrame(left, fg_color="#252526", corner_radius=12)
        asset_card.grid(row=row, column=0, sticky="ew", pady=(0, 12)); row += 1

        btn_style = dict(
            fg_color="#323232", hover_color="#454545", height=32,
            corner_radius=8, font=ctk.CTkFont(size=12)
        )
        btn_frame = ctk.CTkFrame(asset_card, fg_color="transparent")
        btn_frame.grid(row=0, column=0, padx=20, pady=14, sticky="w")

        ctk.CTkButton(btn_frame, text="🖼 Add Image", command=self.add_canvas_image, width=120, **btn_style).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_frame, text="📊 Select CSV", command=self.select_csv, width=100, **btn_style).pack(side="left")

        self.asset_label = ctk.CTkLabel(
            asset_card, text="No attachments", text_color="#a1a1aa",
            font=ctk.CTkFont(size=12)
        )
        self.asset_label.grid(row=1, column=0, padx=20, pady=(0, 14), sticky="w")

        btn_frame2 = ctk.CTkFrame(left, fg_color="transparent")
        btn_frame2.grid(row=row, column=0, sticky="ew", pady=(4, 0))
        btn_frame2.grid_columnconfigure((0, 1), weight=1)

        self.generate_btn = ctk.CTkButton(
            btn_frame2, text="Generate AI Content", height=44, corner_radius=10,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.generate_report_action
        )
        self.generate_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        
        self.export_btn = ctk.CTkButton(
            btn_frame2, text="Export PDF →", height=44, corner_radius=10,
            fg_color="#0a84ff", hover_color="#007aff",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.export_pdf_action
        )
        self.export_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            right, text="Canvas Items",
            font=ctk.CTkFont(size=15, weight="bold"), text_color="#f5f5f7"
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))
        ctk.CTkLabel(
            right, text="Right-Click to Add · Drag to Move",
            font=ctk.CTkFont(size=12), text_color="#636366"
        ).grid(row=0, column=0, sticky="e", pady=(0, 4))

        self.calibrator = CalibratorView(right)
        self.calibrator.base_font_size = int(self.size_combo.get())
        self.calibrator.base_font_family = self.font_combo.get()
        self.calibrator.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

    def update_page_format(self, text):
        if text == "Custom...":
            dialog = ctk.CTkInputDialog(text="Enter dimensions (width, height) in mm (e.g. 210, 297):", title="Custom Size")
            result = dialog.get_input()
            if result:
                try:
                    parts = result.split(",")
                    w_mm, h_mm = float(parts[0]), float(parts[1])
                    w_pt = (w_mm / 25.4) * 72
                    h_pt = (h_mm / 25.4) * 72
                    self.custom_page_format = (w_pt, h_pt)
                    self.calibrator.set_page_format((w_pt, h_pt))
                except Exception:
                    tkinter.messagebox.showerror("Error", "Invalid dimensions format.")
                    self.format_combo.set("A4")
                    self.custom_page_format = None
                    self.calibrator.set_page_format("A4")
            else:
                self.format_combo.set("A4")
                self.custom_page_format = None
                self.calibrator.set_page_format("A4")
        else:
            self.custom_page_format = None
            self.calibrator.set_page_format(text)

    def update_font(self, text):
        if text == "Custom...":
            path = tkinter.filedialog.askopenfilename(
                title="Select Custom Font", filetypes=[("TrueType Font", "*.ttf")]
            )
            if path:
                self.custom_font_path = path
                self.calibrator.base_font_family = "Custom..."
            else:
                self.font_combo.set("Helvetica")
                self.custom_font_path = None
                self.calibrator.base_font_family = "Helvetica"
        else:
            self.custom_font_path = None
            self.calibrator.base_font_family = text
            
        # Update existing items
        for page in self.calibrator.pages.values():
            for item in page:
                if item.get("type") in ("text", "table"):
                    item["font_family"] = self.calibrator.base_font_family
        self.calibrator._redraw_all()

    def update_size(self, size_str):
        self.calibrator.base_font_size = int(size_str)
        self.calibrator._redraw_all()

    def select_color(self):
        color_code = tkinter.colorchooser.askcolor(title="Choose text color")[1]
        if color_code:
            self.text_color = color_code
            self.color_btn.configure(text=f"● Color", text_color=color_code)

    def add_canvas_image(self):
        path = tkinter.filedialog.askopenfilename(
            title="Add Canvas Image", filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if path:
            self.calibrator.add_image(path, x_pct=0.5, y_pct=0.5)

    def select_csv(self):
        path = tkinter.filedialog.askopenfilename(
            title="Select CSV", filetypes=[("CSV Files", "*.csv")]
        )
        if path:
            self.csv_path = path
            self._refresh_asset_label()

    def _refresh_asset_label(self):
        parts = []
        if self.picture_paths:
            parts.append(f"{len(self.picture_paths)} picture(s)")
        if self.csv_path:
            parts.append(f"CSV: {os.path.basename(self.csv_path)}")
        self.asset_label.configure(
            text=" · ".join(parts) if parts else "No attachments",
            text_color="#d4d4d8" if parts else "#a1a1aa"
        )

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

        def run_generation():
            try:
                report_data = generate_report(settings, notes, report_type, csv_data)
                if not report_data:
                    raise Exception("LLM returned no data.")
                    
                def append_to_ui():
                    try:
                        self.calibrator.clear_generated()
                        y_offset = 0.05
                        
                        def place_and_get_offset(text, x_pct, scale=1.0, bold=False, padding=0.03, align="left"):
                            nonlocal y_offset
                            self.calibrator.add_text(text, x_pct=x_pct, y_pct=y_offset)
                            item = self.calibrator.pages[self.calibrator.current_page][-1]
                            item["scale"] = scale
                            item["bold"] = bold
                            item["color"] = self.text_color
                            item["align"] = align
                            self.calibrator._redraw_item(item)
                            
                            bbox = self.calibrator.canvas.bbox(item["canvas_id"])
                            if bbox:
                                h = bbox[3] - bbox[1]
                                y_offset += (h / self.calibrator.page_height) + padding
                            else:
                                y_offset += 0.08
                                
                        if "title" in report_data and report_data["title"]:
                            place_and_get_offset(report_data["title"], x_pct=0.1, scale=1.4, bold=True, padding=0.04, align="center")
                            
                        if "date" in report_data and report_data["date"]:
                            place_and_get_offset(report_data["date"], x_pct=0.1, scale=0.9, padding=0.04)
                            
                        for para in report_data.get("paragraphs", []):
                            if not para.strip(): continue
                            place_and_get_offset(para, x_pct=0.1, scale=1.0, padding=0.04)
                            
                        if report_data.get("table") and report_data["table"]:
                            self.calibrator.add_table(report_data["table"], x_pct=0.1, y_pct=y_offset)
                            item = self.calibrator.pages[self.calibrator.current_page][-1]
                            item["color"] = self.text_color
                            self.calibrator._redraw_item(item)
                            
                            bbox = self.calibrator.canvas.bbox(item["canvas_id"])
                            if bbox:
                                h = bbox[3] - bbox[1]
                                y_offset += (h / self.calibrator.page_height) + 0.04
                            else:
                                y_offset += 0.2
                                
                        self.generate_btn.configure(text="Generate AI Content", state="normal")
                        tkinter.messagebox.showinfo("Success", "AI Content has been added to your canvas!")
                    except Exception as e:
                        self.generate_btn.configure(text="Generate AI Content", state="normal")
                        tkinter.messagebox.showerror("Error rendering", str(e))
                
                self.after(0, append_to_ui)
    
            except Exception as e:
                def show_error():
                    self.generate_btn.configure(text="Generate AI Content", state="normal")
                    tkinter.messagebox.showerror("Error", str(e))
                self.after(0, show_error)
                
        threading.Thread(target=run_generation, daemon=True).start()
            
    def export_pdf_action(self):
        save_path = tkinter.filedialog.asksaveasfilename(
            defaultextension=".pdf", title="Save PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not save_path:
            return
            
        font_settings = {
            "family": self.font_combo.get(),
            "size": int(self.size_combo.get()),
            "color": self.text_color,
            "custom_path": self.custom_font_path
        }
        
        page_format = self.custom_page_format if self.custom_page_format else self.format_combo.get()
        
        self.export_btn.configure(text="Exporting...", state="disabled")
        self.update()
        
        try:
            create_pdf(
                output_path=save_path,
                report_data={},
                canvas_pages=self.calibrator.get_all_pages(),
                picture_paths=[],
                page_format=page_format,
                font_settings=font_settings,
            )
            self.export_btn.configure(text="Export PDF →", state="normal")
            tkinter.messagebox.showinfo("Done", f"Report saved to:\n{save_path}")
        except Exception as e:
            self.export_btn.configure(text="Export PDF →", state="normal")
            tkinter.messagebox.showerror("Export Error", str(e))

import customtkinter as ctk
from PIL import Image, ImageTk


class CalibratorView(ctk.CTkFrame):
    """A simulated page canvas where the user can drag-position and scroll-zoom their logo."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#2c2c2e", corner_radius=12, **kwargs)

        self.logo_path = None
        self.logo_image = None
        self.logo_photo = None
        self.logo_item = None
        self.logo_scale = 1.0
        self.current_pct_x = 0.8
        self.current_pct_y = 0.05
        self.drag_data = {"x": 0, "y": 0, "item": None}

        self.canvas = ctk.CTkCanvas(
            self, bg="#f5f5f7", highlightthickness=0, cursor="fleur"
        )
        self.canvas.pack(padx=16, pady=16, expand=True)

        self.canvas.tag_bind("logo", "<ButtonPress-1>", self._on_drag_start)
        self.canvas.tag_bind("logo", "<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)

        self.set_page_format("A4")

    # ── Page format ───────────────────────────────────────
    def set_page_format(self, format_name):
        formats = {
            "A4": (595.27, 841.89),
            "Letter": (612.0, 792.0),
            "Legal": (612.0, 1008.0),
        }
        if format_name not in formats:
            format_name = "A4"
        self.pdf_width, self.pdf_height = formats[format_name]

        self.page_width = 300
        self.page_height = int((self.pdf_height / self.pdf_width) * self.page_width)
        self.canvas.configure(width=self.page_width, height=self.page_height)

        if self.logo_path:
            self._redraw_logo()

    # ── Logo operations ───────────────────────────────────
    def set_logo(self, image_path):
        self.logo_path = image_path
        self.logo_scale = 1.0
        self.logo_image = Image.open(image_path)
        self.current_pct_x = 0.8
        self.current_pct_y = 0.05
        self._redraw_logo()

    def _redraw_logo(self):
        if not self.logo_image:
            return
        self.canvas.delete("logo")

        base_width = 80
        scaled_w = int(base_width * self.logo_scale)
        ratio = scaled_w / float(self.logo_image.size[0])
        scaled_h = max(1, int(self.logo_image.size[1] * ratio))

        resized = self.logo_image.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(resized)

        x = int(self.current_pct_x * self.page_width)
        y = int(self.current_pct_y * self.page_height)
        self.logo_item = self.canvas.create_image(
            x, y, anchor="nw", image=self.logo_photo, tags="logo"
        )

    # ── Drag events ───────────────────────────────────────
    def _on_drag_start(self, event):
        self.drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def _on_drag_motion(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.drag_data["item"], dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        coords = self.canvas.coords(self.logo_item)
        if coords:
            self.current_pct_x = coords[0] / self.page_width
            self.current_pct_y = coords[1] / self.page_height

    # ── Scroll-zoom ───────────────────────────────────────
    def _on_mouse_wheel(self, event):
        if not self.logo_item:
            return
        overlap = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if self.logo_item not in overlap:
            return

        factor = 1.1 if (getattr(event, "delta", 0) > 0 or getattr(event, "num", 0) == 4) else 1 / 1.1
        self.logo_scale = max(0.1, min(self.logo_scale * factor, 5.0))
        self._redraw_logo()

    # ── Public API ────────────────────────────────────────
    def get_pdf_coordinates(self):
        return (self.current_pct_x, self.current_pct_y)

    def get_logo_scale(self):
        return self.logo_scale

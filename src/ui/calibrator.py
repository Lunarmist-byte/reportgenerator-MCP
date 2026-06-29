import tkinter as tk
import tkinter.filedialog
import tkinter.simpledialog
import customtkinter as ctk
from PIL import Image, ImageTk

class CalibratorView(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#121214", corner_radius=12, **kwargs)

        self.pages = {1: []}
        self.current_page = 1
        
        self.editing_entry = None
        self.editing_window_id = None
        self.editing_item = None
        
        self.drag_data = {"x": 0, "y": 0, "item": None, "drawing": False, "start_x": 0, "start_y": 0}
        self.drawing_rect_id = None
        self.selected_item = None
        self.selection_rect_id = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.canvas_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.canvas_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.canvas = tk.Canvas(
            self.canvas_container, bg="#ffffff", highlightthickness=0, cursor="crosshair"
        )
        self.canvas.pack(expand=True, fill="none", anchor="center")

        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 16))
        
        self.prev_btn = ctk.CTkButton(self.pagination_frame, text="< Prev", width=60, command=self._prev_page, fg_color="#323232", hover_color="#454545")
        self.prev_btn.pack(side="left")
        
        self.page_label = ctk.CTkLabel(self.pagination_frame, text="Page 1", text_color="#d1d1d6", font=ctk.CTkFont(weight="bold"))
        self.page_label.pack(side="left", expand=True)
        
        self.next_btn = ctk.CTkButton(self.pagination_frame, text="Next >", width=60, command=self._next_page, fg_color="#323232", hover_color="#454545")
        self.next_btn.pack(side="right")

        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_drag_release)
        
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)

        self.canvas.bind("<Button-3>", self._show_context_menu)
        self.canvas.bind("<Button-2>", self._show_context_menu)

        self.canvas.bind("<Delete>", self._on_delete)
        self.canvas.bind("<BackSpace>", self._on_delete)

        self.set_page_format("A4")

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Add Image Here", command=self._add_image_at_mouse)
        self.context_menu.add_command(label="Add Text Here", command=self._add_text_at_mouse)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Edit Text", command=self._edit_text)
        self.context_menu.add_command(label="Toggle Bold", command=self._toggle_bold)
        self.context_menu.add_command(label="Toggle Italic", command=self._toggle_italic)
        self.context_menu.add_command(label="Toggle Underline", command=self._toggle_underline)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Item", command=self._on_delete)

        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self._update_pagination_ui()


    def _prev_page(self):
        if self.current_page > 1:
            self._select_item(None)
            self.current_page -= 1
            self._redraw_all()
            self._update_pagination_ui()

    def _next_page(self):
        self._select_item(None)
        self.current_page += 1
        if self.current_page not in self.pages:
            self.pages[self.current_page] = []
        self._redraw_all()
        self._update_pagination_ui()

    def _update_pagination_ui(self):
        self.page_label.configure(text=f"Page {self.current_page}")
        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")

    def _redraw_all(self):
        self.canvas.delete("all")
        self.selection_rect_id = None
        for item in self.pages[self.current_page]:
            self._redraw_item(item)


    def set_page_format(self, format_name):
        if isinstance(format_name, tuple):
            self.pdf_width, self.pdf_height = format_name
        else:
            formats = {
                "A4": (595.27, 841.89),
                "Letter": (612.0, 792.0),
                "Legal": (612.0, 1008.0),
            }
            if format_name not in formats:
                format_name = "A4"
            self.pdf_width, self.pdf_height = formats[format_name]

        self.page_width = int(self.pdf_width)
        self.page_height = int(self.pdf_height)
        self.canvas.configure(width=self.page_width, height=self.page_height)
        self._redraw_all()


    def _show_context_menu(self, event):
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

        overlap = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        items = [i for i in overlap if i != self.selection_rect_id]
        if items:
            self._select_item(items[-1])
        else:
            self._select_item(None)

        state = "normal" if self.selected_item else "disabled"
        self.context_menu.entryconfig("Delete Item", state=state)

        is_text = False
        if self.selected_item:
            for item in self.pages[self.current_page]:
                if item["canvas_id"] == self.selected_item:
                    is_text = (item["type"] == "text")
                    break
                    
        text_state = "normal" if is_text else "disabled"
        self.context_menu.entryconfig("Edit Text", state=text_state)
        self.context_menu.entryconfig("Toggle Bold", state=text_state)
        self.context_menu.entryconfig("Toggle Italic", state=text_state)
        self.context_menu.entryconfig("Toggle Underline", state=text_state)

        self.context_menu.tk_popup(event.x_root, event.y_root)

    def _add_image_at_mouse(self):
        path = tkinter.filedialog.askopenfilename(
            title="Select Logo/Image", filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if path:
            x_pct = self.last_mouse_x / self.page_width
            y_pct = self.last_mouse_y / self.page_height
            self.add_image(path, x_pct, y_pct)

    def _add_text_at_mouse(self):
        x_pct = self.last_mouse_x / self.page_width
        y_pct = self.last_mouse_y / self.page_height
        self.add_text("", x_pct, y_pct)
        item = self.pages[self.current_page][-1]
        self._start_inline_edit(item)

    def add_image(self, path, x_pct=0.5, y_pct=0.5):
        img = Image.open(path)
        item = {
            "type": "image",
            "path": path,
            "image": img,
            "x_pct": x_pct,
            "y_pct": y_pct,
            "scale": 1.0,
            "canvas_id": None,
            "photo": None
        }
        self.pages[self.current_page].append(item)
        self._redraw_item(item)
        self._select_item(item["canvas_id"])

    def add_text(self, text, x_pct=0.5, y_pct=0.5):
        item = {
            "type": "text",
            "text": text,
            "x_pct": x_pct,
            "y_pct": y_pct,
            "scale": 1.0,
            "font_family": "Helvetica",
            "bold": False,
            "italic": False,
            "underline": False,
            "color": "#000000",
            "canvas_id": None
        }
        self.pages[self.current_page].append(item)
        self._redraw_item(item)
        self._select_item(item["canvas_id"])


    def _redraw_item(self, item):
        if item.get("canvas_id"):
            self.canvas.delete(item["canvas_id"])

        x = int(item["x_pct"] * self.page_width)
        y = int(item["y_pct"] * self.page_height)

        if item["type"] == "image":
            base_width = 80
            scaled_w = max(1, int(base_width * item["scale"]))
            ratio = scaled_w / float(item["image"].size[0])
            scaled_h = max(1, int(item["image"].size[1] * ratio))

            resized = item["image"].resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
            item["photo"] = ImageTk.PhotoImage(resized)

            item["canvas_id"] = self.canvas.create_image(
                x, y, anchor="nw", image=item["photo"]
            )
        elif item["type"] == "text":
            base_size = 7
            scaled_size = max(4, int(base_size * item["scale"]))
            font_str = f"{item['font_family']} {scaled_size}"
            if item.get("bold"):
                font_str += " bold"
            if item.get("italic"):
                font_str += " italic"
            if item.get("underline"):
                font_str += " underline"

            item["canvas_id"] = self.canvas.create_text(
                x, y, anchor="nw", text=item["text"], font=font_str,
                fill=item["color"], width=int(self.page_width * item.get("w_pct", 0.8))
            )

    def _select_item(self, canvas_id):
        self.selected_item = canvas_id
        if self.selection_rect_id:
            self.canvas.delete(self.selection_rect_id)
            self.selection_rect_id = None
            if hasattr(self, 'handle_ids'):
                for h_id in self.handle_ids:
                    self.canvas.delete(h_id)
            self.handle_ids = {}

        if self.selected_item:
            bbox = self.canvas.bbox(self.selected_item)
            if bbox:
                self.selection_rect_id = self.canvas.create_rectangle(
                    bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2,
                    outline="#ff3b30", dash=(2, 2)
                )
                self._create_handles(bbox)

    def _create_handles(self, bbox):
        if not hasattr(self, 'handle_ids'):
            self.handle_ids = {}
            
        x1, y1, x2, y2 = bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        sz = 4
        
        positions = {
            "NW": (x1, y1), "N": (cx, y1), "NE": (x2, y1),
            "E": (x2, cy), "SE": (x2, y2), "S": (cx, y2),
            "SW": (x1, y2), "W": (x1, cy)
        }
        
        for pos, (hx, hy) in positions.items():
            h_id = self.canvas.create_rectangle(hx-sz, hy-sz, hx+sz, hy+sz, fill="#ff3b30", outline="white")
            self.handle_ids[h_id] = pos

    def _update_selection_box(self):
        if self.selected_item and self.selection_rect_id:
            bbox = self.canvas.bbox(self.selected_item)
            if bbox:
                x1, y1, x2, y2 = bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2
                self.canvas.coords(self.selection_rect_id, x1, y1, x2, y2)
                
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                sz = 4
                positions = {
                    "NW": (x1, y1), "N": (cx, y1), "NE": (x2, y1),
                    "E": (x2, cy), "SE": (x2, y2), "S": (cx, y2),
                    "SW": (x1, y2), "W": (x1, cy)
                }
                
                for h_id, pos in getattr(self, 'handle_ids', {}).items():
                    hx, hy = positions[pos]
                    self.canvas.coords(h_id, hx-sz, hy-sz, hx+sz, hy+sz)

    def _on_drag_start(self, event):
        self.canvas.focus_set()
        overlap = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        
        clicked_handle = None
        if hasattr(self, 'handle_ids'):
            for item_id in overlap:
                if item_id in self.handle_ids:
                    clicked_handle = item_id
                    break
                    
        if clicked_handle:
            self.drag_data["mode"] = "resize"
            self.drag_data["handle"] = self.handle_ids[clicked_handle]
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.drag_data["item"] = self.selected_item
            
            bbox = self.canvas.bbox(self.selected_item)
            self.drag_data["cx"] = (bbox[0] + bbox[2]) / 2
            self.drag_data["cy"] = (bbox[1] + bbox[3]) / 2
            return

        items = [i for i in overlap if i != self.selection_rect_id and (not hasattr(self, 'handle_ids') or i not in self.handle_ids)]
        if items:
            item_id = items[-1]
            self._select_item(item_id)
            self.drag_data["mode"] = "move"
            self.drag_data["item"] = item_id
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
        else:
            self._select_item(None)
            self.drag_data["item"] = None
            self.drag_data["mode"] = None

    def _on_drag_motion(self, event):
        if not self.drag_data.get("item"): return
        
        if self.drag_data.get("mode") == "resize":
            handle = self.drag_data["handle"]
            cx = self.drag_data["cx"]
            cy = self.drag_data["cy"]
            
            old_x = self.drag_data["x"]
            old_y = self.drag_data["y"]
            
            if handle in ("E", "W"):
                old_d = abs(old_x - cx)
                new_d = abs(event.x - cx)
            elif handle in ("N", "S"):
                old_d = abs(old_y - cy)
                new_d = abs(event.y - cy)
            else:
                old_d = ((old_x - cx)**2 + (old_y - cy)**2)**0.5
                new_d = ((event.x - cx)**2 + (event.y - cy)**2)**0.5
                
            if old_d > 5:
                factor = new_d / old_d
            else:
                factor = 1.0
                
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            
            for item in self.pages[self.current_page]:
                if item["canvas_id"] == self.drag_data["item"]:
                    bbox = self.canvas.bbox(item["canvas_id"])
                    if bbox:
                        old_w = bbox[2] - bbox[0]
                        old_h = bbox[3] - bbox[1]
                        cx_pct = item["x_pct"] + (old_w / 2) / self.page_width
                        cy_pct = item["y_pct"] + (old_h / 2) / self.page_height
                        
                        is_text = item.get("type") == "text"
                        if is_text and handle in ("E", "W"):
                            if handle == "E":
                                new_w = event.x - bbox[0]
                            else:
                                new_w = bbox[2] - event.x
                            item["w_pct"] = max(0.05, new_w / self.page_width)
                            if handle == "W":
                                dx = event.x - bbox[0]
                                item["x_pct"] += dx / self.page_width
                        else:
                            item["scale"] = max(0.1, min(item.get("scale", 1.0) * factor, 5.0))
                        
                        self._redraw_item(item)
                        
                        new_bbox = self.canvas.bbox(item["canvas_id"])
                        if new_bbox:
                            new_w = new_bbox[2] - new_bbox[0]
                            new_h = new_bbox[3] - new_bbox[1]
                            if not (is_text and handle in ("E", "W")):
                                item["x_pct"] = cx_pct - (new_w / 2) / self.page_width
                                item["y_pct"] = cy_pct - (new_h / 2) / self.page_height
                            
                            self._redraw_item(item)
                            self._select_item(item["canvas_id"])
                            self.drag_data["item"] = item["canvas_id"]
                    break
        elif self.drag_data.get("mode") == "move":
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["item"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self._update_selection_box()
            
            dx_pct = dx / self.page_width
            dy_pct = dy / self.page_height
            for item in self.pages[self.current_page]:
                if item["canvas_id"] == self.drag_data["item"]:
                    item["x_pct"] += dx_pct
                    item["y_pct"] += dy_pct
                    break
                        
    def _on_drag_release(self, event):
        pass

    def _on_mouse_wheel(self, event):
        if not self.selected_item:
            return

        factor = 1.1 if (getattr(event, "delta", 0) > 0 or getattr(event, "num", 0) == 4) else 1 / 1.1

        for item in self.pages[self.current_page]:
            if item["canvas_id"] == self.selected_item:
                bbox = self.canvas.bbox(item["canvas_id"])
                if bbox:
                    old_w = bbox[2] - bbox[0]
                    old_h = bbox[3] - bbox[1]
                    cx_pct = item["x_pct"] + (old_w / 2) / self.page_width
                    cy_pct = item["y_pct"] + (old_h / 2) / self.page_height
                    
                    item["scale"] = max(0.1, min(item.get("scale", 1.0) * factor, 5.0))
                    
                    self._redraw_item(item)
                    
                    new_bbox = self.canvas.bbox(item["canvas_id"])
                    if new_bbox:
                        new_w = new_bbox[2] - new_bbox[0]
                        new_h = new_bbox[3] - new_bbox[1]
                        item["x_pct"] = cx_pct - (new_w / 2) / self.page_width
                        item["y_pct"] = cy_pct - (new_h / 2) / self.page_height
                        
                        self._redraw_item(item)
                        self._select_item(item["canvas_id"])
                break


    def _edit_text(self):
        for item in self.pages[self.current_page]:
            if item["canvas_id"] == self.selected_item and item["type"] == "text":
                self._start_inline_edit(item)
                break
                
    def _on_double_click(self, event):
        if self.selected_item:
            for item in self.pages[self.current_page]:
                if item["canvas_id"] == self.selected_item and item["type"] == "text":
                    self._start_inline_edit(item)
                    break
                    
    def _start_inline_edit(self, item):
        if self.editing_entry:
            self._finish_inline_edit(None)
            
        self.editing_item = item
        x = int(item["x_pct"] * self.page_width)
        y = int(item["y_pct"] * self.page_height)
        
        base_size = 14
        scaled_size = max(4, int(base_size * item["scale"]))
        font_str = f"{item['font_family']} {scaled_size}"
        
        self.editing_entry = tk.Text(self.canvas, font=font_str, fg=item["color"], bg="#ffffff", bd=1, relief="solid", wrap="word")
        self.editing_entry.insert("1.0", item["text"])
        
        pixel_width = int(self.page_width * item.get("w_pct", 0.8))
        bbox = self.canvas.bbox(item["canvas_id"])
        pixel_height = max(100, (bbox[3] - bbox[1]) + 20) if bbox else 100
        
        self.editing_window_id = self.canvas.create_window(x, y, anchor="nw", window=self.editing_entry, width=pixel_width, height=pixel_height)
        self.editing_entry.focus_set()
        
        self.editing_entry.bind("<FocusOut>", self._finish_inline_edit)

    def _finish_inline_edit(self, event):
        if not self.editing_entry or not self.editing_item:
            return
            
        new_text = self.editing_entry.get("1.0", "end-1c")
        if new_text.strip() or new_text:
            self.editing_item["text"] = new_text
        else:
            if not self.editing_item["text"]:
                if self.editing_item in self.pages[self.current_page]:
                    self.pages[self.current_page].remove(self.editing_item)
                    self._select_item(None)
                    
        self.editing_entry.destroy()
        self.editing_entry = None
        self.canvas.delete(self.editing_window_id)
        self.editing_window_id = None
        
        if self.editing_item in self.pages[self.current_page]:
            self._redraw_item(self.editing_item)
            self._select_item(self.editing_item["canvas_id"])
        
        self.editing_item = None

    def _toggle_bold(self):
        for item in self.pages[self.current_page]:
            if item["canvas_id"] == self.selected_item and item["type"] == "text":
                item["bold"] = not item.get("bold", False)
                self._redraw_item(item)
                self._select_item(item["canvas_id"])
                break
                
    def _toggle_italic(self):
        for item in self.pages[self.current_page]:
            if item["canvas_id"] == self.selected_item and item["type"] == "text":
                item["italic"] = not item.get("italic", False)
                self._redraw_item(item)
                self._select_item(item["canvas_id"])
                break

    def _toggle_underline(self):
        for item in self.pages[self.current_page]:
            if item["canvas_id"] == self.selected_item and item["type"] == "text":
                item["underline"] = not item.get("underline", False)
                self._redraw_item(item)
                self._select_item(item["canvas_id"])
                break
                


    def _on_delete(self, event=None):
        if self.selected_item:
            for item in self.pages[self.current_page]:
                if item["canvas_id"] == self.selected_item:
                    self.pages[self.current_page].remove(item)
                    self.canvas.delete(item["canvas_id"])
                    break
            self._select_item(None)


    def get_all_pages(self):
        return self.pages

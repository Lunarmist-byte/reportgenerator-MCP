from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QColor, QPen
from PyQt6.QtCore import Qt, QRectF, QPointF

class LogoItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, calibrator_ref):
        super().__init__(pixmap)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.calibrator_ref = calibrator_ref
        
    def itemChange(self, change, value):
        if change == QGraphicsPixmapItem.GraphicsItemChange.ItemPositionHasChanged:
            self.calibrator_ref.on_logo_moved(value)
        return super().itemChange(change, value)

class CalibratorView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Default page format (A4)
        self.set_page_format("A4")

    def set_page_format(self, format_name):
        formats = {
            "A4": (595.27, 841.89),
            "Letter": (612.0, 792.0),
            "Legal": (612.0, 1008.0)
        }
        if format_name not in formats:
            format_name = "A4"
            
        self.pdf_width, self.pdf_height = formats[format_name]
        
        # Scale to fit UI (say max width 400)
        self.page_width = 400
        self.page_height = int((self.pdf_height / self.pdf_width) * self.page_width)
        
        self.scene.setSceneRect(0, 0, self.page_width, self.page_height)
        self.setFixedSize(self.page_width + 10, self.page_height + 10)
        
        # Redraw background and border
        self.scene.clear()
        self.logo_item = None
        self.scene.addRect(0, 0, self.page_width, self.page_height, QPen(QColor("#cccccc")), QColor("#ffffff"))

        # We need to re-add the logo if it exists
        # In a real app we might store the path, but here the parent sets it again if needed.
        
        self.current_x = 0
        self.current_y = 0

    def set_logo(self, image_path):
        if self.logo_item:
            self.scene.removeItem(self.logo_item)
            
        self.logo_path = image_path
        pixmap = QPixmap(image_path)
        # Scale logo to reasonable default size, say 100px wide max
        pixmap = pixmap.scaledToWidth(100, Qt.TransformationMode.SmoothTransformation)
        self.logo_item = LogoItem(pixmap, self)
        self.scene.addItem(self.logo_item)
        self.logo_scale = 1.0
        self.logo_item.setScale(self.logo_scale)
        
        # Set default position (top right corner)
        self.logo_item.setPos(self.page_width - 120, 20)
        self.on_logo_moved(self.logo_item.pos())

    def wheelEvent(self, event):
        if self.logo_item and self.logo_item.isUnderMouse():
            # Zoom in or out
            zoom_in_factor = 1.1
            zoom_out_factor = 1 / zoom_in_factor
            
            if event.angleDelta().y() > 0:
                zoom_factor = zoom_in_factor
            else:
                zoom_factor = zoom_out_factor
                
            self.logo_scale *= zoom_factor
            
            # Constrain scale
            self.logo_scale = max(0.1, min(self.logo_scale, 5.0))
            self.logo_item.setScale(self.logo_scale)
        else:
            super().wheelEvent(event)

    def on_logo_moved(self, pos):
        # Calculate percentage position based on UI page size
        pct_x = pos.x() / self.page_width
        pct_y = pos.y() / self.page_height
        
        # In reportlab, bottom-left is (0,0). So we must invert Y.
        self.current_x = pct_x * self.pdf_width
        # For Y in reportlab, Y=842 is top, Y=0 is bottom
        # pct_y is 0 at top, 1 at bottom.
        # Reportlab Y = pdf_height - (pct_y * pdf_height) - image_height
        # We will let the PDF generator handle the exact math by providing the percentage
        self.current_pct_x = pct_x
        self.current_pct_y = pct_y

    def get_pdf_coordinates(self):
        """Returns the percentage position (x_pct, y_pct) of the top-left of the logo."""
        if not hasattr(self, 'current_pct_x'):
            return (0.8, 0.05) # Default approx top right
        return (self.current_pct_x, self.current_pct_y)

    def get_logo_scale(self):
        return self.logo_scale if hasattr(self, 'logo_scale') else 1.0

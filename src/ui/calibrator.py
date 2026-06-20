from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QColor, QPen
from PyQt6.QtCore import Qt, QRectF

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
        
        # A4 paper size in points is approx 595 x 842. 
        # We use a scaled down version for the UI, say 400 x 566
        self.page_width = 400
        self.page_height = 566
        self.scene.setSceneRect(0, 0, self.page_width, self.page_height)
        
        # Draw paper background
        self.setBackgroundBrush(QColor("#ffffff"))
        
        # Draw a border for the page
        self.scene.addRect(0, 0, self.page_width, self.page_height, QPen(QColor("#cccccc")))

        self.logo_item = None
        self.logo_scale = 1.0
        
        self.setFixedSize(self.page_width + 10, self.page_height + 10)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Coordinate mapping for PDF (PDF is 595 x 842)
        self.pdf_width = 595.27
        self.pdf_height = 841.89

        # Default position
        self.current_x = 0
        self.current_y = 0

    def set_logo(self, image_path):
        if self.logo_item:
            self.scene.removeItem(self.logo_item)
            self.logo_item = None
            
        pixmap = QPixmap(image_path)
        # Scale logo to reasonable default size, say 100px wide max
        pixmap = pixmap.scaledToWidth(100, Qt.TransformationMode.SmoothTransformation)
        self.logo_item = LogoItem(pixmap, self)
        self.scene.addItem(self.logo_item)
        
        # Set default position (top right corner)
        self.logo_item.setPos(self.page_width - 120, 20)
        self.on_logo_moved(self.logo_item.pos())

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

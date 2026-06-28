import os
from reportlab.lib.pagesizes import A4, LETTER, LEGAL
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
import PIL.Image as PILImage

def create_pdf(output_path, report_data, canvas_pages=None, picture_paths=None, page_format="A4", font_settings=None):
    format_map = {
        "A4": A4,
        "Letter": LETTER,
        "Legal": LEGAL
    }
    selected_pagesize = format_map.get(page_format, A4)
    w, h = selected_pagesize

    c = canvas.Canvas(output_path, pagesize=selected_pagesize)
    styles = getSampleStyleSheet()

    if not canvas_pages:
        canvas_pages = {1: []}
        
    for page_num, items in sorted(canvas_pages.items()):
        for item in items:
            item_type = item.get("type")
            if item_type == "image":
                path = item.get("path")
                scale = item.get("scale", 1.0)
                if path and os.path.exists(path):
                    try:
                        with PILImage.open(path) as img:
                            img_w, img_h = img.size
                            aspect = img_h / float(img_w)
                            logo_w = (80 / 300.0) * w * scale
                            logo_h = logo_w * aspect
                            x = item.get("x_pct", 0) * w
                            y_top = (1 - item.get("y_pct", 0)) * h
                            y = y_top - logo_h
                            c.drawImage(path, x, y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
                    except Exception as e:
                        print(f"Error drawing canvas image: {e}")
            elif item_type == "text":
                text_val = item.get("text", "")
                scale = item.get("scale", 1.0)
                color_hex = item.get("color", "#333333")
                bold = item.get("bold", False)
                italic = item.get("italic", False)
                font_family = item.get("font_family", "Helvetica")
                
                font_size_pct = (7 / 300.0) * scale
                scaled_size = font_size_pct * w
                
                font_name = font_family
                if bold and italic:
                    if font_family == "Times-Roman": font_name = "Times-BoldItalic"
                    elif font_family == "Courier": font_name = "Courier-BoldOblique"
                    else: font_name = f"{font_family}-BoldOblique"
                elif bold:
                    if font_family == "Times-Roman": font_name = "Times-Bold"
                    else: font_name = f"{font_family}-Bold"
                elif italic:
                    if font_family == "Times-Roman": font_name = "Times-Italic"
                    elif font_family == "Courier": font_name = "Courier-Oblique"
                    else: font_name = f"{font_family}-Oblique"
                    
                style = ParagraphStyle(
                    'CustomStyle',
                    parent=styles['Normal'],
                    fontName=font_name,
                    fontSize=scaled_size,
                    leading=scaled_size * 1.2,
                    textColor=colors.HexColor(color_hex)
                )
                
                formatted_text = str(text_val).replace('\n', '<br/>')
                
                if item.get("underline"):
                    formatted_text = f"<u>{formatted_text}</u>"
                    
                try:
                    p = Paragraph(formatted_text, style)
                    
                    wrap_width = w * item.get("w_pct", 0.8)
                    actual_w, actual_h = p.wrap(wrap_width, h)
                    
                    x = item.get("x_pct", 0) * w
                    y_top = (1 - item.get("y_pct", 0)) * h
                    y = y_top - actual_h
                    
                    p.drawOn(c, x, y)
                except Exception as e:
                    print(f"Error drawing text: {e}")
                    
        c.showPage()
        
    c.save()

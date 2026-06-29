import os
from reportlab.lib.pagesizes import A4, LETTER, LEGAL
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
import PIL.Image as PILImage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_pdf(output_path, report_data, canvas_pages=None, picture_paths=None, page_format="A4", font_settings=None):
    if isinstance(page_format, tuple):
        selected_pagesize = page_format
    else:
        format_map = {
            "A4": A4,
            "Letter": LETTER,
            "Legal": LEGAL
        }
        selected_pagesize = format_map.get(page_format, A4)
        
    w, h = selected_pagesize
    
    font_settings = font_settings or {}
    custom_font_path = font_settings.get("custom_path")
    has_custom_font = False
    if custom_font_path and os.path.exists(custom_font_path):
        try:
            pdfmetrics.registerFont(TTFont('CustomFont', custom_font_path))
            has_custom_font = True
        except Exception:
            pass

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
                    except Exception:
                        pass
            elif item_type == "text":
                text_val = item.get("text", "")
                scale = item.get("scale", 1.0)
                color_hex = item.get("color", "#000000")
                bold = item.get("bold", False)
                italic = item.get("italic", False)
                font_family = item.get("font_family", "Helvetica")
                
                base_size = font_settings.get("size", 14) if font_settings else 14
                scaled_size = max(4, int(base_size * scale))
                
                font_name = font_family
                if font_family == "Custom..." and has_custom_font:
                    font_name = "CustomFont"
                else:
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
                        
                align_val = item.get("align", "left")
                if align_val == "center":
                    alignment_enum = TA_CENTER
                elif align_val == "right":
                    alignment_enum = TA_RIGHT
                else:
                    alignment_enum = TA_LEFT
                    
                style = ParagraphStyle(
                    'CustomStyle',
                    parent=styles['Normal'],
                    fontName=font_name,
                    fontSize=scaled_size,
                    leading=scaled_size * 1.2,
                    textColor=colors.HexColor(color_hex),
                    alignment=alignment_enum
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
                except Exception:
                    pass
            elif item_type == "table":
                table_data = item.get("table_data", {})
                headers = table_data.get("headers", [])
                rows = table_data.get("rows", [])
                
                scale = item.get("scale", 1.0)
                base_size = font_settings.get("size", 14) if font_settings else 14
                scaled_size = max(4, int(base_size * scale))
                
                # We need to construct the data for the Table class
                # reportlab.platypus.Table expects a list of lists.
                table_grid = []
                if headers:
                    table_grid.append(headers)
                for row in rows:
                    table_grid.append(row)
                
                if not table_grid:
                    continue
                
                wrap_width = w * item.get("w_pct", 0.8)
                
                # Apply financial table styles
                style_commands = [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), f"{item.get('font_family', 'Helvetica')}-Bold"),
                    ('FONTSIZE', (0, 0), (-1, 0), scaled_size),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('FONTNAME', (0, 1), (-1, -1), item.get('font_family', 'Helvetica')),
                    ('FONTSIZE', (0, 1), (-1, -1), scaled_size),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#d1d5db")),
                ]
                
                t = Table(table_grid, width=wrap_width)
                t.setStyle(TableStyle(style_commands))
                
                # Note: Table objects don't wrap automatically like Paragraphs to calculate their height.
                # The wrap method is required to calculate the actual width and height required.
                actual_w, actual_h = t.wrap(wrap_width, h)
                
                x = item.get("x_pct", 0) * w
                y_top = (1 - item.get("y_pct", 0)) * h
                y = y_top - actual_h
                
                t.drawOn(c, x, y)
        c.showPage()
        
    c.save()

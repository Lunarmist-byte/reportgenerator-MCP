import os
from reportlab.lib.pagesizes import A4, LETTER, LEGAL
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def create_pdf(output_path, report_data, logo_path, logo_coords, logo_scale=1.0, picture_paths=None, page_format="A4", font_settings=None):
    """
    logo_coords: tuple (x_pct, y_pct) representing top-left corner of the logo
    logo_scale: float scale factor for the logo
    picture_paths: list of strings (paths to images)
    page_format: string ("A4", "Letter", "Legal")
    font_settings: dict with keys "family", "size", "color"
    """
    
    # Map format string to reportlab pagesize
    format_map = {
        "A4": A4,
        "Letter": LETTER,
        "Legal": LEGAL
    }
    selected_pagesize = format_map.get(page_format, A4)

    # We will use SimpleDocTemplate for the flowing text, but a custom canvas maker to draw the logo at exact absolute coordinates.
    class LogoCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            
        def showPage(self):
            # Draw Logo if provided
            if logo_path and os.path.exists(logo_path):
                w, h = selected_pagesize
                x_pct, y_pct = logo_coords
                
                # Assume base logo width is approx 100 points
                import PIL.Image as PILImage
                try:
                    with PILImage.open(logo_path) as img:
                        img_w, img_h = img.size
                        aspect = img_h / float(img_w)
                        logo_w = 100 * logo_scale
                        logo_h = logo_w * aspect
                        
                        x = x_pct * w
                        y_top = (1 - y_pct) * h
                        y = y_top - logo_h
                        
                        self.drawImage(logo_path, x, y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
                except Exception as e:
                    print(f"Error drawing logo: {e}")

            canvas.Canvas.showPage(self)

    doc = SimpleDocTemplate(output_path, pagesize=selected_pagesize,
                            rightMargin=72, leftMargin=72,
                            topMargin=100, bottomMargin=72)
    
    # Fallback font settings
    if font_settings is None:
        font_settings = {"family": "Helvetica", "size": 11, "color": "#333333"}
        
    base_font = font_settings.get("family", "Helvetica")
    base_size = font_settings.get("size", 11)
    text_color_hex = font_settings.get("color", "#333333")
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName=f"{base_font}-Bold" if base_font != "Times-Roman" else "Times-Bold",
        fontSize=base_size * 2,
        spaceAfter=20,
        textColor=colors.HexColor(text_color_hex)
    )
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontName=base_font,
        fontSize=base_size + 1,
        spaceAfter=30,
        textColor=colors.HexColor("#666666"),
        alignment=1 # Center
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName=base_font,
        fontSize=base_size,
        spaceAfter=14,
        leading=base_size * 1.5,
        textColor=colors.HexColor(text_color_hex)
    )

    story = []

    # Title
    if "title" in report_data:
        story.append(Paragraph(report_data["title"], title_style))
    
    # Date
    if "date" in report_data:
        story.append(Paragraph(report_data["date"], date_style))
        
    # Optional Pictures placed in flow
    if picture_paths:
        for pic in picture_paths:
            if os.path.exists(pic):
                try:
                    im = Image(pic, width=4*inch, height=3*inch)
                    im.hAlign = 'CENTER'
                    story.append(im)
                    story.append(Spacer(1, 20))
                except Exception as e:
                    print(f"Error drawing picture {pic}: {e}")
            
    # Paragraphs
    if "paragraphs" in report_data:
        for p in report_data["paragraphs"]:
            story.append(Paragraph(p, body_style))
            
    # Table (Financials)
    if "table" in report_data and report_data["table"]:
        table_data = []
        if "headers" in report_data["table"]:
            table_data.append(report_data["table"]["headers"])
        if "rows" in report_data["table"]:
            table_data.extend(report_data["table"]["rows"])
            
        if table_data:
            story.append(Spacer(1, 20))
            t = Table(table_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f0f0f0")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#333333")),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), f"{base_font}-Bold" if base_font != "Times-Roman" else "Times-Bold"),
                ('FONTSIZE', (0,0), (-1,0), base_size + 1),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.white),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#cccccc")),
                ('FONTNAME', (0,1), (-1,-1), base_font),
                ('FONTSIZE', (0,1), (-1,-1), base_size - 1),
            ]))
            story.append(t)

    doc.build(story, canvasmaker=LogoCanvas)

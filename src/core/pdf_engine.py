import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def create_pdf(output_path, report_data, logo_path, logo_coords, picture_path=None):
    """
    logo_coords: tuple (x_pct, y_pct) representing top-left corner of the logo
    """
    
    # We will use SimpleDocTemplate for the flowing text, but a custom canvas maker to draw the logo at exact absolute coordinates.
    class LogoCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            
        def showPage(self):
            # Draw Logo if provided
            if logo_path and os.path.exists(logo_path):
                # A4 size is 595.27 x 841.89 points
                w, h = A4
                x_pct, y_pct = logo_coords
                
                # Assume logo width is approx 100 points
                # Maintain aspect ratio
                import PIL.Image as PILImage
                try:
                    with PILImage.open(logo_path) as img:
                        img_w, img_h = img.size
                        aspect = img_h / float(img_w)
                        logo_w = 100
                        logo_h = logo_w * aspect
                        
                        # Calculate exact x, y. 
                        # reportlab bottom-left is (0,0)
                        # top-left of the image should be at (x_pct * w, (1 - y_pct) * h)
                        # So bottom-left of the image is at Y = top_left_Y - logo_h
                        x = x_pct * w
                        y_top = (1 - y_pct) * h
                        y = y_top - logo_h
                        
                        self.drawImage(logo_path, x, y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
                except Exception as e:
                    print(f"Error drawing logo: {e}")

            canvas.Canvas.showPage(self)

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=100, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        textColor=colors.HexColor("#333333")
    )
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=30,
        textColor=colors.HexColor("#666666"),
        alignment=1 # Center
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=14,
        leading=16
    )

    story = []

    # Title
    if "title" in report_data:
        story.append(Paragraph(report_data["title"], title_style))
    
    # Date
    if "date" in report_data:
        story.append(Paragraph(report_data["date"], date_style))
        
    # Optional Picture placed in flow
    if picture_path and os.path.exists(picture_path):
        try:
            im = Image(picture_path, width=4*inch, height=3*inch)
            im.hAlign = 'CENTER'
            story.append(im)
            story.append(Spacer(1, 20))
        except Exception as e:
            print(f"Error drawing picture: {e}")
            
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
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 12),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.white),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#cccccc")),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,1), (-1,-1), 10),
            ]))
            story.append(t)

    doc.build(story, canvasmaker=LogoCanvas)

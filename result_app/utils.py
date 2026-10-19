import pandas as pd
import io
import os
import uuid
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A5, landscape, portrait
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Line, Rect
from reportlab.graphics import renderPDF
from datetime import datetime
import tempfile

def process_excel(file):
    """Process uploaded Excel file and return data"""
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        raise Exception(f"Error reading Excel file: {str(e)}")

def calculate_gpa(marks, grading_system=None):
    """Calculate GPA based on marks"""
    if grading_system is None:
        grading_system = {
            'A+': {'min': 80, 'gpa': 5.00},
            'A': {'min': 70, 'gpa': 4.00},
            'A-': {'min': 60, 'gpa': 3.50},
            'B': {'min': 50, 'gpa': 3.00},
            'C': {'min': 40, 'gpa': 2.00},
            'D': {'min': 33, 'gpa': 1.00},
            'F': {'min': 0, 'gpa': 0.00}
        }
    
    for grade, criteria in grading_system.items():
        if marks >= criteria['min']:
            return grade, criteria['gpa']
    return 'F', 0.00

def calculate_grade(marks, grading_system=None):
    """Calculate grade based on marks"""
    grade, _ = calculate_gpa(marks, grading_system)
    return grade

def process_student_data(df, column_mapping):
    """Process student data and calculate results"""
    students = []
    total_subjects = len(column_mapping['subject_columns'])
    
    for _, row in df.iterrows():
        student = {
            'name': str(row[column_mapping['name_column']]),
            'roll': str(row[column_mapping['roll_column']]),
            'class': str(row[column_mapping['class_column']]),
            'shift': str(row[column_mapping['shift_column']]),
            'section': str(row[column_mapping['section_column']]),
            'semester': str(row[column_mapping['semester_column']]),
            'subjects': {}
        }
        
        marks = []
        for subject in column_mapping['subject_columns']:
            mark = row[subject]
            if pd.isna(mark):
                mark = 0
            mark = float(mark)
            marks.append(mark)
            student['subjects'][subject] = mark
        
        student['total'] = sum(marks)
        student['average'] = student['total'] / total_subjects if total_subjects > 0 else 0
        
        # Get both grade and GPA
        grade, gpa = calculate_gpa(student['average'])
        student['grade'] = grade
        student['gpa'] = float(gpa)
        
        students.append(student)
    
    # Calculate position/rank
    sorted_students = sorted(students, key=lambda x: x['total'], reverse=True)
    for i, student in enumerate(sorted_students, 1):
        student['position'] = i
    
    return students

def get_color_scheme(color_name):
    """Get color scheme based on selected color with modern palette"""
    color_schemes = {
        'blue': {
            'primary': colors.HexColor('#021024'),
            'secondary': colors.HexColor('#5483B3'),
            'light': colors.HexColor('#C1E8FF'),
            'lighter': colors.HexColor('#f2f8fe'),
            'border': colors.HexColor('#b9cfe3'),
            'text': colors.HexColor('#021024'),
            'accent': colors.HexColor('#7DA0C4'),
        },
        'green': {
            'primary': colors.HexColor('#1a6e3e'),
            'secondary': colors.HexColor('#27ae60'),
            'light': colors.HexColor('#eafaf1'),
            'lighter': colors.HexColor('#f7fdf9'),
            'border': colors.HexColor('#a8d5b5'),
            'text': colors.HexColor('#1a2a20'),
            'accent': colors.HexColor('#2ecc71'),
        },
        'red': {
            'primary': colors.HexColor('#7a1a1a'),
            'secondary': colors.HexColor('#e74c3c'),
            'light': colors.HexColor('#fdedec'),
            'lighter': colors.HexColor('#fdf7f7'),
            'border': colors.HexColor('#e5b3b3'),
            'text': colors.HexColor('#3a1a1a'),
            'accent': colors.HexColor('#e74c3c'),
        },
        'purple': {
            'primary': colors.HexColor('#4a1a7a'),
            'secondary': colors.HexColor('#8e44ad'),
            'light': colors.HexColor('#f4ecf7'),
            'lighter': colors.HexColor('#faf5fc'),
            'border': colors.HexColor('#d4b3e5'),
            'text': colors.HexColor('#2a1a3a'),
            'accent': colors.HexColor('#9b59b6'),
        },
        'orange': {
            'primary': colors.HexColor('#7a4a1a'),
            'secondary': colors.HexColor('#e67e22'),
            'light': colors.HexColor('#fef9e7'),
            'lighter': colors.HexColor('#fffdf7'),
            'border': colors.HexColor('#e5d4b3'),
            'text': colors.HexColor('#3a2a1a'),
            'accent': colors.HexColor('#f39c12'),
        }
    }
    return color_schemes.get(color_name, color_schemes['blue'])

def create_result_pdf(students, settings_obj, pdf_path=None):
    """Generate professional PDF with ReportLab"""
    if pdf_path is None:
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', f'result_{uuid.uuid4().hex[:8]}.pdf')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    # Get page size
    if hasattr(settings_obj, 'paper_size') and settings_obj.paper_size == 'A5':
        page_size = A5
    else:
        page_size = A4
    
    if hasattr(settings_obj, 'orientation') and settings_obj.orientation == 'landscape':
        page_size = landscape(page_size)
    
    # Create PDF
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=page_size,
        rightMargin=0.8*inch,
        leftMargin=0.8*inch,
        topMargin=0.6*inch,
        bottomMargin=0.6*inch,
    )
    
    # Get color scheme
    if hasattr(settings_obj, 'primary_color'):
        colors_theme = get_color_scheme(settings_obj.primary_color)
    else:
        colors_theme = get_color_scheme('blue')
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Modern custom styles
    school_name_style = ParagraphStyle(
        'SchoolNameStyle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors_theme['primary'],
        alignment=TA_CENTER,
        spaceAfter=2,
        fontName='Helvetica-Bold',
        letterSpacing=1,
    )
    
    address_style = ParagraphStyle(
        'AddressStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica',
    )
    
    result_title_style = ParagraphStyle(
        'ResultTitleStyle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors_theme['secondary'],
        alignment=TA_CENTER,
        spaceAfter=8,
        spaceBefore=4,
        fontName='Helvetica-Bold',
        letterSpacing=2,
    )
    
    info_label_style = ParagraphStyle(
        'InfoLabelStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        fontName='Helvetica-Bold',
    )
    
    info_value_style = ParagraphStyle(
        'InfoValueStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors_theme['text'],
        fontName='Helvetica',
    )
    
    subject_header_style = ParagraphStyle(
        'SubjectHeaderStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        letterSpacing=0.5,
    )
    
    subject_cell_style = ParagraphStyle(
        'SubjectCellStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors_theme['text'],
        fontName='Helvetica',
    )
    
    grade_chip_style = ParagraphStyle(
        'GradeChipStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#021024'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )
    
    summary_label_style = ParagraphStyle(
        'SummaryLabelStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        fontName='Helvetica',
        textTransform='uppercase',
        letterSpacing=0.5,
    )
    
    summary_value_style = ParagraphStyle(
        'SummaryValueStyle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors_theme['primary'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )
    
    position_style = ParagraphStyle(
        'PositionStyle',
        parent=styles['Normal'],
        fontSize=13,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        letterSpacing=1,
    )
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER,
        fontName='Helvetica',
        letterSpacing=0.3,
    )
    
    signature_style = ParagraphStyle(
        'SignatureStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors_theme['text'],
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=2,
    )
    
    # Build PDF content
    story = []
    
    for idx, student in enumerate(students):
        # --- Decorative header line ---
        header_line = Drawing(400, 3)
        header_line.add(Line(0, 0, 400, 0, strokeColor=colors_theme['secondary'], strokeWidth=2))
        header_line.hAlign = 'CENTER'
        story.append(header_line)
        story.append(Spacer(1, 0.05*inch))
        
        # --- School header ---
        header_content = []
        
        # Logo
        if hasattr(settings_obj, 'school_logo') and settings_obj.school_logo:
            try:
                logo_path = os.path.join(settings.MEDIA_ROOT, settings_obj.school_logo.name)
                if os.path.exists(logo_path):
                    img = Image(logo_path, width=0.8*inch, height=0.8*inch)
                    img.hAlign = 'CENTER'
                    header_content.append(img)
            except:
                pass
        
        school_name = getattr(settings_obj, 'school_name', 'Excellence Academy')
        school_address = getattr(settings_obj, 'school_address', '123 Education Blvd, Knowledge City')
        
        header_content.append(Paragraph(school_name, school_name_style))
        header_content.append(Paragraph(school_address, address_style))
        header_content.append(Spacer(1, 0.05*inch))
        header_content.append(Paragraph("ACADEMIC RESULT SHEET", result_title_style))
        
        # Decorative divider
        divider = Drawing(300, 2)
        divider.add(Line(0, 0, 300, 0, strokeColor=colors_theme['light'], strokeWidth=1))
        divider.hAlign = 'CENTER'
        header_content.append(divider)
        
        for element in header_content:
            story.append(element)
        
        story.append(Spacer(1, 0.1*inch))
        
        # --- Student info card ---
        info_data = [
            [Paragraph("Student Name", info_label_style), Paragraph(str(student['name']), info_value_style),
             Paragraph("Roll Number", info_label_style), Paragraph(str(student['roll']), info_value_style)],
            [Paragraph("Class", info_label_style), Paragraph(str(student['class']), info_value_style),
             Paragraph("Section", info_label_style), Paragraph(str(student['section']), info_value_style)],
            [Paragraph("Shift", info_label_style), Paragraph(str(student['shift']), info_value_style),
             Paragraph("Semester", info_label_style), Paragraph(str(student['semester']), info_value_style)],
        ]
        
        info_table = Table(info_data, colWidths=[1*inch, 1.8*inch, 1*inch, 1.8*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors_theme['lighter']),
            ('GRID', (0, 0), (-1, -1), 1, colors_theme['border']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.15*inch))
        
        # --- Subject marks table ---
        subject_data = [
            [Paragraph("Subject", subject_header_style), 
             Paragraph("Marks", subject_header_style),
             Paragraph("Grade", subject_header_style)]
        ]
        
        # Alternate row colors
        row_colors = [colors.white, colors_theme['lighter']]
        
        for i, (subject, marks) in enumerate(student['subjects'].items()):
            subject_grade, _ = calculate_gpa(marks)
            subject_data.append([
                Paragraph(str(subject), subject_cell_style),
                Paragraph(str(marks), subject_cell_style),
                Paragraph(f"<font color='#021024'><b>{subject_grade}</b></font>", grade_chip_style)
            ])
        
        subject_table = Table(subject_data, colWidths=[3.2*inch, 1.2*inch, 1.2*inch])
        subject_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors_theme['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), row_colors),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))
        story.append(subject_table)
        story.append(Spacer(1, 0.15*inch))
        
        # --- Summary statistics card ---
        total_value = str(student['total'])
        avg_value = f"{float(student['average']):.1f}" if isinstance(student['average'], (int, float)) else str(student['average'])
        gpa_value = f"{float(student['gpa']):.2f}" if isinstance(student['gpa'], (int, float)) else str(student['gpa'])
        
        summary_data = [
            [Paragraph("TOTAL", summary_label_style), Paragraph(total_value, summary_value_style)],
            [Paragraph("AVERAGE", summary_label_style), Paragraph(avg_value, summary_value_style)],
            [Paragraph("GRADE", summary_label_style), Paragraph(str(student['grade']), summary_value_style)],
            [Paragraph("GPA", summary_label_style), Paragraph(gpa_value, summary_value_style)],
        ]
        
        summary_table = Table(summary_data, colWidths=[1.2*inch, 1.2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors_theme['light']),
            ('GRID', (0, 0), (-1, -1), 1, colors_theme['border']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.1*inch))
        
        # --- Position badge ---
        position_data = [[Paragraph(f"🏆 POSITION: {student['position']}", position_style)]]
        
        position_table = Table(position_data, colWidths=[2.5*inch])
        position_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors_theme['primary']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('ROUNDEDCORNERS', [20, 20, 20, 20]),
        ]))
        
        # Center the position badge
        center_table = Table([[position_table]], colWidths=[5.6*inch])
        center_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(center_table)
        story.append(Spacer(1, 0.15*inch))
        
        # --- Footer with signature and seal ---
        footer_elements = []
        
        # Left: Date
        footer_elements.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y')}", footer_style))
        
        # Center: Signature
        sig_paragraphs = []
        if hasattr(settings_obj, 'signature_image') and settings_obj.signature_image:
            try:
                sig_path = os.path.join(settings.MEDIA_ROOT, settings_obj.signature_image.name)
                if os.path.exists(sig_path):
                    sig_img = Image(sig_path, width=1.2*inch, height=0.35*inch)
                    sig_img.hAlign = 'CENTER'
                    sig_paragraphs.append(sig_img)
            except:
                pass
        
        if not sig_paragraphs:
            # Draw signature line
            sig_line = Drawing(1.5*inch, 0.2*inch)
            sig_line.add(Line(0, 0.1*inch, 1.5*inch, 0.1*inch, strokeColor=colors_theme['text'], strokeWidth=1))
            sig_paragraphs.append(sig_line)
        
        sig_paragraphs.append(Paragraph("Principal's Signature", signature_style))
        
        # Wrap signature in a table to center it
        sig_table = Table([[sig_paragraphs]], colWidths=[2*inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Right: Seal
        seal_elements = []
        if hasattr(settings_obj, 'seal_image') and settings_obj.seal_image:
            try:
                seal_path = os.path.join(settings.MEDIA_ROOT, settings_obj.seal_image.name)
                if os.path.exists(seal_path):
                    seal_img = Image(seal_path, width=0.6*inch, height=0.6*inch)
                    seal_img.hAlign = 'RIGHT'
                    seal_elements.append(seal_img)
            except:
                pass
        
        # Footer table with three columns
        footer_table_data = [
            [footer_elements, sig_table, seal_elements]
        ]
        
        footer_table = Table(footer_table_data, colWidths=[1.8*inch, 2*inch, 1.8*inch])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(footer_table)
        story.append(Spacer(1, 0.05*inch))
        
        # --- Footer note ---
        story.append(Paragraph(
            "Generated by PixelIQ Result Generator | pixeliqit.com | Upgrade to a complete Institute Management System",
            footer_style
        ))
        
        # --- Bottom decorative line ---
        bottom_line = Drawing(400, 1)
        bottom_line.add(Line(0, 0, 400, 0, strokeColor=colors_theme['border'], strokeWidth=0.5))
        bottom_line.hAlign = 'CENTER'
        story.append(bottom_line)
        
        # Add page break except for last student
        if idx < len(students) - 1:
            story.append(PageBreak())
    
    # Build PDF
    def _brand_meta(canvas, doc):
        """Stamp PixelIQ branding into the PDF document metadata."""
        canvas.setTitle("PixelIQ Result Generator · Academic Result Sheet")
        canvas.setAuthor("PixelIQ · pixeliqit.com")
        canvas.setSubject("Student academic result sheet")
        canvas.setCreator("PixelIQ Result Generator (pixeliqit.com)")

    try:
        doc.build(story, onFirstPage=_brand_meta, onLaterPages=_brand_meta)
        return pdf_path
    except Exception as e:
        print(f"PDF Generation Error: {str(e)}")
        raise e

def generate_pdf(student_data, settings_data, pdf_file_path=None):
    """Wrapper function for PDF generation"""
    return create_result_pdf(student_data, settings_data, pdf_file_path)
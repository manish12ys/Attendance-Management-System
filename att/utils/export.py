import pandas as pd
import io
from fpdf import FPDF
from flask import send_file
from datetime import datetime

def export_to_excel(attendance_records, course=None, start_date=None, end_date=None):
    """
    Export attendance records to Excel
    """
    # Create a pandas DataFrame from the attendance records
    data = []
    for record in attendance_records:
        data.append({
            'Date': record.date.strftime('%d-%m-%Y'),
            'Student': record.user.name,
            'Course': f"{record.course.name} ({record.course.code})",
            'Section': 'N/A',  # Section relationship removed
            'Status': record.status,
            'Marked By': record.marked_by_user.name,
            'Time': record.marked_at.strftime('%H:%M')
        })

    df = pd.DataFrame(data)

    # Create a BytesIO object to store the Excel file
    output = io.BytesIO()

    # Create a Pandas Excel writer using the BytesIO object
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write the DataFrame to the Excel file
        df.to_excel(writer, sheet_name='Attendance Report', index=False)

        # Get the worksheet
        worksheet = writer.sheets['Attendance Report']

        # Set column widths
        for idx, col in enumerate(df.columns):
            column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = column_width

        # Add header with report information
        worksheet.insert_rows(0, 4)
        worksheet.cell(1, 1, 'Attendance Management System - Attendance Report')
        worksheet.cell(2, 1, f'Course: {course.name if course else "All Courses"}')
        worksheet.cell(3, 1, f'Period: {start_date.strftime("%d-%m-%Y")} to {end_date.strftime("%d-%m-%Y")}')
        worksheet.cell(4, 1, f'Generated on: {datetime.now().strftime("%d-%m-%Y %H:%M")}')

    # Seek to the beginning of the BytesIO object
    output.seek(0)

    # Create a filename for the Excel file
    filename = f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return output, filename

def export_to_pdf(attendance_records, course=None, start_date=None, end_date=None):
    """
    Export attendance records to PDF
    """
    # Create a PDF object
    pdf = FPDF()
    pdf.add_page()

    # Set font
    pdf.set_font('Arial', 'B', 16)

    # Add title
    pdf.cell(0, 10, 'Attendance Management System - Attendance Report', 0, 1, 'C')

    # Add report information
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Course: {course.name if course else "All Courses"}', 0, 1)
    pdf.cell(0, 10, f'Period: {start_date.strftime("%d-%m-%Y")} to {end_date.strftime("%d-%m-%Y")}', 0, 1)
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%d-%m-%Y %H:%M")}', 0, 1)

    # Add summary
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Summary', 0, 1)

    pdf.set_font('Arial', '', 12)
    total_records = len(attendance_records)
    present_count = len([r for r in attendance_records if r.status == 'present'])
    absent_count = len([r for r in attendance_records if r.status == 'absent'])
    late_count = len([r for r in attendance_records if r.status == 'late'])

    pdf.cell(0, 10, f'Total Records: {total_records}', 0, 1)
    pdf.cell(0, 10, f'Present: {present_count}', 0, 1)
    pdf.cell(0, 10, f'Absent: {absent_count}', 0, 1)
    pdf.cell(0, 10, f'Late: {late_count}', 0, 1)

    # Add detailed report
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Detailed Report', 0, 1)

    # Add table header
    pdf.set_font('Arial', 'B', 10)
    col_width = pdf.w / 6
    col_width = pdf.w / 7  # Adjust column width for 7 columns
    pdf.cell(col_width, 10, 'Date', 1, 0, 'C')
    pdf.cell(col_width, 10, 'Student', 1, 0, 'C')
    pdf.cell(col_width, 10, 'Course', 1, 0, 'C')
    pdf.cell(col_width, 10, 'Section', 1, 0, 'C')
    pdf.cell(col_width, 10, 'Status', 1, 0, 'C')
    pdf.cell(col_width, 10, 'Marked By', 1, 0, 'C')
    pdf.cell(col_width, 10, 'Time', 1, 1, 'C')

    # Add table data
    pdf.set_font('Arial', '', 10)
    for record in attendance_records:
        # Check if we need to add a new page
        if pdf.get_y() + 10 > pdf.h - 20:
            pdf.add_page()

            # Add table header again
            pdf.set_font('Arial', 'B', 10)
            col_width = pdf.w / 7  # Adjust column width for 7 columns
            pdf.cell(col_width, 10, 'Date', 1, 0, 'C')
            pdf.cell(col_width, 10, 'Student', 1, 0, 'C')
            pdf.cell(col_width, 10, 'Course', 1, 0, 'C')
            pdf.cell(col_width, 10, 'Section', 1, 0, 'C')
            pdf.cell(col_width, 10, 'Status', 1, 0, 'C')
            pdf.cell(col_width, 10, 'Marked By', 1, 0, 'C')
            pdf.cell(col_width, 10, 'Time', 1, 1, 'C')
            pdf.set_font('Arial', '', 10)

        pdf.cell(col_width, 10, record.date.strftime('%d-%m-%Y'), 1, 0, 'C')
        pdf.cell(col_width, 10, record.user.name, 1, 0, 'C')
        pdf.cell(col_width, 10, f"{record.course.name} ({record.course.code})", 1, 0, 'C')
        pdf.cell(col_width, 10, 'N/A', 1, 0, 'C')  # Section relationship removed
        pdf.cell(col_width, 10, record.status, 1, 0, 'C')
        pdf.cell(col_width, 10, record.marked_by_user.name, 1, 0, 'C')
        pdf.cell(col_width, 10, record.marked_at.strftime('%H:%M'), 1, 1, 'C')

    # Create a BytesIO object to store the PDF
    output = io.BytesIO()

    # Save the PDF to the BytesIO object
    pdf.output(output)

    # Seek to the beginning of the BytesIO object
    output.seek(0)

    # Create a filename for the PDF file
    filename = f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return output, filename

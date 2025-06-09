from django.http import HttpResponse
from django.utils import timezone
from .models import RoomReservation
import csv

def generate_reservations_report(request):
    # Create filename with timestamp
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reservations_report_{timestamp}.csv"

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    
    # Write CSV headers
    writer.writerow([
        'Reservation ID', 
        'Customer Name', 
        'Email', 
        'Phone', 
        'NIN',
        'Check-In Date', 
        'Check-Out Date', 
        'Nights', 
        'Status',
        'Room Number', 
        'Room Type', 
        'Price/Night', 
        'Total Price',
        'Reservation Date',
        'Special Requests',
        'Created By'
    ])

    # Get all reservations ordered by check-in date (newest first)
    reservations = RoomReservation.objects.select_related(
        'room', 
        'room__room_type', 
        'created_by'
    ).order_by('-check_in_date')

    # Write data rows
    for res in reservations:
        writer.writerow([
            res.reservation_id,
            res.customer or 'N/A',
            res.email or 'N/A',
            res.phone_number or 'N/A',
            res.NIN or 'N/A',
            res.check_in_date.strftime("%Y-%m-%d"),
            res.check_out_date.strftime("%Y-%m-%d"),
            res.total_nights,
            res.status,
            res.room.room_number,
            res.room.room_type.name,
            f"{res.room.price_per_night}" if res.room.price_per_night else "N/A",
            f"{res.total_price:.2f}" if res.total_price else "N/A",
            res.reservation_date.strftime("%Y-%m-%d %H:%M"),
            res.special_requests or 'None',
            res.created_by.username if res.created_by else 'System'
        ])

    return response


from io import BytesIO
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from .models import RoomReservation
from django.contrib.auth.decorators import login_required

@login_required
def generate_reservation_pdf(request, reservation_id):
    try:
        # Get reservation object
        reservation = get_object_or_404(RoomReservation, id=reservation_id)
        
        # Calculate important values
        total_nights = (reservation.check_out_date - reservation.check_in_date).days
        price_per_night = reservation.room.price_per_night
        
        # Create PDF buffer
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        
        # Set up styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = styles['Heading2']
        body_style = styles['BodyText']
        
        # PDF Content
        width, height = A4
        
        # Header
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawCentredString(width/2, height-50, "Mary Keeri Suites")
        pdf.setFont("Helvetica", 10)
        pdf.drawCentredString(width/2, height-70, "123 Hotel Street, Nairobi | Tel: 0782331553 | Email: info@marykeeri.com")
        
        # Title
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawCentredString(width/2, height-100, "RESERVATION CONFIRMATION")
        
        # Customer Information
        y_position = height-140
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y_position, "Guest Information:")
        y_position -= 20
        
        customer_info = [
            ["Name:", reservation.customer],
            ["Email:", reservation.email],
            ["Phone:", reservation.phone_number],
            ["NIN:", reservation.NIN]
        ]
        
        table = Table(customer_info, colWidths=[60, 400])
        table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        table.wrapOn(pdf, width, height)
        table.drawOn(pdf, 50, y_position-80)
        
        # Reservation Details
        y_position -= 140
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y_position, "Reservation Details:")
        y_position -= 20
        
        reservation_details = [
            ["Room Number:", str(reservation.room.room_number)],
            ["Check-in Date:", reservation.check_in_date.strftime("%d-%b-%Y")],
            ["Check-out Date:", reservation.check_out_date.strftime("%d-%b-%Y")],
            ["Total Nights:", str(total_nights)],
            ["Status:", reservation.status],
            ["Reservation Date:", reservation.reservation_date.strftime("%d-%b-%Y %H:%M")],
            ["Reservation ID:", str(reservation.reservation_id)]
        ]
        
        table = Table(reservation_details, colWidths=[100, 360])
        table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ]))
        table.wrapOn(pdf, width, height)
        table.drawOn(pdf, 50, y_position-100)
        
        # Payment Summary
        y_position -= 140
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y_position, "Payment Summary:")
        y_position -= 20
        
        payment_details = [
            ["Price per Night:", f"Ush {price_per_night:,.2f}"],
            ["Total Nights:", str(total_nights)],
            ["Total Price:", f"Ush {reservation.total_price:,.2f}"]
        ]
        
        table = Table(payment_details, colWidths=[100, 360])
        table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BACKGROUND', (2,0), (2,-1), colors.lightblue),
        ]))
        table.wrapOn(pdf, width, height)
        table.drawOn(pdf, 50, y_position-60)
        
        # Policies
        y_position -= 100
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y_position, "Hotel Policies:")
        y_position -= 20
        
        policies = [
            "1. Check-in time: 2:00 PM | Check-out time: 11:00 AM",
            "2. Cancellations must be made 48 hours prior to arrival",
            "3. Valid ID required at check-in",
            "4. No smoking in rooms",
            "5. Damages will be charged to the guest"
        ]
        
        for policy in policies:
            pdf.setFont("Helvetica", 10)
            pdf.drawString(60, y_position, policy)
            y_position -= 15
            
        # Footer
        pdf.setFont("Helvetica-Oblique", 9)
        pdf.drawString(50, 40, "Thank you for choosing Mary Keeri Suites!")
        pdf.drawString(50, 25, f"Document generated by: {reservation.created_by.get_full_name()}")
        
        # Save PDF
        pdf.showPage()
        pdf.save()
        
        # Prepare response
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"Reservation_{reservation_id}.pdf")
    
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)
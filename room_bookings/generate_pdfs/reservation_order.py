from io import BytesIO
from django.http import FileResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import letter
from room_bookings.models import *

# Printing Receipt for resevation
@login_required(login_url='/user/login/')
def print_reservation(request, id):
    # Create a buffer to hold the PDF data
    buffer = BytesIO()

    # Define the PDF size (57mm wide, height dynamically adjustable)
    receipt_width = 57 * mm
    initial_height = 100 * mm  # Base height
    line_height = 5 * mm  # Height for each line

    # Retrieve the order by ID and the related order items
    try:
        reservation_order = RoomReservation.objects.get(id=id)
    except reservation_order.DoesNotExist:
        return HttpResponse("Order not found.", status=404)

    # Dynamically calculate the receipt height based on content
    total_lines = 15  # Adjust this based on content (e.g., 15 lines = base height)
    receipt_height = initial_height + (line_height * total_lines)

    # Create the PDF canvas
    p = canvas.Canvas(buffer, pagesize=(receipt_width, receipt_height))

    # Set starting Y position near the top
    y = receipt_height - 10 * mm  # Start 10mm from the top

    # Business header
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(receipt_width / 2, y, "Mary Keeri Suites")
    y -= 6 * mm

    p.setFont("Helvetica", 10)
    p.drawCentredString(receipt_width / 2, y, "Tel: 0782331553 / 0741330555")
    y -= 6 * mm  # Decrement for spacing

    # Move email to a new line
    p.drawCentredString(receipt_width / 2, y, "Email: marykeerisuites@gmail.com")
    y -= 8 * mm

    # Receipt Title
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(receipt_width / 2, y, "RECEIPT")
    y -= 8 * mm

    # Order and customer details
    p.setFont("Helvetica", 9)
    p.drawString(5 * mm, y, f"Order ID: {reservation_order.id}")
    y -= 5 * mm
    p.drawString(5 * mm, y, f"Date: {reservation_order.reservation_date}")
    y -= 5 * mm
    p.drawString(5 * mm, y, f"Customer: {reservation_order.customer}")
    y -= 6 * mm

    # Items Section Header
    p.setFont("Helvetica-Bold", 9)
    p.drawString(5 * mm, y, "Room")
    p.drawString(25 * mm, y, "Nights")
    p.drawString(40 * mm, y, "Price")
    y -= 6 * mm

    # Items in the order
    p.setFont("Helvetica", 9)
    p.drawString(5 * mm, y, f"{reservation_order.room.room_number }")
    p.drawString(25 * mm, y, f"{reservation_order.total_nights}")
    p.drawString(40 * mm, y, f"{reservation_order.total_price:.2f}")
    y -= 6 * mm

    # Special Notes
    if reservation_order.special_requests:
        y -= 3 * mm  # Extra spacing for special notes section
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(5 * mm, y, "Special Notes:")
        y -= 4 * mm
        p.setFont("Helvetica", 8)
        p.drawString(5 * mm, y, reservation_order.special_requests)
        y -= 6 * mm

    # Footer
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(receipt_width / 2, y, "Thank you for dining with us!")
    y -= 5 * mm
    p.setFont("Helvetica", 8)
    p.drawCentredString(receipt_width / 2, y, f"Served by: {reservation_order.created_by}")

    # Finalize and close the PDF
    p.showPage()
    p.save()

    # Return PDF as response
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"receipt_{reservation_order.id}.pdf")

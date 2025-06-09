from io import BytesIO
from django.http import FileResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import letter
from room_bookings.models import *

# Printing Receipt for transaction
@login_required(login_url='/user/login/')
def print_sauna_order(request, id):
    # Create a buffer to hold the PDF data
    buffer = BytesIO()

    # Define the PDF size (57mm wide, height dynamically adjustable)
    receipt_width = 57 * mm
    initial_height = 100 * mm  # Base height
    line_height = 5 * mm  # Height for each line

    # Retrieve the order by ID and the related order items
    try:
        sauna_order = SaunaUser.objects.get(id=id)
    except sauna_order.DoesNotExist:
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
    y -= 8 * mm
    # Email Header
    p.setFont("Helvetica", 10)
    p.drawCentredString(receipt_width / 2, y, "Email: marykeerisuites@gmail.com")
    y -= 8 * mm
    # Receipt Title
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(receipt_width / 2, y, "RECEIPT")
    y -= 8 * mm


    # Order and customer details
    p.setFont("Helvetica", 9)
    p.drawString(5 * mm, y, f"Order ID: {sauna_order.id}")
    y -= 5 * mm
    p.drawString(5 * mm, y, f"Date: {sauna_order.order_date}")
    y -= 5 * mm
    p.drawString(5 * mm, y, f"Customer: {sauna_order.customer_name}")
    y -= 6 * mm

    # Items Section Header
    p.setFont("Helvetica-Bold", 9)
    p.drawString(5 * mm, y, "Service")
    p.drawString(25 * mm, y, "Keys")
    p.drawString(40 * mm, y, "Price")
    y -= 6 * mm

    # Items in the order
    p.setFont("Helvetica", 9)
    p.drawString(5 * mm, y, f"{sauna_order.service}")
    p.drawString(25 * mm, y, f"{sauna_order.keys}")
    p.drawString(40 * mm, y, f"{sauna_order.price:.2f}")
    y -= 6 * mm

    # # Special Notes
    # if sauna_order.gender:
    #     y -= 3 * mm  # Extra spacing for special notes section
    #     p.setFont("Helvetica-Oblique", 8)
    #     p.drawString(5 * mm, y, "Special Notes:")
    #     y -= 4 * mm
    #     p.setFont("Helvetica", 8)
    #     p.drawString(5 * mm, y, sauna_order.gender)
    #     y -= 6 * mm

    # Footer
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(receipt_width / 2, y, "Thank you for dining with us!")
    y -= 5 * mm
    p.setFont("Helvetica", 8)
    p.drawCentredString(receipt_width / 2, y, f"Served by: {sauna_order.created_by}")

    # Finalize and close the PDF
    p.showPage()
    p.save()

    # Return PDF as response
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"receipt_{sauna_order.id}.pdf")

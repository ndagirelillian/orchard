from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views import View
from core.models import Setting
from .forms import *
from .models import *
from django.db.models import Q
from datetime import datetime
from django.contrib import messages

# Create your views here.
def fetch_reservation_details(request, reservation_id):
    # Get the reservation object
    reservation = get_object_or_404(RoomReservation, id=reservation_id)

    # Prepare the data to be returned as JSON
    data = {
        "reservation_id": reservation.reservation_id,
        "customer": reservation.customer,
        "reservation_date": reservation.reservation_date,
        "room_number": reservation.room.room_npyumber,
        "total_nights": reservation.total_nights,
        "total_price": reservation.total_price,
        "check_in_date": reservation.check_in_date,
        "check_out_date": reservation.check_out_date,
        "status": reservation.status,
        "special_requests": reservation.special_requests or "None",
        "created_by": reservation.created_by,
    }

    return JsonResponse(data)


# ROOM TYPES VIEW
@login_required(login_url='/user/login/')
def rooms(request):
    room_types = RoomType.objects.all()
    return render(request, "roomtypes.html", {"room_types": room_types})



# FILTER ROOMS BY TYPE
@login_required(login_url='/user/login/')
def rooms_filter(request, id):
    rooms = Room.objects.filter(room_type=id, is_available=True)
    return render(request, "rooms.html", {"rooms": rooms})


# reservations/views.py
# def reservation_list(request):
#     reservations = RoomReservation.objects.select_related('booking').all()
#     return render(request, 'reservations/list.html', {'reservations': reservations})


# ROOM RESERVATION LIST VIEW
@login_required(login_url='/user/login/')
def reservation(request):
    reservations_list = RoomReservation.objects.all().select_related('booking').order_by('-reservation_date')
    paginator = Paginator(reservations_list, 10)
    
    # Get the page number from the request
    page_number = request.GET.get('page')

    # Get the corresponding page
    reservations_list = paginator.get_page(page_number)
    return render(request, "reservations.html", {"reservations_list": reservations_list})

# GET SPECIFIC RESERVATION VIEW
@login_required(login_url="/user/login/")
def getReservation(request, id):
    settings = Setting.objects.first()
    reservation = get_object_or_404(RoomReservation, id=id)
    return render(request, "getreservation.html", {"reservation": reservation, "setting": settings})

# ADD ROOM RESERVATION VIEW
@login_required(login_url='/user/login/')
def add_reservation(request):
    if request.method == 'POST':
        form = RoomReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.created_by = request.user
            reservation.save()
            return redirect('reservations')
    else:
        form = RoomReservationForm()

    return render(request, 'add_reservation.html', {'form': form})

#ADD CUSTOMER VIEW
@login_required(login_url='/user/login/')
def add_customer(request):
    if request.method == 'POST':
        form =CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_reservation')
    else:
        form = CustomerForm()

    return render(request, 'add_customer.html', {'form': form})

    
# Sauna
@login_required(login_url='/user/login/')
def add_sauna(request):
    if request.method == 'POST':
        form = SaunaUserForm(request.POST)
        if form.is_valid():
            sauna_order = form.save(commit=False)
            sauna_order.created_by = request.user
            sauna_order.save()

            return redirect('sauna_customers')
    else:
        form = SaunaUserForm()

    return render(request, 'add_sauna.html', {'form': form})

# all sauna_customers


@login_required(login_url='/user/login/')
def sauna_customers(request):
    saunacustomers = SaunaUser.objects.all()
    sauna_list = SaunaUser.objects.all().select_related(
        'service', 'created_by').order_by('-order_date')
    paginator = Paginator(sauna_list, 10)

    # Get the page number from the request
    page_number = request.GET.get('page')

    # Get the corresponding page
    sauna_list = paginator.get_page(page_number)

    return render(request, "sauna_customers.html", {"sauna_list": sauna_list})


# View for a single sauna customer's details
@login_required(login_url='/user/login/')
def get_sauna_customer(request, id):
    try:
        # Retrieve the sauna customer by their ID

        customer = get_object_or_404(SaunaUser, id=id)
    except SaunaUser.DoesNotExist:
        # If the customer doesn't exist, redirect to the sauna customers list with an error message
        return redirect('sauna_customers')

    # Render the customer's details in the template
    return render(request, 'eachsauna_customer.html', {'customer': customer})



class RoomManagementView(View):
    template_name = 'room_management.html'

    def get(self, request):
        room_type_form = RoomTypeForm()
        room_form = RoomForm()
        room_types = RoomType.objects.all()
        rooms = Room.objects.select_related('room_type').all()
        
        context = {
            'room_type_form': room_type_form,
            'room_form': room_form,
            'room_types': room_types,
            'rooms': rooms,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        if 'add_room_type' in request.POST:
            room_type_form = RoomTypeForm(request.POST, request.FILES)
            if room_type_form.is_valid():
                room_type_form.save()
                return redirect('room_management')
            # If invalid, fall through to render with errors
        
        elif 'add_room' in request.POST:
            room_form = RoomForm(request.POST, request.FILES)
            if room_form.is_valid():
                room_form.save()
                return redirect('room_management')
            # If invalid, fall through to render with errors
        
        # If neither form was submitted or forms were invalid
        room_type_form = room_type_form if 'add_room_type' in request.POST else RoomTypeForm()
        room_form = room_form if 'add_room' in request.POST else RoomForm()
        
        room_types = RoomType.objects.all()
        rooms = Room.objects.select_related('room_type').all()
        
        context = {
            'room_type_form': room_type_form,
            'room_form': room_form,
            'room_types': room_types,
            'rooms': rooms,
        }
        return render(request, self.template_name, context)
    
    

@login_required(login_url='/user/login/')
def update_reservation_status(request, pk):
    reservation = get_object_or_404(RoomReservation, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(RoomReservation.RESERVATION_STATUS_CHOICES):
            reservation.status = new_status
            reservation.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=405)


def roomBooking(request):
    available_rooms = Room.objects.all()

    # Check if filter parameters are present
    guests = request.GET.get('guests')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    if guests and check_in and check_out:
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

            # Filter based on capacity
            available_rooms = available_rooms.filter(capacity__gte=guests)

            # Exclude rooms already booked in the selected range
            overlapping_bookings = Booking.objects.filter(
                Q(check_in__lt=check_out_date) & Q(check_out__gt=check_in_date)
            ).values_list('room_id', flat=True)

            available_rooms = available_rooms.exclude(id__in=overlapping_bookings)

        except ValueError:
            pass  # Handle invalid date format

    return render(request, "room_booking.html", {
        'available_rooms': available_rooms
    })



def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            
            # Additional validation
            if booking.check_in >= booking.check_out:
                messages.error(request, "Check-out date must be after check-in date")
                return redirect('room_booking')
                
            if booking.guests > booking.room.capacity:
                messages.error(request, "Number of guests exceeds room capacity")
                return redirect('room_booking')
                
            # Check room availability
            overlapping_bookings = Booking.objects.filter(
                room=booking.room,
                check_in__lt=booking.check_out,
                check_out__gt=booking.check_in
            ).exists()
            
            if overlapping_bookings:
                messages.error(request, "Room is not available for the selected dates")
                return redirect('room_booking')
                
            booking.save()
            messages.success(request, "Booking created successfully! We will contact you by email in a short time.")
            return redirect('room_booking')
        else:
            # Form has errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    return redirect('room_booking')

def booked_rooms(request):
    bookings = Booking.objects.all().order_by('-booking_date')
    paginator = Paginator(bookings, 10)
    
    page_number= request.GET.get('page')
    
    bookings =  paginator.get_page(page_number)
    return render(request, 'booked_rooms.html', {'bookings':bookings})


def booking_detail(request, id):
    booking = get_object_or_404(Booking, id=id)

    return render(request, 'booking_detail.html', {'booking': booking})

#Convert booking to Reservations


def convert_to_reservation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status != 'reserved':
        booking.status = 'reserved'
        booking.save()
        messages.success(
            request, 'Booking converted to reservation successfully.')
    else:
        messages.info(request, 'Booking is already a reservation.')

    return redirect('booked_rooms')


# def confirm_booking(request, booking_id):
#     booking = Booking.objects.get(id=booking_id)
#     if booking.status != 'reserved':
#         reservation = booking.convert_to_reservation(user=request.user)
#         messages.success(
#             request, f"Booking confirmed and reservation created for {reservation.customer}")
#     else:
#         messages.info(
#             request, "This booking is already converted to a reservation.")
#     return redirect('booking_detail')


def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status != 'reserved':
        booking.status = 'reserved'
        booking.save()  # 🔁 This triggers the signal
        messages.success(
            request, "Booking confirmed and converted to reservation.")
    else:
        messages.info(request, "Already reserved.")

    return redirect('booking_detail', id=booking.id)


def reservation_detail(request, reservation_id):
    reservation = get_object_or_404(RoomReservation, id=reservation_id)
    return render(request, 'reservation_detail.html', {'reservation': reservation})




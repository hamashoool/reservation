from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.utils import timezone

from main.decorators import is_person
from main.forms import Booking, BookingFormm
from main.models import People, Table


@login_required
@is_person
def booking(request, pk, slug):
    table = Table.objects.get(pk=pk, slug=slug)
    if request.method == 'POST':
        try:
            people_instance = People.objects.get(user=request.user)
        except Table.DoesNotExist:
            people_instance = People(user=request.user)
        form = Booking(request.POST, instance=people_instance)
        tform = BookingFormm(request.POST or None, instance=request.user)
        try:
            if form.is_valid() and tform.is_valid():
                user = tform.save(commit=False)
                tbl = table
                if tbl.booked == True:
                    tbl.refresh_from_db()
                    messages.error(request, "Sorry! This table is already taken. You can't book it.")
                    return render(request, 'main/booking.html', {'form': form, 'tform': tform})
                else:
                    tbl.booked = True
                    tbl.booked_by = request.user
                tbl.save()
                user.save()
                user = form.save(commit=False)
                user.refresh_from_db()
                user.user = request.user
                user.phone = form.cleaned_data.get('phone')
                user.date = timezone.now()
                user.address = form.cleaned_data.get('address')
                user.save()
                return redirect('tables')
        except IntegrityError as e:
            if 'UNIQUE constraint' in str(e.args):
                messages.error(request, 'You are not able to make booking again.')
                return render(request, 'main/booking.html', {'form': form, 'tform': tform})
    else:
        form = Booking()
        tform = BookingFormm()
    return render(request, 'main/booking.html', {'form': form, 'tform': tform})


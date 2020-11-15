from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, render_to_response
from django.views.generic import UpdateView, ListView

from main.models import Table, Restaurant
from .decorators import is_person
from .forms import SignUpForm, CustomUserForm, UserUpdateForm, UserModelUpdateForm, CancelBooking


def about(request):
    r = Restaurant.objects.all()
    args = {
        "about_page": "active",
        "rest" : r,
    }
    return render(request, 'main/about.html', args)


def home(request):
    args = {
        'restaurants': restaurants,
        "home_page": "active",
    }
    return render(request, 'main/home.html', args)


def restaurants(request):
    if request.user.is_authenticated:
        if request.user.usertype.who == 'P':
            restaurants = Restaurant.objects.all()
        else:
            restaurants = Restaurant.objects.filter(user=request.user)
    else:
        restaurants = Restaurant.objects.filter(ratings__isnull=False).order_by('-ratings__average')



    args = {
        'restaurants': restaurants,
        "restaurants_page": "active",
    }
    return render(request, 'main/restaurants.html', args)


def singup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        who_form = CustomUserForm(request.POST)
        if form.is_valid() and who_form.is_valid():
            userr = form.save()
            userr.usertype.who = who_form.cleaned_data.get('who')
            userr.usertype.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
        who_form = CustomUserForm()
    return render(request, 'registration/registration.html', {'form': form, 'who': who_form})


@is_person
@login_required
def tables(request):
    table = Table.objects.all()
    try:
        this_table = table.get(booked_by=request.user)
        form = CancelBooking(request.POST or None, instance=this_table)
        a = table.get(booked_by=request.user)
        b = a.restaurant

        if form.is_valid():
            user = form.save(commit=False)
            tbl = this_table
            tbl.booked = False
            tbl.booked_by = None
            tbl.save()
            user.save()
            return redirect('tables')
        else:
            form = CancelBooking()

    except ObjectDoesNotExist:
        messages.error(request, "You Don't have any table")
        return render(request, 'main/tables.html')

    print(a.name)
    args = {
        'form': form,
        'person_tables': a,
        'restaurant': b,
        "tables_page": "active",
    }
    return render(request, 'main/tables.html', args)


def _handler404(request, exception, template_name="errors/index.html"):
    response = render_to_response("errors/index.html")
    response.status_code = 404
    return response

@login_required
def profile(request, pk, slug):
    if pk and slug:
        user = User.objects.get(pk=pk, username=slug)
    else:
        user = request.user
    return render(request, 'main/profile.html', {'profile': user, "profile_page": "active"})


@login_required
def user_edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = UserModelUpdateForm(request.POST, request.FILES, instance=request.user.people)
        if u_form.is_valid() or p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('home')
    else:
        p_form = UserModelUpdateForm(instance=request.user.people)
        u_form = UserUpdateForm(instance=request.user)
    return render(request, 'main/edit_profile.html', {'u_form': u_form, 'p_form': p_form})


class RestaurantUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Restaurant
    fields = ('name', 'restaurant_image', 'description')

    def form_invalid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        restaurant = self.get_object()
        if self.request.user != restaurant.user:
            return False
        else:
            return True


class RestaurantSearchView(ListView):
    template_name = 'main/search_view.html'
    paginate_by = 20
    count = 0

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['count'] = self.count or 0
        context['query'] = self.request.GET.get('q')
        return context

    def get_queryset(self):
        request = self.request
        query = request.GET.get('q', None)

        if query is not None:
           return Restaurant.objects.search(query=query)
        return Restaurant.objects.none()


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_change.html', {
        'form': form
    })
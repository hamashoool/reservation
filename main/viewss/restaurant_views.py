from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView

from main.decorators import is_restaurant
from main.forms import TablesForm, RestaurantForm
from main.models import Restaurant, Table


def restaurant_detail(request, pk, slug):
    try:
        restaurant = Restaurant.objects.get(slug=slug, pk=pk)
    except ObjectDoesNotExist:
        raise Http404
    print(restaurant.user.username)
    args = {
        'restaurant': restaurant,
    }
    return render(request, 'main/restaurant_detail.html', args)


@login_required
@is_restaurant
def create_tables(request):
    restaurant = Restaurant.objects.get(user=request.user)
    if request.method == 'POST':
        form = TablesForm(request.POST or None)
        if form.is_valid():
            user = form.save(commit=False)
            user.restaurant = restaurant
            user.name = form.cleaned_data.get('name')
            user.time = form.cleaned_data.get('time')
            user.save()
            messages.success(request, "Table has been created.")
            return redirect('create_tables')
    else:
        form = TablesForm()
    args = {
        'table': restaurant,
        'form': form,
        'create_table_page': "active"
    }
    return render(request, 'main/tt.html', args)


class TableUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Table
    fields = ('name', 'time',)

    def get_success_url(self):
        restaurant = Restaurant.objects.get(user=self.request.user)
        return reverse_lazy('restaurant_detail', kwargs={'pk': restaurant.id, 'slug': restaurant.slug})

    def form_invalid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        table = self.get_object()
        if self.request.user != table.restaurant.user:
            return False
        else:
            return True


class TableDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Table

    def get_success_url(self):
        restaurant = Restaurant.objects.get(user=self.request.user)
        return reverse_lazy('restaurant_detail', kwargs={'pk': restaurant.id, 'slug': restaurant.slug})

    def test_func(self):
        table = self.get_object()
        if self.request.user != table.restaurant.user:
            return False
        else:
            return True


@login_required
@is_restaurant
def create_restaurant(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.user = request.user
            user.save()
            return redirect('/')
    else:
        form = RestaurantForm()
    args = {
        'form': form,
        'create_restaurant_page': "active",
    }
    return render(request, 'main/create_restaurant.html', args)

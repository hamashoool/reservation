from django.urls import path, include

from .views import tables, singup, home, profile, user_edit_profile, RestaurantUpdateView, RestaurantSearchView, about, change_password, restaurants
from main.viewss.people_views import booking
from main.viewss.restaurant_views import restaurant_detail, create_tables, create_restaurant, TableUpdateView, TableDeleteView

urlpatterns = [
    path('', home, name='home'),
    path('restaurants', restaurants, name='restaurant_s'),
    path('about_us/', about, name='about'),
    path('booking/<int:pk>/<str:slug>/', booking, name='booking'),
    path('profile/<int:pk>/<str:slug>', profile, name='profile'),
    path('profile/update/', user_edit_profile, name='update_profile'),
    path('profile/update/password/', change_password, name='change_password'),
    path('register/', singup, name='register'),
    path('restaurant/update/<int:pk>/<str:slug>/', RestaurantUpdateView.as_view(), name='update_restaurant'),
    path('restaurant/create/', create_restaurant, name='create_restaurant'),
    path('restaurant/<int:pk>/<str:slug>/', restaurant_detail, name='restaurant_detail'),
    path('search/', RestaurantSearchView.as_view(), name='search'),
    path('tables/', tables, name='tables'),
    path('tables/<int:pk>/update/', TableUpdateView.as_view(), name='update_tables'),
    path('tables/<int:pk>/delete/', TableDeleteView.as_view(), name='delete_table'),
    path('tables/create/', create_tables, name='create_tables'),
]

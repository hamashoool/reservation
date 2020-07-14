from django.contrib import admin

from main.models import Restaurant, Table, People, UserType, Time

admin.site.register(Restaurant)
admin.site.register(Table)
admin.site.register(People)
admin.site.register(UserType)
admin.site.register(Time)

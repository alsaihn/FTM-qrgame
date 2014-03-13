from django.contrib import admin
from game.models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'image', 'last_checkin')

class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'pirate_total', 'ninja_total', 'in_play')

admin.site.register(User, UserAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Images)



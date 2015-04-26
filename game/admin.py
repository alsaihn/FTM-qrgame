from django.contrib import admin
from game.models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'image', 'last_checkin')

class PanelAdmin(admin.ModelAdmin):
    list_display = ('panel_name', 'start_time', 'end_time', 'in_play')

admin.site.register(User, UserAdmin)
admin.site.register(Panel, PanelAdmin)
admin.site.register(Images)
admin.site.register(Group)
admin.site.register(QrCode)



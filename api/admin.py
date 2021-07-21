from django.contrib import admin

from api.models import Tasks, Links, User

admin.site.register(User)
admin.site.register(Tasks)
admin.site.register(Links)

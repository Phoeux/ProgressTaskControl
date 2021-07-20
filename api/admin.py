from django.contrib import admin

from api.models import Tasks
from api.schema import User

admin.site.register(User)
admin.site.register(Tasks)

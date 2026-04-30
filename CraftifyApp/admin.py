from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Login)
admin.site.register(Artist)
admin.site.register(Products)
admin.site.register(Cart)
admin.site.register(Feedback)
admin.site.register(Chat)


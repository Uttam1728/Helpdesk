from django.contrib import admin

from common.models import Message, Category

# Register your models here.
admin.site.register(Message)
admin.site.register(Category)
from django.contrib import admin
from django.contrib.auth.models import User

from user_accounts.models import Account

# Register your models here.

admin.site.register(Account)
admin.site.register(User)
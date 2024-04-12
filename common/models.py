from django.db import models

from user_accounts.models import Account


# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    answer = models.TextField(blank=True, null=True)
    contact_person = models.ForeignKey(Account, on_delete=models.CASCADE,
                      limit_choices_to={'role': 'staff'},
                      related_name='categories',
                      blank=True, null=True)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='subcategories', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category_name

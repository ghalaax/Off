from django.contrib import admin
from .models import OffAccount, OffTransaction

# Register your models here.
admin.site.register(OffAccount)
admin.site.register(OffTransaction)

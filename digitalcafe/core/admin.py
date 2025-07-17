from django.contrib import admin
from .models import Product
from .models import CartItem
from .models import Transaction, LineItem

admin.site.register(CartItem)
# Register your models here.

admin.site.register(Product)
admin.site.register(Transaction)
admin.site.register(LineItem)

# Register your models here.

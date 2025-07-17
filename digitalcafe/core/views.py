from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages  # ✅ Needed for flash messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from .models import CartItem
from django.contrib.auth import logout
import datetime as dt
from .models import Transaction, LineItem


def login_view(request):
    if request.method == 'GET':
        template = loader.get_template("core/login_view.html")
        return HttpResponse(template.render({}, request))

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is None:
            messages.add_message(request, messages.INFO, 'Invalid login.')
            return redirect(request.path_info)

        login(request, user)

        # Check if user was trying to access a specific page
        next_url = request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        
        # If not, redirect to home
        return redirect('index')

@login_required
def logout_view(request):
    logout(request)
    return redirect("login_view")

@login_required
def index(request):
    products = Product.objects.all()
    return render(request, "core/index.html", {
        "product_data": products,
        "user": request.user,  # 👈 Optional: for greeting the user later
    })

@login_required
def product_detail(request, product_id):
    if request.method == 'GET':
        template = loader.get_template("core/product_detail.html")
        p = Product.objects.get(id=product_id)
        context = {
            "product": p
        }
        return HttpResponse(template.render(context, request))
    
    elif request.method == 'POST':
        submitted_quantity = request.POST['quantity']
        submitted_product_id = request.POST['product_id']
        product = Product.objects.get(id=submitted_product_id)
        user = request.user

        # ✅ Create and save CartItem
        cart_item = CartItem(user=user, product=product, quantity=submitted_quantity)
        cart_item.save()

        # ✅ Add a success message
        messages.add_message(
            request,
            messages.INFO,
            f'Added {submitted_quantity} of {product.name} to your cart'
        )

        # ✅ Redirect to the product list
        return redirect('index')

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, "core/cart.html", {"cart_items": cart_items, "total": total})

@login_required
def checkout(request):
    if request.method == 'GET':
        template = loader.get_template("core/checkout.html")
        cart_items = CartItem.objects.filter(user=request.user)
        context = {
            'cart_items': list(cart_items),
        }
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        cart_items = CartItem.objects.filter(user=request.user)
        created_at = dt.datetime.now(tz=dt.timezone.utc)
        transaction = Transaction(user=request.user, created_at=created_at)
        transaction.save()
        for cart_item in cart_items:
            line_item = LineItem(
                transaction=transaction,
                product=cart_item.product,
                quantity=cart_item.quantity,
            )
            line_item.save()
            cart_item.delete()
        messages.add_message(request, messages.INFO, 'Thank you for your purchase!')
        return redirect('index')

@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'transactions': transactions,
    }
    template = loader.get_template('core/transaction_history.html')
    return HttpResponse(template.render(context, request))
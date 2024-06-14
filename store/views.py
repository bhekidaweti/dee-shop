from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import *
from . utils import cookieCart, cartData, guestOrder
from .forms import RegistrationForm


# Create your views here.
def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("store"))
        else:
            #Keep rendering the login page if the username  and/or password is invalid
            messages.error(request, 'Invalid username and/or passowrd')
            return render(request, "store/login.html")
    else:
        return render(request, "store/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("store"))


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(
                user = user,
                name = user.username,
                email = user.email
            )
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')  
            #messages.success(request, 'Your account has been succesfully registed for' + username )
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return HttpResponseRedirect(reverse("store"))
    else:
        form = RegistrationForm()
    return render(request, "store/register.html", {'form': form})
   
def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']           

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']


    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)

@csrf_exempt
def payment_notify(request):
    # Handle PayFast IPN (Instant Payment Notification)
    # Verify and update order status here
    return render(request, 'payment_notify.html')

def payment_success(request):
    # Handle successful payment
    return render(request, 'payment_success.html')

def payment_cancelled(request):
    # Handle cancelled payment
    return render(request, 'payment_cancelled.html')

@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                zipcode=data['shipping']['zipcode'],
            )  

    return JsonResponse('Payment complete..!', safe=False) 
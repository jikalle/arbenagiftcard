from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import datetime

from .models import Customer, Product, Order, OrderItem, ShippingAddress
from .utils import cartData, guestOrder

@login_required
def main(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()
        
    context = {
        'products':products, 'cartItems': cartItems, 
    }
    return render(request, 'core/index.html', context)

def cart(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
        
    context = {
        'items':items, 'order':order, 'cartItems':cartItems
    }
    return render(request, 'core/cart.html', context)

def checkout(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
        
    context = {
        'items': items, 'order': order, 'cartItems': cartItems
    }
    return render(request, 'core/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    
    print('Action:', action)
    print('productId:', productId)
    
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.qty = (orderItem.qty + 1)
        # if orderItem not in order.orderItem:
        #     orderItem.qty = (orderItem.qty + 1)
        #     messages.info(request, 'item added successfulyy')
        # else:
        #     messages.info(request, 'You added this item already')
    elif action == 'remove':
        orderItem.qty = (orderItem.qty - 1)
        
    orderItem.save()
    if orderItem.qty <= 0:
            orderItem.delete()
        
    return JsonResponse('Item was added', safe=False)

from django.views.decorators.csrf import csrf_exempt

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
        
    if total == order.get_cart_total:
        order.complete = True
    order.save()
    
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )
        
    return JsonResponse('Payment completed...', safe=False)




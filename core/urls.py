from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.main, name='home'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.updateItem, name='update-item'),
    path('process_order/', views.processOrder, name='process-order'),
]
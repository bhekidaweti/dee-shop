from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name = "store"),
    path('cart/', views.cart, name = "cart"),
    path('checkout/', views.checkout, name = "checkout"),
    
    path('update_item/', views.updateItem, name = "update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('register/', views.register, name="register"),
    path('payment_notify/', views.payment_notify, name='payment_notify'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_cancelled/', views.payment_cancelled, name='payment_cancelled'),

    ]
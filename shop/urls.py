from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('register/admin/', views.register_admin, name='register_admin'),
    path('register/vendor/', views.register_vendor, name='register_vendor'),
    path('register/customer/', views.register_customer, name='register_customer'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('custom_admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('vendor/products/', views.vendor_products, name='vendor_products'),
    path('vendor/add_product/', views.add_product, name='add_product'),
    path('vendor/edit_product/<int:pk>/', views.edit_product, name='edit_product'),
    path('vendor/delete_product/<int:pk>/', views.delete_product, name='delete_product'),
    path('product/<int:product_id>/', views.view_product, name='view_product'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('purchase/<int:product_id>/', views.purchase_product, name='purchase_product'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
]

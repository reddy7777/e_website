from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Product, Profile, Cart, CartItem
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse

# Utility functions to check user roles
def is_admin(user):
    # return hasattr(user, 'profile') and user.profile.user_type == 'admin'
    return user.is_authenticated  and user.is_superuser

def is_vendor(user):
    return hasattr(user, 'profile') and user.profile.user_type == 'vendor'

def is_customer(user):
    return hasattr(user, 'profile') and user.profile.user_type == 'customer'

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

def vendor_dashboard(request):
    return render(request, 'vendor_dashboard.html')

def customer_dashboard(request):
    return render(request, 'customer_dashboard.html')


# Homepage
def homepage(request):
    return render(request, 'home.html')


# def user_login(request):
#     if request.method == 'POST':
#         print("requested method is post")
#         form = AuthenticationForm(request, data=request.POST)
#         # print(f"form: {form}")
#         print(f"username: {form.cleaned_data.get('username')}")
#         if form.is_valid():
#             print(f"form: {form}")
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, username=username, password=password)
#             print(f"user:{user}")
#             if user is not None:
#                 login(request, user)
#                 # Redirect based on user profile type
#                 print(user.profile.is_customer, user.profile.is_vendor, user.profile.is_admin)
#                 if hasattr(user, 'profile'):
#                     if user.profile.is_admin:
#                         return redirect('admin_dashboard')
#                     elif user.profile.is_vendor:
#                         return redirect('vendor_dashboard')
#                     elif user.profile.is_customer:
#                         return redirect('customer_dashboard')
#                 return redirect('homepage')  # In case user has no profile or invalid type
#             else:
#                 print(f"user is not registered")
#                 return redirect('login')  # Or display a login error message
#         else:
#             print("Form is invalid")
#             print(form.errors)  # Log form errors for debugging
#     else:
#         print("Requested method is GET")
#         form = AuthenticationForm()
#     return render(request, 'registration/login.html', {'form': form})

# def user_login(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 print(f"user:{user.user_type}")
#                 login(request, user)
#                 # Redirect based on user_type
#                 if user.user_type == 'admin':
#                     return redirect('admin_dashboard')
#                 elif user.user_type == 'vendor':
#                     print(f"redirecting to vendor dashboard")
#                     return redirect('vendor_dashboard')
#                 elif user.user_type == 'customer':
#                     print(f"redirecting to customer dashboard")
#                     return redirect('customer_dashboard')
#                 else:
#                     return redirect('homepage')  # Fallback for unknown user_type
#             else:
#                 return render(request, 'registration/login.html', {'form': form, 'error': 'Invalid credentials'})
#         else:
#             return render(request, 'registration/login.html', {'form': form, 'error': 'Form is invalid'})
#     else:
#         form = AuthenticationForm()
#     return render(request, 'registration/login.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                print(f"user:{user.user_type}")
                login(request, user)
                if hasattr(user, 'profile'):
                    print(f"user_type: {user.profile.user_type}")  # Debugging
                    if user.profile.user_type == 'admin':
                        print("redirecting to admin dashboard")
                        return redirect('admin_dashboard')
                    elif user.profile.user_type == 'vendor':
                        return redirect('vendor_dashboard')
                    elif user.profile.user_type == 'customer':
                        return redirect('customer_dashboard')
                else:
                    print("User profile not found.")  # Debugging
                return redirect('homepage')
            else:
                return render(request, 'registration/login.html', {'form': form, 'error': 'Invalid credentials'})
        else:
            print(f"Form errors: {form.errors}")  # Debugging
            return render(request, 'registration/login.html', {'form': form, 'error': 'Form is invalid'})
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


## logout
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')



# Admin dashboard (accessible only by admin users)
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    print("directing to admin dashboard page.")
    if not request.user.is_superuser:
        print(f"Access denied for user: {request.user.username}")
        return HttpResponse("Unauthorized", status=403)
    
    products = Product.objects.all()  # Admin can view all products
    users = Profile.objects.all()    # Admin can view all user profiles
    return render(request, 'admin_dashboard.html', {
        'products': products,
        'users': users
    })

# Vendor dashboard (accessible only by vendor users)
@login_required
@user_passes_test(is_vendor)
def vendor_dashboard(request):
    print("directing to vendor dashboard page.")
    products = Product.objects.filter(vendor=request.user)  
    return render(request, 'vendor_dashboard.html', {'products': products})
    # return render(request, 'vendor_dashboard.html')

## customer dashboard
@login_required
@user_passes_test(is_customer)
def customer_dashboard(request):
    # Add relevant logic for the customer dashboard
    print("directing to customer dashboard page.")
    products = Product.objects.all()

    orders=[]
    return render(request, 'customer_dashboard.html',{'products':products,'orders':orders,})

# Register views
def register_admin(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.profile.is_admin = True
            user.save()
            # return redirect('login')

            profile = Profile.objects.create(user=user, user_type = 'admin')
            profile.save()
            login(request, user)
            return redirect('admin_dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register_admin.html', {'form': form})

def register_vendor(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.profile.is_vendor = True
            user.save()

            profile = Profile.objects.create(user=user, user_type = 'vendor')
            profile.save()
            login(request, user)
            return redirect('vendor_dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register_vendor.html', {'form': form})

def register_customer(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.profile.is_customer = True
            user.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register_customer.html', {'form': form})

# Product views (for vendors)
@login_required
@user_passes_test(is_vendor)
def vendor_products(request):
    products = Product.objects.filter(vendor=request.user)  # Vendor can manage their own products
    return render(request, 'vendor/vendor_products.html', {'products': products})





@login_required
@user_passes_test(is_vendor)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user
            product.save()
            return redirect('vendor_products')
    else:
        form = ProductForm()
    return render(request, 'vendor/add_product.html', {'form': form})

@login_required
@user_passes_test(is_vendor)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('vendor_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'vendor/edit_product.html', {'form': form})

@login_required
@user_passes_test(is_vendor)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor=request.user)
    # product.delete()
    # return redirect('vendor_products')
    if request.method == 'POST':
        product.delete()

        return redirect('vendor_products')
    return render(request, 'vendor/delete_product.html', {'product': product})

# # Product list for customers
# @login_required
# @user_passes_test(is_customer)
# def product_list(request):
#     products = Product.objects.filter(stock__gt=0)  # Customers see only available products
#     return render(request, 'shop/product_list.html', {'products': products})

# Product details for customers
@login_required
@user_passes_test(is_customer)
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})


def view_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'view_product.html', {'product': product})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Assuming there's a Cart model with a method `add_product`
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.add_product(product)
    return redirect('view_cart')

def view_cart(request):
    cart = Cart.objects.get(user=request.user)
    return render(request, 'view_cart.html', {'cart': cart})

def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, user=request.user)
    cart.remove_product(product)
    return redirect('view_cart')  # Redirect to the cart view after removing the product

def purchase_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Logic for purchasing the product
    return render(request, 'purchase_confirmation.html', {'product': product})
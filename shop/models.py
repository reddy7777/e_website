from django.db import models
from django.contrib.auth.models import User, AbstractUser

from django.db.models.signals import post_save
from django.dispatch import receiver
# from .models import Profile


class User(AbstractUser):
    # Custom fields, for example
    user_type = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('vendor', 'Vendor'), ('customer', 'Customer')], default='customer')

    # Add related_name to groups and user_permissions to avoid reverse accessor clash
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='shop_users',  # Custom reverse name for groups relationship
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='shop_user'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='shop_users',  # Custom reverse name for user_permissions relationship
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='shop_user'
    )




class Profile(models.Model):
    """
    Extends the User model to differentiate between Admin, Vendor, and Customer roles.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)  # Determines if the user is an admin
    is_customer = models.BooleanField(default=False)  # Default role is customer
    is_vendor = models.BooleanField(default=False)  # Vendor-specific role
    # first_login = models.BooleanField(default=True)  # Flag to track first login
    user_type = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('customer', 'Customer'), ('vendor', 'Vendor')])

    def __str__(self):
        return self.user.username


class Product(models.Model):
    """
    Represents a product managed by a Vendor.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products',
        limit_choices_to={'profile__is_vendor': True},  # Ensures only vendors can own products
        default=1
    )

    def __str__(self):
        return self.name

    def is_in_stock(self):
        """
        Returns True if the product is in stock.
        """
        return self.stock > 0


class Cart(models.Model):
    """
    Represents a shopping cart for a customer.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'profile__is_customer': True},  # Ensures only customers can own carts
    )
    products = models.ManyToManyField(Product, through='CartItem')

    def __str__(self):
        return f"Cart for {self.user.username}"

    def total_price(self):
        """
        Calculates the total price of items in the cart.
        """
        return sum(item.product.price * item.quantity for item in self.cartitem_set.all())
    
    def add_product(self, product, quantity=1):
        """
        Adds a product to the cart or updates its quantity if it already exists.
        """
        cart_item, created = CartItem.objects.get_or_create(cart=self, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

    def remove_product(self, product):
        """
        Removes the product from the cart. Deletes the CartItem.
        """
        try:
            cart_item = self.cartitem_set.get(product=product)
            cart_item.delete()
        except CartItem.DoesNotExist:
            pass



class CartItem(models.Model):
    """
    Represents an item in a customer's cart.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in {self.cart.user.username}'s cart"

    def total_item_price(self):
        """
        Calculates the total price for this cart item.
        """
        return self.product.price * self.quantity

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

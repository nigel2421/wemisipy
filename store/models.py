
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True) # This makes the URL look nice (e.g., /granite/)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Hardware specific fields
    dimensions = models.CharField(max_length=100, blank=True, help_text="e.g. 10x10ft")
    image = models.ImageField(upload_to='products/')
    is_featured = models.BooleanField(default=False) # If true, shows on Homepage
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f'{self.product.name} Image'

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart with session ID {self.session_id}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    products = models.ManyToManyField(Product)

    def __str__(self):
        return f"Wishlist for {self.user.username}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    order_id = models.CharField(max_length=20, unique=True, editable=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Billing info (optional, just in case they want it on the receipt)
    full_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate a simple order ID like WMI-20240322-XXXX
            import random
            import string
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%H%M')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            self.order_id = f"WMI-{date_str}-{random_str}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price at the time of purchase

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_id}"

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=255, help_text="Auto-generated from title. Used for the URL.")
    content = CKEditor5Field('Content', config_name='extends', help_text="The main content of the blog post.")
    image = models.ImageField(upload_to='blog_images/', help_text="A feature image for the blog post.")
    published_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-published_date'] # This will show the newest posts first

    def __str__(self):
        return self.title

class JobOpening(models.Model):
    JOB_TYPES = (
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=255)
    location = models.CharField(max_length=100, default='Nairobi')
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='Full-time')
    description = CKEditor5Field('Description', config_name='extends')
    requirements = CKEditor5Field('Requirements', config_name='extends')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class JobApplication(models.Model):
    job = models.ForeignKey(JobOpening, related_name='applications', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    cv = models.FileField(upload_to='cvs/')
    cover_letter = models.TextField()
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application from {self.full_name} for {self.job.title}"

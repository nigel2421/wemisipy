from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=255, help_text="Auto-generated from title. Used for the URL.")
    content = models.TextField(help_text="The main content of the blog post.")
    image = models.ImageField(upload_to='blog_images/', help_text="A feature image for the blog post.")
    published_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-published_date'] # This will show the newest posts first

    def __str__(self):
        return self.title
from django.contrib import sitemaps
from django.urls import reverse
from .models import Product

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'store', 'cart_detail', 'wishlist_detail', 'careers', 'blog']

    def location(self, item):
        return reverse(item)

class ProductSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

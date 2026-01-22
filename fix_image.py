
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')
django.setup()

from store.models import Product

# The path of the broken image
broken_image_path = 'products/photo_2025-11-26_10-09-15.jpg'

# Find all products that reference this broken image
products_to_fix = Product.objects.filter(image=broken_image_path)

if products_to_fix.exists():
    print(f"Found {products_to_fix.count()} product(s) with broken image reference.")
    for product in products_to_fix:
        print(f"  - Clearing image for product: '{product.name}' (ID: {product.id})")
        # Set the image field to None to remove the reference
        product.image = None
        product.save()
    print("Successfully fixed broken image references.")
else:
    print("No products found with the specified broken image reference.")

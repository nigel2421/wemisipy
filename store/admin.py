from django.contrib import admin
from .models import Category, Product, ProductImage, BlogPost

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'available']
    list_editable = ['price', 'available']
    inlines = [ProductImageInline]

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)} # Automatically creates the URL slug from the title
from django.contrib import admin
from django import forms
from .models import Category, Product, ProductImage, BlogPost

# Custom form for BlogPost to include a class for the content textarea
class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = '__all__'
        widgets = {
            'content': forms.Textarea(attrs={'class': 'richtext-editor'}),
        }

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
    form = BlogPostForm
    list_display = ('title', 'author', 'published_date')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)} # Automatically creates the URL slug from the title

    # Add the necessary JavaScript for CKEditor
    class Media:
        js = (
            'https://cdn.ckeditor.com/ckeditor5/41.1.0/classic/ckeditor.js',
            'store/js/blog_editor.js',
        )

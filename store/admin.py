from django.contrib import admin, messages
from django import forms
from django.urls import path, reverse
from django.shortcuts import render, redirect
from .models import Category, Product, ProductImage, BlogPost, Order, OrderItem, JobOpening, JobApplication
from django.utils.html import format_html

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
    list_display = ('name', 'price', 'category', 'available', 'is_featured', 'bulk_upload_link')
    list_editable = ['price', 'available']
    list_filter = ('category', 'available', 'is_featured')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/bulk-upload/', self.admin_site.admin_view(self.bulk_upload), name='store_product_bulk_upload'),
        ]
        return custom_urls + urls

    def bulk_upload(self, request, object_id):
        product = self.get_object(request, object_id)
        if request.method == 'POST':
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            messages.success(request, f'Successfully uploaded {len(images)} images.')
            return redirect('admin:store_product_change', object_id)
        
        context = dict(
           self.admin_site.each_context(request),
           product=product,
           opts=self.model._meta,
           has_permission=self.has_change_permission(request, product),
        )
        return render(request, 'admin/store/product/bulk_upload.html', context)

    def bulk_upload_link(self, obj):
        url = reverse('admin:store_product_bulk_upload', args=[obj.pk])
        return format_html('<a class="button" href="{}">Bulk Upload Images</a>', url)
    bulk_upload_link.short_description = 'Images'

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
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'total_price', 'status', 'created_at', 'invoice_link']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'full_name', 'phone_number']
    inlines = [OrderItemInline]
    readonly_fields = ['order_id', 'total_price', 'created_at', 'updated_at']

    def invoice_link(self, obj):
        url = reverse('admin_order_invoice', args=[obj.id])
        return format_html('<a class="button" href="{}">Generate PDF</a>', url)
    invoice_link.short_description = 'Invoice'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']

@admin.register(JobOpening)
class JobOpeningAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'job_type', 'is_active', 'created_at']
    list_filter = ['is_active', 'job_type', 'location']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'job', 'email', 'phone', 'applied_at']
    list_filter = ['job', 'applied_at']
    search_fields = ['full_name', 'email', 'phone', 'cover_letter']
    readonly_fields = ['job', 'full_name', 'email', 'phone', 'cv', 'cover_letter', 'applied_at']

    def has_add_permission(self, request):
        return False

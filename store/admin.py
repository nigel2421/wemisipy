from django.contrib import admin, messages
from django import forms
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Category, Product, ProductImage, BlogPost, Order, OrderItem, JobOpening, JobApplication
from django.utils.html import format_html
import json

# ── Custom form for BlogPost ────────────────────────────────────────────────
class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = '__all__'
        widgets = {
            'content': forms.Textarea(attrs={'class': 'richtext-editor'}),
        }

# ── Category Admin ──────────────────────────────────────────────────────────
class SubcategoryInline(admin.TabularInline):
    model = Category
    fk_name = 'parent'
    extra = 1
    fields = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    verbose_name = "Subcategory"
    verbose_name_plural = "Subcategories"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'parent', 'order', 'subcategory_count')
    list_filter = ('parent',)
    list_editable = ('order',)
    inlines = [SubcategoryInline]
    search_fields = ('name',)

    def subcategory_count(self, obj):
        return obj.subcategories.count()
    subcategory_count.short_description = 'Subcategories'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('subcategories')

# ── Product Admin ───────────────────────────────────────────────────────────
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'category' in self.fields:
            categories = list(Category.objects.select_related('parent').all())
            top_levels = [c for c in categories if not c.parent]
            
            flat_choices = [('', '---------')]
            for top in top_levels:
                flat_choices.append((top.id, str(top.name).upper()))
                subs = [c for c in categories if c.parent_id == top.id]
                for sub in subs:
                    flat_choices.append((sub.id, f"   — {sub.name}"))
            
            self.fields['category'].choices = flat_choices

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'price', 'category', 'available', 'is_featured', 'bulk_upload_link')
    list_editable = ['price', 'available']
    list_filter = ('category', 'available', 'is_featured')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/bulk-upload/',
                 self.admin_site.admin_view(self.bulk_upload),
                 name='store_product_bulk_upload'),
            path('<path:object_id>/reorder-images/',
                 self.admin_site.admin_view(self.reorder_images),
                 name='store_product_reorder_images'),
        ]
        return custom_urls + urls

    def bulk_upload(self, request, object_id):
        product = self.get_object(request, object_id)
        if request.method == 'POST':
            images = request.FILES.getlist('images')
            # Find the current max order so new images append at the end
            existing_max = product.images.order_by('-order').values_list('order', flat=True).first() or 0
            for idx, image in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    order=existing_max + idx + 1
                )
            messages.success(request, f'Successfully uploaded {len(images)} image(s).')
            return redirect('admin:store_product_change', object_id)

        existing_images = product.images.order_by('order')
        context = dict(
            self.admin_site.each_context(request),
            product=product,
            existing_images=existing_images,
            opts=self.model._meta,
            has_permission=self.has_change_permission(request, product),
        )
        return render(request, 'admin/store/product/bulk_upload.html', context)

    def reorder_images(self, request, object_id):
        """AJAX endpoint: accepts JSON list of image IDs and updates their order."""
        if request.method != 'POST':
            return JsonResponse({'error': 'POST required'}, status=405)
        try:
            data = json.loads(request.body)
            image_ids = data.get('image_ids', [])
            for idx, img_id in enumerate(image_ids):
                ProductImage.objects.filter(id=img_id, product_id=object_id).update(order=idx)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def bulk_upload_link(self, obj):
        url = reverse('admin:store_product_bulk_upload', args=[obj.pk])
        return format_html('<a class="button" href="{}">📷 Upload Images</a>', url)
    bulk_upload_link.short_description = 'Images'

# ── Blog Post Admin ─────────────────────────────────────────────────────────
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    form = BlogPostForm
    list_display = ('title', 'author', 'published_date')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

    class Media:
        js = (
            'https://cdn.ckeditor.com/ckeditor5/41.1.0/classic/ckeditor.js',
            'store/js/blog_editor.js',
        )

# ── Order Admin ─────────────────────────────────────────────────────────────
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

# ── Job Openings Admin ──────────────────────────────────────────────────────
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

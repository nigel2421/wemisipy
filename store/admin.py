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
    verbose_name_plural = "Subcategories (shown in nav dropdown)"
    show_change_link = True

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('order', 'name')


class TopLevelFilter(admin.SimpleListFilter):
    """Filter: show only top-level parents or only subcategories."""
    title = 'Level'
    parameter_name = 'level'

    def lookups(self, request, model_admin):
        return [
            ('top', 'Top-level (Parent Categories)'),
            ('sub', 'Subcategories'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'top':
            return queryset.filter(parent__isnull=True)
        if self.value() == 'sub':
            return queryset.filter(parent__isnull=False)
        return queryset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('display_name', 'level_badge', 'parent', 'order', 'subcategory_count', 'product_count_display')
    list_display_links = ('display_name',)
    list_filter = (TopLevelFilter, 'parent')
    list_editable = ('order',)
    inlines = [SubcategoryInline]
    search_fields = ('name',)
    fieldsets = (
        ('Category Details', {
            'fields': ('name', 'slug', 'order'),
            'description': (
                '<strong>Name</strong>: The display label for this category.<br>'
                '<strong>Slug</strong>: Auto-filled URL-safe version of the name.<br>'
                '<strong>Order</strong>: Controls position in the nav (lower = first).'
            ),
        }),
        ('Parent / Hierarchy', {
            'fields': ('parent',),
            'description': (
                'Leave <em>Parent</em> blank to make this a <strong>top-level nav item</strong>. '
                'Select a parent to nest this as a <strong>subcategory dropdown item</strong>.'
            ),
        }),
    )

    # ── Custom display columns ─────────────────────────────────────────────

    def display_name(self, obj):
        if obj.parent:
            return format_html(
                '<span style="margin-left:20px; color:#555;">↳ {}</span>', obj.name
            )
        return format_html('<strong>{}</strong>', obj.name)
    display_name.short_description = 'Category Name'
    display_name.admin_order_field = 'name'

    def level_badge(self, obj):
        if obj.parent is None:
            return format_html(
                '<span style="background:#1a1c1e;color:#fff;padding:2px 8px;'
                'border-radius:3px;font-size:0.75rem;font-weight:600;">PARENT</span>'
            )
        return format_html(
            '<span style="background:#f15a24;color:#fff;padding:2px 8px;'
            'border-radius:3px;font-size:0.75rem;">sub</span>'
        )
    level_badge.short_description = 'Level'

    def subcategory_count(self, obj):
        count = obj.subcategories.count()
        if count:
            return format_html('<strong style="color:#1a1c1e;">{}</strong>', count)
        return '—'
    subcategory_count.short_description = 'Subcategories'

    def product_count_display(self, obj):
        count = obj.products.count()
        if count:
            return format_html('<span style="color:#16a34a;">{} products</span>', count)
        return format_html('<span style="color:#94a3b8;">0</span>')
    product_count_display.short_description = 'Products'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent').prefetch_related('subcategories', 'products')



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

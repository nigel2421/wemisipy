
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views, ai_views
from .sitemaps import StaticViewSitemap, ProductSitemap
from django.contrib.sitemaps.views import sitemap
from django.http import FileResponse
import os

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), 
    path('', views.home, name='home'),
    path('store/', views.store, name='store'),
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'),
    path('category/<slug:category_slug>/<slug:sub_slug>/', views.subcategory_detail, name='subcategory_detail'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    
    # New Cart URLs
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/update/<int:product_id>/', views.update_cart_item, name='update_cart_item'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/<str:order_id>/', views.checkout_success, name='checkout_success'),
    path('admin/order/<int:order_id>/invoice/', views.download_invoice, name='admin_order_invoice'),

    # Wishlist URLs
    path('wishlist/', views.wishlist_detail, name='wishlist_detail'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
     path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('careers/', views.careers, name='careers'), 
    path('careers/<slug:slug>/', views.job_detail, name='job_detail'),
    path('careers/<slug:slug>/apply/', views.apply_for_job, name='apply_for_job'),
    path('blog/', views.blog, name='blog'), # The main blog page
    path('blog/<slug:slug>/', views.blog_post_detail, name='blog_post_detail'), # The detail page for a single post
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    # AI Assistant
    path('ai/chat/', ai_views.ai_chat_message, name='ai_chat'),
    path('ai/generate-blog/', ai_views.ai_generate_blog, name='ai_generate_blog'),

    # PWA
    path('manifest.json', lambda r: FileResponse(open(os.path.join(settings.BASE_DIR, 'mbele/templates/manifest.json'), 'rb'), content_type='application/json'), name='manifest_json'),
    path('sw.js', lambda r: FileResponse(open(os.path.join(settings.BASE_DIR, 'mbele/templates/sw.js'), 'rb'), content_type='application/javascript'), name='service_worker'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

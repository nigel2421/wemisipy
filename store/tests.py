import json
import os
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from store.models import Product, Cart, CartItem, Wishlist, Category, BlogPost, JobOpening, JobApplication

class StoreFunctionalityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(name='Test Product', price=100.00, category=self.category)

    def test_add_to_cart(self):
        response = self.client.post(reverse('add_to_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)

    def test_toggle_wishlist(self):
        response = self.client.post(reverse('toggle_wishlist', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['added'])

    def test_checkout_flow(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]))
        response = self.client.post(reverse('checkout'), {
            'full_name': 'Test User',
            'phone_number': '0712345678',
            'address': 'Nairobi',
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('wa.me', response.url)

class AIFunctionalityTests(TestCase):
    @override_settings(GOOGLE_API_KEY='fake_key')
    @patch('google.generativeai.GenerativeModel')
    def test_ai_chat_message(self, mock_model):
        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Hello! I am your assistant."
        mock_chat.send_message.return_value = mock_response
        mock_model.return_value.start_chat.return_value = mock_chat
        mock_model.return_value.generate_content.return_value = mock_response

        response = self.client.post(
            reverse('ai_chat'),
            data=json.dumps({'message': 'Hi', 'history': []}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['response'], "Hello! I am your assistant.")

    @override_settings(GOOGLE_API_KEY='fake_key')
    @patch('google.generativeai.GenerativeModel')
    def test_ai_generate_blog(self, mock_model):
        mock_response = MagicMock()
        mock_response.text = "<h1>Test Blog</h1><p>Content</p>"
        mock_model.return_value.generate_content.return_value = mock_response

        response = self.client.post(
            reverse('ai_generate_blog'),
            data=json.dumps({'topic': 'Test Topic'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('Test Blog', data['content'])

class PWATests(TestCase):
    def test_manifest_json(self):
        response = self.client.get(reverse('manifest_json'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_service_worker(self):
        response = self.client.get(reverse('service_worker'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/javascript')

class CareersTests(TestCase):
    def setUp(self):
        self.job = JobOpening.objects.create(
            title="Stone Mason",
            slug="stone-mason",
            location="Nairobi",
            job_type="Full-time",
            description="<p>Test</p>",
            requirements="<p>Test</p>"
        )

    def test_careers_list(self):
        response = self.client.get(reverse('careers'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stone Mason")

    def test_job_detail(self):
        response = self.client.get(reverse('job_detail', args=[self.job.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stone Mason")

    def test_apply_for_job(self):
        cv_file = SimpleUploadedFile("resume.pdf", b"file_content", content_type="application/pdf")
        response = self.client.post(
            reverse('apply_for_job', args=[self.job.slug]),
            {
                'full_name': 'John Doe',
                'email': 'john@example.com',
                'phone': '0712345678',
                'cv': cv_file,
                'cover_letter': 'Pick me!'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(JobApplication.objects.count(), 1)

class BlogTests(TestCase):
    def test_blog_post_flow(self):
        post = BlogPost.objects.create(
            title="New Design Trends",
            slug="new-design-trends",
            content="<p>Trends</p>"
        )
        response = self.client.get(reverse('blog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New Design Trends")

class AdminCustomizationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='password', email='admin@example.com')
        self.client.login(username='admin', password='password')
        self.parent_cat = Category.objects.create(name='Parent Category', slug='parent-cat')
        self.sub_cat = Category.objects.create(name='Sub Category', slug='sub-cat', parent=self.parent_cat)

    def test_product_admin_form_category_choices(self):
        from store.admin import ProductAdminForm
        form = ProductAdminForm()
        choices = form.fields['category'].choices
        choice_labels = [label for _, label in choices]
        self.assertIn('PARENT CATEGORY', choice_labels)
        self.assertIn('   — Sub Category', choice_labels)

class FrontendTests(TestCase):
    def test_home_partners_section(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        partners = [
            'Crown Paints', 
            'Mombasa Cement', 
            'East African Portland', 
            'Sika East Africa', 
            'National Cement'
        ]
        for partner in partners:
            self.assertContains(response, partner)

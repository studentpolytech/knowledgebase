from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from kb.models import Department, Category, Document
from kb.views import (
    home, select_department, document_list,
    document_detail, add_comment, delete_comment
)
from kb.views_class_based import (
    DocumentCreateView, DocumentUpdateView, DocumentDeleteView
)

User = get_user_model()

class UrlsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_home_url(self):
        url = reverse('home')
        resolved_func = resolve(url).func
        self.assertEqual(resolved_func.__name__, home.__name__)

    def test_document_list_url(self):
        url = reverse('document_list')
        resolved_func = resolve(url).func
        self.assertEqual(resolved_func.__name__, document_list.__name__)

    def test_document_create_url(self):
        url = reverse('document_create')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, DocumentCreateView)

    def test_document_detail_url(self):
        department = Department.objects.create(name='Test Dept')
        category = Category.objects.create(name='Test Cat', department=department)
        document = Document.objects.create(
            title='Test Doc',
            content='Content',
            author=self.user,
            category=category,
            department=department
        )
        url = reverse('document_detail', args=[document.slug])
        resolved_func = resolve(url).func
        self.assertEqual(resolved_func.__name__, document_detail.__name__)

    def test_add_comment_url(self):
        department = Department.objects.create(name='Test Dept')
        category = Category.objects.create(name='Test Cat', department=department)
        document = Document.objects.create(
            title='Test Doc',
            content='Content',
            author=self.user,
            category=category,
            department=department
        )
        url = reverse('add_comment', args=[document.slug])
        resolved_func = resolve(url).func
        self.assertEqual(resolved_func.__name__, add_comment.__name__)

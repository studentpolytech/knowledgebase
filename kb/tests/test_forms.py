from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from kb.forms import DocumentForm, CommentForm
from kb.models import Department, Category

User = get_user_model()

class DocumentFormTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='IT')
        self.category = Category.objects.create(
            name='Guides',
            department=self.department
        )
        self.user = User.objects.create_user(
            username='formtester',
            password='testpass123',
            department=self.department
        )

    def test_valid_document_form(self):
        form_data = {
            'title': 'Test Document',
            'content': 'Content',
            'category': self.category.id,
            'department': self.department.id
        }
        form = DocumentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_document_form_with_file(self):
        test_file = SimpleUploadedFile(
            'test.pdf',
            b'file_content',
            content_type='application/pdf'
        )
        form_data = {
            'title': 'Test PDF',
            'content': 'Content',
            'category': self.category.id,
            'department': self.department.id
        }
        form = DocumentForm(data=form_data, files={'file': test_file})
        self.assertTrue(form.is_valid())

    def test_invalid_file_type(self):
        test_file = SimpleUploadedFile(
            'test.exe',
            b'file_content',
            content_type='application/exe'
        )
        form_data = {
            'title': 'Test File',
            'content': 'Content',
            'category': self.category.id,
            'department': self.department.id
        }
        form = DocumentForm(data=form_data, files={'file': test_file})
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)

class CommentFormTest(TestCase):
    def test_valid_comment_form(self):
        form_data = {
            'text': 'Test comment',
            'link': 'https://example.com'
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form_no_text(self):
        form_data = {
            'text': '',
            'link': 'https://example.com'
        }
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_link(self):
        form_data = {
            'text': 'Test comment',
            'link': 'ftp://example.com'  # Неподходящий протокол
        }
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('link', form.errors)

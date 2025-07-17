from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from kb.models import Department, Category, Document, Comment
import os

User = get_user_model()

class DepartmentModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(
            name='Test Department',
            description='Test Description'
        )

    def test_department_creation(self):
        self.assertEqual(self.department.name, 'Test Department')
        self.assertEqual(self.department.slug, 'test-department')
        self.assertEqual(str(self.department), 'Test Department')

    def test_slug_auto_generation(self):
        dept = Department.objects.create(name='Another Department')
        self.assertEqual(dept.slug, 'another-department')

class CustomUserModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='HR')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            user_type='MANAGER',
            department=self.department,
            position='HR Manager'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.user_type, 'MANAGER')
        self.assertEqual(self.user.department.name, 'HR')
        self.assertTrue(self.user.check_password('testpass123'))

class CategoryModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Finance')
        self.category = Category.objects.create(
            name='Reports',
            department=self.department,
            description='Financial reports'
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Reports')
        self.assertEqual(self.category.department.name, 'Finance')
        self.assertEqual(str(self.category), 'Reports (Finance)')

class DocumentModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='IT')
        self.user = User.objects.create_user(
            username='doccreator',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Guides',
            department=self.department
        )
        self.document = Document.objects.create(
            title='Installation Guide',
            content='Step by step guide',
            author=self.user,
            category=self.category,
            department=self.department
        )

    def test_document_creation(self):
        self.assertEqual(self.document.title, 'Installation Guide')
        self.assertTrue(self.document.slug.startswith('installation-guide'))
        self.assertTrue(self.document.is_published)
        self.assertEqual(self.document.author.username, 'doccreator')

    def test_file_upload(self):
        test_file = SimpleUploadedFile(
            'test.pdf',
            b'file_content',
            content_type='application/pdf'
        )
        doc = Document.objects.create(
            title='Test PDF',
            content='Content',
            author=self.user,
            category=self.category,
            department=self.department,
            file=test_file
        )
        self.assertEqual(doc.extension(), 'pdf')
        os.remove(doc.file.path)  # Clean up

class CommentModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Marketing')
        self.user = User.objects.create_user(
            username='commenter',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Campaigns',
            department=self.department
        )
        self.document = Document.objects.create(
            title='Summer Campaign',
            content='Details',
            author=self.user,
            category=self.category,
            department=self.department
        )
        self.comment = Comment.objects.create(
            document=self.document,
            author=self.user,
            text='Great campaign!',
            link='https://example.com'
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.text, 'Great campaign!')
        self.assertEqual(self.comment.link, 'https://example.com')
        self.assertTrue(self.comment.is_active)
        self.assertEqual(str(self.comment), f'Комментарий {self.comment.id} к документу Summer Campaign')
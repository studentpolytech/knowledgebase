from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from kb.models import Department, Category, Document, Comment

User = get_user_model()

class DocumentListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(name='Sales')
        self.user = User.objects.create_user(
            username='salesuser',
            password='testpass123',
            department=self.department
        )
        self.category = Category.objects.create(
            name='Contracts',
            department=self.department
        )
        self.document = Document.objects.create(
            title='Sales Contract',
            content='Content',
            author=self.user,
            category=self.category,
            department=self.department
        )

    def test_document_list_view_authenticated(self):
        self.client.login(username='salesuser', password='testpass123')
        response = self.client.get(reverse('document_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sales Contract')

    def test_document_list_view_unauthenticated(self):
        response = self.client.get(reverse('document_list'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('document_list')}")

    def test_document_list_filter_by_category(self):
        self.client.login(username='salesuser', password='testpass123')
        response = self.client.get(f"{reverse('document_list')}?category={self.category.id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sales Contract')

class DocumentDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(name='HR')
        self.user = User.objects.create_user(
            username='hruser',
            password='testpass123',
            department=self.department
        )
        self.category = Category.objects.create(
            name='Policies',
            department=self.department
        )
        self.document = Document.objects.create(
            title='HR Policy',
            content='Content',
            author=self.user,
            category=self.category,
            department=self.department
        )

    def test_document_detail_view(self):
        self.client.login(username='hruser', password='testpass123')
        response = self.client.get(reverse('document_detail', args=[self.document.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'HR Policy')

    def test_document_detail_view_no_access(self):
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123',
            department=Department.objects.create(name='IT')
        )
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('document_detail', args=[self.document.slug]))
        self.assertEqual(response.status_code, 403)  # Forbidden

class CommentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(name='Finance')
        self.user = User.objects.create_user(
            username='financeuser',
            password='testpass123',
            department=self.department
        )
        self.category = Category.objects.create(
            name='Reports',
            department=self.department
        )
        self.document = Document.objects.create(
            title='Financial Report',
            content='Content',
            author=self.user,
            category=self.category,
            department=self.department
        )

    def test_add_comment(self):
        self.client.login(username='financeuser', password='testpass123')
        response = self.client.post(
            reverse('add_comment', args=[self.document.slug]),
            {'text': 'Test comment', 'link': 'https://example.com'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(Comment.objects.count(), 1)

    def test_delete_comment(self):
        self.client.login(username='financeuser', password='testpass123')
        comment = Comment.objects.create(
            document=self.document,
            author=self.user,
            text='Test comment'
        )
        response = self.client.post(
            reverse('delete_comment', args=[comment.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 0)
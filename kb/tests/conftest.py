import pytest
from django.contrib.auth import get_user_model
from kb.models import Department, Category, Document

User = get_user_model()

@pytest.fixture
def department():
    return Department.objects.create(name='Test Department')

@pytest.fixture
def category(department):
    return Category.objects.create(
        name='Test Category',
        department=department
    )

@pytest.fixture
def user(department):
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        department=department
    )

@pytest.fixture
def document(user, category, department):
    return Document.objects.create(
        title='Test Document',
        content='Test Content',
        author=user,
        category=category,
        department=department
    )
import time
import os
from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser

# === DEPARTMENT ===
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# === CUSTOM USER ===
class CustomUser(AbstractUser):
    USER_TYPES = (
        ('ADMIN', 'Administrator'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employee'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='EMPLOYEE')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField(max_length=100, blank=True)

    class Meta:
        permissions = [
            ("manage_departments", "Can manage departments"),
            ("manage_categories", "Can manage categories"),
            ("manage_documents", "Can manage documents"),
            ("view_all_documents", "Can view all documents"),
        ]

# === CATEGORY ===
class Category(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.department.name})"

# === FILE PATH ===
def document_upload_path(instance, filename):
    return f'documents/{instance.department.slug}/{instance.category.name}/{filename}'

# === DOCUMENT ===
class Document(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])],
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Генерируем slug из title, добавляя timestamp для уникальности
            base_slug = slugify(self.title)
            unique_slug = base_slug
            timestamp = int(time.time())
            while Document.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{timestamp}"
                timestamp += 1
            self.slug = unique_slug
        super().save(*args, **kwargs) #изменено на автоматисческое добавление адреса при создании документа

    def extension(self):
        return os.path.splitext(self.file.name)[1][1:].lower() if self.file else None

    def __str__(self):
        return self.title

# === COMMENT ===
class Comment(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    link = models.URLField(blank=True, null=True, max_length=500)  # Новое поле
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Комментарий {self.id} к документу {self.document.title}"

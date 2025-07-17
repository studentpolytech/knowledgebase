from django import forms
from .models import Document, Comment
from django.core.exceptions import ValidationError
import mimetypes

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'content', 'category', 'department', 'file']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Определяем тип файла по расширению
            mime_type, _ = mimetypes.guess_type(file.name)

            allowed_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'image/jpeg',
                'image/png'
            ]

            if mime_type not in allowed_types:
                raise ValidationError("Недопустимый тип файла")

            if file.size > 10 * 1024 * 1024:
                raise ValidationError("Файл слишком большой (максимум 10MB)")

        return file


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'link']  # Добавляем link

    def clean_link(self):
        link = self.cleaned_data.get('link')
        if link and not link.startswith(('http://', 'https://')):
            raise ValidationError("Ссылка должна начинаться с http:// или https://")
        return link

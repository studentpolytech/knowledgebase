from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from .models import Document, Category
from .forms import DocumentForm


class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'kb/document_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.department:
            form.fields['category'].queryset = Category.objects.filter(
                department=self.request.user.department
            )
            # Установим department по умолчанию из пользователя
            form.fields['department'].initial = self.request.user.department
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        
        # Если department не выбран в форме, берем из пользователя
        if not form.cleaned_data.get('department') and self.request.user.department:
            form.instance.department = self.request.user.department
        
        # Проверяем, что department установлен
        if not form.instance.department:
            form.add_error('department', 'Необходимо выбрать отдел')
            return self.form_invalid(form)
            
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('document_detail', kwargs={'slug': self.object.slug})


class DocumentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "kb/document_form.html"

    def test_func(self):
        doc = self.get_object()
        return (
            self.request.user.user_type == 'ADMIN' or
            self.request.user == doc.author or
            self.request.user.has_perm('kb.manage_documents')
        )

    def get_success_url(self):
        return reverse_lazy('document_detail', kwargs={'slug': self.object.slug})


class DocumentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Document
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = 'kb/document_confirm_delete.html'
    success_url = reverse_lazy('document_list')

    def test_func(self):
        doc = self.get_object()
        return (
            self.request.user.user_type == 'ADMIN' or
            self.request.user == doc.author or
            self.request.user.has_perm('kb.manage_documents')
        )

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Удаляем связанные комментарии перед удалением документа
        self.object.comments.all().delete()
        return super().delete(request, *args, **kwargs)

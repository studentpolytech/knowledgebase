from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Document, Comment, Department, Category


@login_required(login_url='/accounts/login/')
def home(request):
    """Главная страница"""
    if request.user.is_authenticated and not request.user.department:
        if request.user.user_type in ['EMPLOYEE', 'MANAGER']:
            return render(request, 'kb/access_denied.html', {
                'message': 'Ваш аккаунт не привязан к отделу. Обратитесь к администратору.'
            })
    return render(request, 'kb/home.html')


@login_required
def select_department(request):
    """Выбор отдела"""
    if request.method == 'POST':
        department_id = request.POST.get('department')
        department = get_object_or_404(Department, id=department_id)
        request.user.department = department
        request.user.save()
        messages.success(request, f'Выбран отдел: {department.name}')
        return redirect('document_list')
    return redirect('home')


@login_required
def document_list(request):
    """Список документов"""
    if request.user.user_type == 'EMPLOYEE' and not request.user.department:
        return render(request, 'kb/access_denied.html', {
            'message': 'Ваш аккаунт не привязан к отделу. Обратитесь к администратору.'
        })

    if request.user.user_type == 'ADMIN':
        documents = Document.objects.filter(is_published=True)
    else:
        documents = Document.objects.filter(
            is_published=True,
            department=request.user.department
        )

    categories = Category.objects.filter(department=request.user.department) if request.user.department else Category.objects.all()

    category_id = request.GET.get('category')
    selected_category = None
    if category_id:
        try:
            documents = documents.filter(category_id=category_id)
            selected_category = Category.objects.get(id=category_id)
        except (ValueError, Category.DoesNotExist):
            selected_category = None

    return render(request, 'kb/document_list.html', {
        'documents': documents,
        'categories': categories,
        'selected_category': selected_category,
        'can_add_document': request.user.has_perm('kb.manage_documents') or
                            request.user.user_type in ['MANAGER', 'ADMIN']
    })


@login_required
def document_detail(request, slug):
    """Детали документа"""
    document = get_object_or_404(Document, slug=slug)

    if request.user.user_type != 'ADMIN':
        if not document.is_published and not request.user.has_perm('kb.manage_documents'):
            raise PermissionDenied
        if request.user.department != document.department:
            raise PermissionDenied

    if not check_document_access(request.user, document):
        raise PermissionDenied

    if request.method == 'POST':
        return handle_post_requests(request, document)

    comments = document.comments.filter(is_active=True)

    can_delete_comments = (
        request.user.user_type == 'ADMIN' or
        (request.user.user_type == 'MANAGER' and request.user.department == document.department)
    )

    can_manage_documents = request.user.has_perm('kb.manage_documents')

    return render(request, 'kb/document_detail.html', {
        'document': document,
        'comments': comments,
        'can_delete_comments': can_delete_comments,
        'can_add_comment': request.user.department == document.department,
        'user': request.user,
        'can_manage_documents': can_manage_documents,
    })


@login_required
def add_comment(request, slug):
    """Добавить комментарий"""
    document = get_object_or_404(Document, slug=slug)
    
    if not (request.user.user_type == 'ADMIN' or 
            (request.user.department and request.user.department == document.department)):
        raise PermissionDenied

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        link = request.POST.get('link', '').strip()
        
        if text:  # Комментарий не может быть пустым
            Comment.objects.create(
                document=document,
                author=request.user,
                text=text,
                link=link if link else None  # Сохраняем ссылку, если она есть
            )
            messages.success(request, 'Комментарий добавлен')
    
    return redirect('document_detail', slug=document.slug)

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, id=pk)
    document = comment.document

    if not (
        request.user.user_type == 'ADMIN' or
        (request.user.user_type == 'MANAGER' and request.user.department == document.department) or
        (request.user == comment.author)
    ):
        raise PermissionDenied

    comment.delete()
    messages.success(request, 'Комментарий удален')
    return redirect('document_detail', slug=document.slug)


# Вспомогательные функции

def check_document_access(user, document):
    """Проверка доступа к документу"""
    if user.user_type == 'ADMIN':
        return True
    if not document.is_published and not user.has_perm('kb.manage_documents'):
        return False
    return user.department == document.department


def handle_post_requests(request, document):
    """Обработка POST-запросов (удаление комментариев и др.)"""
    if 'delete_comment' in request.POST:
        return delete_comment(request, request.POST.get('comment_id'))
    return redirect('document_detail', slug=document.slug)

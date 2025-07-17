from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import CustomUser, Department, Category, Document, Comment

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'department', 'position', 'is_staff')
    list_filter = ('user_type', 'department', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (_('Дополнительная информация'), {'fields': ('user_type', 'department', 'position')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Дополнительная информация'), {
            'fields': ('user_type', 'department', 'position', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'email', 'position')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.user_type == 'MANAGER':
            return qs.filter(department=request.user.department)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department" and request.user.user_type == 'MANAGER':
            kwargs["queryset"] = Department.objects.filter(id=request.user.department.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'description')
    list_filter = ('department',)
    search_fields = ('name', 'department__name', 'description')
    list_select_related = ('department',)
    raw_id_fields = ('department',)
    list_per_page = 20

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.user_type == 'MANAGER':
            return qs.filter(department=request.user.department)
        return qs

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'department', 'created_at', 
                    'is_published', 'comment_count', 'file_link')
    list_filter = ('department', 'category', 'is_published', 'created_at')
    search_fields = ('title', 'content', 'author__username', 'category__name')
    list_select_related = ('author', 'category', 'department')
    date_hierarchy = 'created_at'
    raw_id_fields = ('author',)
    list_per_page = 20
    actions = ['publish_documents', 'unpublish_documents']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.user_type == 'MANAGER':
            return qs.filter(department=request.user.department)
        elif request.user.user_type == 'EMPLOYEE':
            return qs.filter(department=request.user.department, is_published=True)
        return qs
    
    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = _('Комментарии')
    
    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}">Скачать</a>', obj.file.url)
        return "-"
    file_link.short_description = _('Файл')
    
    def publish_documents(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'Опубликовано документов: {updated}')
    publish_documents.short_description = _('Опубликовать выбранные документы')
    
    def unpublish_documents(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'Снято с публикации документов: {updated}')
    unpublish_documents.short_description = _('Снять с публикации выбранные документы')

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.title)
        super().save_model(request, obj, form, change)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('truncated_text', 'author', 'document_link', 'department', 
                   'created_at', 'is_active')
    list_filter = ('is_active', 'document__department', 'created_at')
    search_fields = ('text', 'author__username', 'document__title')
    list_editable = ('is_active',)
    list_select_related = ('author', 'document__department')
    date_hierarchy = 'created_at'
    actions = ['restore_comments', 'deactivate_comments']
    list_per_page = 20
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.user_type == 'MANAGER':
            return qs.filter(document__department=request.user.department)
        return qs
    
    def truncated_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    truncated_text.short_description = _('Текст комментария')
    
    def document_link(self, obj):
        return format_html('<a href="{}">{}</a>', 
                         f'/admin/kb/document/{obj.document.id}/change/',
                         obj.document.title)
    document_link.short_description = _('Документ')
    
    def department(self, obj):
        return obj.document.department
    department.short_description = _('Департамент')
    
    def restore_comments(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Восстановлено комментариев: {updated}')
    restore_comments.short_description = _('Восстановить выбранные комментарии')
    
    def deactivate_comments(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано комментариев: {updated}')
    deactivate_comments.short_description = _('Деактивировать выбранные комментарии')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Comment, CommentAdmin)
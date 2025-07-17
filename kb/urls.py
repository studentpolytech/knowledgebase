from django.urls import path, include
from . import views
from django.contrib.auth.decorators import login_required
from .views_class_based import (
    DocumentCreateView,
    DocumentUpdateView,
    DocumentDeleteView
)

urlpatterns = [
    #path('', views.home, name='home'),
    path('select-department/', views.select_department, name='select_department'),
    path('documents/', views.document_list, name='document_list'),
    path('documents/create/', DocumentCreateView.as_view(), name='document_create'),
    path('documents/<slug:slug>/edit/', DocumentUpdateView.as_view(), name='document_update'),
    path('documents/<slug:slug>/delete/', DocumentDeleteView.as_view(), name='document_delete'),
    path('documents/<slug:slug>/add_comment/', views.add_comment, name='add_comment'),
    path('documents/<slug:slug>/', views.document_detail, name='document_detail'),
    path('comments/<int:pk>/delete/', views.delete_comment, name='delete_comment'),

    path('', login_required(views.home), name='home'),
    # Страницы входа и выхода
    path('accounts/', include('django.contrib.auth.urls')),
]

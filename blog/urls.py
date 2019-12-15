from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_new, name='post_new'),
    path('user_registration/', views.user_registration, name='user_registration'),
    path('logout/', views.logout_request, name='logout'),
    path('login/', views.login_request, name='login'),
]
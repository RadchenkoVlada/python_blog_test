from django.urls import path
from . import views
from .views import AddCommentToPost, AddReplyToPost

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_new, name='post_new'),
    path('user_registration/', views.user_registration, name='user_registration'),
    path('logout/', views.logout_request, name='logout'),
    path('login/', views.login_request, name='login'),
    # new url for class-based view
    path('post/<int:pk>/reply/',  AddCommentToPost.as_view(), name='add_comment_to_post'),
    path('post/<int:pk>/reply/<int:parent_pk>/', AddReplyToPost.as_view(), name='add_reply_to_post'),

    # path('post/<int:pk>/reply/', views.add_comment_to_post, name='add_comment_to_post'),
    # path('post/<int:pk>/reply/<int:parent_pk>/', views.add_reply_to_post, name='add_reply_to_post'),
]

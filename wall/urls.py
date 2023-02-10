from django.urls import path
from . import views


urlpatterns = [
    path('comment/', views.CommentView.as_view({'post': 'create'})),
    path('comment/<int:pk>/', views.CommentView.as_view({'put': 'update', 'delete': 'destroy'})),
    path('post/', views.PostRetrieveView.as_view({'post': 'create'})),
    path('post/<int:pk>/', views.PostRetrieveView.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy'
    })),
    path('<int:pk>/', views.PostListView.as_view()),
    path('post/my/', views.PostAuthorView.as_view()),
    path('post/draft/', views.UserDraftPosts.as_view())
]

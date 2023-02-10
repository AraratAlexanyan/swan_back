from django.urls import path
from .import views

urlpatterns = [
     path('sub/<int:pk>/', views.FollowerView.as_view()),
     path('sub/', views.ListFollowersView.as_view()),
     path('fav/', views.ListFollowersView.as_view()),
]

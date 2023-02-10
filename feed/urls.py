from django.urls import path

from .views import *

urlpatterns = [
    path('', FeedView.as_view({'get': 'list'})),
    path('<int:pk>/', FeedView.as_view({'get': 'retrieve'})),
]

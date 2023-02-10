from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginApiView.as_view()),
    path('reg/', RegisterApiView.as_view()),
    path('verify/', EmailVerification.as_view()),
    path('refresh_token/', CookieTokenRefresh.as_view()),
    path('logout/', logout_view),
    path('user/', UserDetail.as_view()),
]

from django.urls import path

from core.login.views import *

urlpatterns = [
    path('', LoginFormView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('reset/password/', resetPasswordView.as_view(), name='reset_password'),
    path('change/password/<str:token>/', changePasswordView.as_view(), name='change_password')
    # path('logout/', LogoutRedirectView.as_view(), name='logout')
]

# urls.py

from django.urls import path
from .views import LoginView, LogoutView, ProtectedView, UserRegistrationAPIView, GetUserAccountAPIView, \
    UserByRoleAPIView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('register/', UserRegistrationAPIView.as_view(), name='user_register'),
    path('user/', GetUserAccountAPIView.as_view(), name='get_user_account'),
    path('users/by_role/<str:role>/', UserByRoleAPIView.as_view(), name='users_by_role'),

]

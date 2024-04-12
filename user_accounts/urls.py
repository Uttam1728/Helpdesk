# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LoginView, LogoutView, ProtectedView, AccountViewSet

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('', include(router.urls)),

]

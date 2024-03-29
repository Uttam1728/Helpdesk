# urls.py

from django.urls import path
from .views import TokenRefreshView

urlpatterns = [

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

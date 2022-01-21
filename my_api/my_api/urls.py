"""my_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # endpoinst for testing
    path('api/test', views.test_get, name='test_get'),
    path('api/test/<int:id>', views.test_get_path_param, name='test_get_path_param'),
    path('api/test/query', views.test_get_query_param, name='test_get_query_param'),
    path('api/test/body', views.test_post_body, name='test_post_body'),
    path('api/test/suma', views.test_suma, name='suma'),
    path('api/test/suma_mas', views.test_suma_mas, name='suma_mas'),
    path('api/test/bueno', views.test_bueno, name='test_bueno'),
    #production endpoints
    path('api/accounts', views.accounts_view, name="accounts_view"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

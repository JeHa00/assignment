"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from config.settings.base import API_V1_PREFIX

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    # drf-spectacular
    path(f"{API_V1_PREFIX}/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        f"{API_V1_PREFIX}/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-swagger-ui",
    ),
    # simplejwt,
    path("api/token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/verification", TokenVerifyView.as_view(), name="token_verify"),
    path("api/token/refresh-token", TokenRefreshView.as_view(), name="token_refresh"),
    # locals
    path(f"{API_V1_PREFIX}/accounts", include("accounts.urls")),
    path(f"{API_V1_PREFIX}/tasks", include("tasks.urls")),
    path(f"{API_V1_PREFIX}", include("subtasks.urls")),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

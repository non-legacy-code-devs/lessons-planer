from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.conf import settings
from routers import router
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from backend.views import (
    ActivateUser,
    ChangePasswordAfterRegister,
    index,
)


schema_view = get_schema_view(
    openapi.Info(
        title="WK-Backend API",
        default_version="v1",
        description="Docs for Bartek & Daniel <3",
        contact=openapi.Contact(email="tomasz.jastrzebski@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

app_name = "backend"

urlpatterns = [
    path("blog/", include("cms.urls")),
    path("admin/", admin.site.urls),
    path("taggit_autosuggest/", include("taggit_autosuggest.urls")),
    path("api/", include((router.urls, "myapp"), namespace="api")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path(
        r"docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "activate/<uid>/<token>/",
        ActivateUser.as_view({"get": "activation"}),
        name="activation",
    ),
    path(
        "api/change_default_password/<id>/",
        ChangePasswordAfterRegister.as_view({"patch": "update"}),
    ),
    path(r"redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    re_path(r"^.*", index, name="index"),
    # All urls not specified in backend will be handled by react frontend
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

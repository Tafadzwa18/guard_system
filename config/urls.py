from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.shortcuts import redirect

urlpatterns = [
    path("", lambda request: redirect("guard_home"), name="home"),

    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("", include("patrols.urls")),
    path("", include("dashboard.urls")),
]

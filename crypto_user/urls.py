from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("signup/", views.crypto_user_signup, name="signup"),
    path("login/", views.crypto_user_login, name="login"),
    path("logout/", views.crypto_user_logout, name="logout"),
    path("kyc/", views.user_kyc, name="kyc"),
    path("dashboard/", views.user_dashboard, name="dashboard"),
    path("coin-register/", views.order_execute, name="order_execute"),
    path("activity/", views.coin_activity, name="activity"),
]

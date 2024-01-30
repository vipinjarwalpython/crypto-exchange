from django.urls import path
from crypto_user.user_api.views import *


urlpatterns = [
    path("signup/", UserSignupView.as_view()),
    path("login/", UserLoginView.as_view()),
    path("logout/", UserLogoutView.as_view()),
    path("kyc/", UserKycView.as_view()),
    path("user-dashboard/", UserDashboardView.as_view()),
    path("user-coin/", UserCoinView.as_view()),
    path("order-execute/", OrderExecuteViews.as_view()),
    path("coin-activity/", UserCoinsActivityViews.as_view()),
    path("fund-activity/", UserFundsActivityViews.as_view()),
    # path("coin-register/", views.order_execute, name="order_execute"),
]

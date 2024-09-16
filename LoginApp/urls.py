from django.urls import path
from . import views

app_name = "LoginApp"

urlpatterns = [
    path("", views.loginMe, name="login"),
    path('superuser/<str:token>', views.superuserLogin, name='superuserLogin'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logoutMe, name='logout'),
]
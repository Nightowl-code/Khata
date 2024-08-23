from django.urls import path
from . import views

app_name = "MainApp"

urlpatterns = [
    path("", views.home, name="home"),
    path("addtransaction", views.addTransaction, name="addtransaction"),
    path("users", views.users, name="users"),
    path('createuser', views.createUser, name="createuser"),\
    path('user/<str:id>', views.user, name="user"),
    path('edituser/<str:id>', views.editUser, name="edituser"),
    path('deleteuser/<str:id>', views.deleteUser, name="deleteuser"),
]
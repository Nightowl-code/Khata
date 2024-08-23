from django.shortcuts import render, HttpResponse, HttpResponseRedirect,redirect
from .forms import TransactionForm, UserForm
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializers import CustomUserSerializer, TransactionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Transaction, CustomUser

def home(request):
    if request.user.is_authenticated:
        return render(request, "MainApp/home.html")
    else:
        return HttpResponseRedirect("/login")
    
def addTransaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("MainApp:user",form.cleaned_data["party"].username)
        else:
           form = TransactionForm()
           return render(request, "MainApp/addTransaction.html", {"form": form})
    else:
        party = request.GET.get("party")
        transaction_type = request.GET.get("type")
        if party and transaction_type:
            user=CustomUser.objects.get(username=party)
            form = TransactionForm(prefill={"party": user.id, "type": transaction_type})
        else:
            form = TransactionForm()
        return render(request, "MainApp/addTransaction.html", {"form": form})

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def users(request):
    if request.method == "GET":
        users = CustomUser.objects.filter(is_staff=False)
        serializer = CustomUserSerializer(users, many=True)
        return render(request, "MainApp/users.html", {"users": serializer.data})
    

def createUser(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("MainApp:users")
        else:
            return render(request, "MainApp/createUser.html", {"form": UserForm(),"error": form.errors,"action":'createuser'})
    else:
        form = UserForm()
        return render(request, "MainApp/createUser.html", {"form": form,"action":'createuser'})
    
def user(request, id):
    user = CustomUser.objects.get(username=id)
    transactions = Transaction.objects.filter(party=user)
    return render(request, "MainApp/user.html", {"user": user, "transactions": transactions})

def editUser(request,id):
    user = CustomUser.objects.get(username=id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("MainApp:users")
        else:
            return render(request, "MainApp/CreateUser.html", {"form": form, "user": user,"action":'edituser/{}'.format(id),"error": form.errors})
    else:
        form = UserForm(instance=user)
        return render(request, "MainApp/CreateUser.html", {"form": form, "user": user,"action":'edituser/{}'.format(id)})
    
def deleteUser(request,id):
    user = CustomUser.objects.get(username=id)
    user.delete()
    return redirect("MainApp:users")
    

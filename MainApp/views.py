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
        if request.user.is_staff:
            users = CustomUser.objects.filter(is_staff=False)
            # add amount of all users.amount in amount variable
            # user with highest credit amount and highest debit amount
            # if users has no 
            if len(users) == 0:
                amount = {
                    "value" : "0",
                    "type": "credit"
                }
                return render(request, "MainApp/home.html",{"amount": amount})
            max_credit_user = users[0]
            max_debit_user = users[0]
            amount = 0
            for user in users:
                if user.amount > max_credit_user.amount:
                    max_credit_user = user
                if user.amount < max_debit_user.amount:
                    max_debit_user = user
                amount += user.amount
            amount = {
                "value" : str(amount),
                "type": "credit" if amount >= 0 else "debit"
            }
            
            transaction = Transaction.objects.filter(party__is_staff=False)
            credit_transaction = transaction.filter(type="credit")
            debit_transaction = transaction.filter(type="debit")
            # get the highest credit and debit transaction
            if len(credit_transaction) == 0 or len(debit_transaction) == 0:
                max_credit_transaction = None
                max_debit_transaction = None
            else:
                max_credit_transaction = credit_transaction[0]
                max_debit_transaction = debit_transaction[0]
                for t in credit_transaction:
                    if t.amount > max_credit_transaction.amount:
                        max_credit_transaction = t
                for t in debit_transaction:
                    if t.amount > max_debit_transaction.amount:
                        max_debit_transaction = t
            
            # last 10 transactions
            current_transaction = transaction.order_by('-date')[:20]

            return render(request, "MainApp/home.html",{"amount": amount, "max_credit_user": max_credit_user, "max_debit_user": max_debit_user, "max_credit_transaction": max_credit_transaction, "max_debit_transaction": max_debit_transaction, "current_transaction": current_transaction})
        else:
            return redirect("MainApp:user",request.user.username)
    else:
        return HttpResponseRedirect("/login")
    
def addTransaction(request):
    if not request.user.is_staff:
        return redirect("MainApp:home")
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("MainApp:user",form.cleaned_data["party"].username)
        else:
           form = TransactionForm()
           return render(request, "MainApp/addTransaction.html", {"form": form,"action_link":"addtransaction"})
    else:
        previous_url = request.META.get('HTTP_REFERER')
        party = request.GET.get("party")
        transaction_type = request.GET.get("type")
        if party and transaction_type:
            user=CustomUser.objects.get(username=party)
            form = TransactionForm(prefill={"party": user.id, "type": transaction_type})
        elif transaction_type:
            form = TransactionForm(prefill={"type": transaction_type})
        else:
            form = TransactionForm()
        return render(request, "MainApp/addTransaction.html", {"form": form,"action_link":"addtransaction"+"?next="+previous_url})

@api_view(['GET', 'POST'])
def users(request):
    if not request.user.is_staff:
        return redirect("MainApp:home")
    if request.method == "GET":
        users = CustomUser.objects.filter(is_staff=False)
        # oder users by username
        users = users.order_by('username')
        serializer = CustomUserSerializer(users, many=True)
        return render(request, "MainApp/users.html", {"users": serializer.data})
    elif request.method == "POST":
        users = CustomUser.objects.filter(is_staff=False)
        user_serializer = CustomUserSerializer(users, many=True)
        return Response(user_serializer.data)
    

def createUser(request):
    if not request.user.is_staff:
        return redirect("MainApp:home")
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            return redirect("MainApp:users")
        else:
            return render(request, "MainApp/createUser.html", {"form": UserForm(),"error": form.errors,"action":'createuser'})
    else:
        form = UserForm()
        return render(request, "MainApp/createUser.html", {"form": form,"action":'createuser'})
    
def user(request, id):
    if not request.user.is_staff and request.user.username != id:
        return redirect("MainApp:home")
    user = CustomUser.objects.get(username=id)
    transactions = Transaction.objects.filter(party=user)
    return render(request, "MainApp/user.html", {"user1": user, "transactions": transactions})

def editUser(request,id):
    if not request.user.is_staff and request.user.username != id:
        return redirect("MainApp:home")
    user = CustomUser.objects.get(username=id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            if request.user.is_staff:
                return redirect("MainApp:users")
            else:
                return redirect("MainApp:home")
        else:
            return render(request, "MainApp/createUser.html", {"form": form, "user": user,"action":'edituser/{}'.format(id),"error": form.errors})
    else:
        form = UserForm(instance=user)
        return render(request, "MainApp/createUser.html", {"form": form, "user": user,"action":'edituser/{}'.format(id)})
    
def deleteUser(request,id):
    if not request.user.is_staff:
        return redirect("MainApp:home")
    user = CustomUser.objects.get(username=id)
    user.delete()
    return redirect("MainApp:users")

@api_view(['GET', 'POST'])
def hisab(request):
    if not request.user.is_staff:
        return redirect("MainApp:home")
    transactions = Transaction.objects.filter(party__is_staff=False)
    transactions = transactions.order_by('date')
    if request.method == "POST":
        transactions = TransactionSerializer(transactions, many=True)
        # print(transactions.data)
        return Response(transactions.data)
    else:
        users = CustomUser.objects.filter(is_staff=False)
        # add amount of all users.amount in amount variable
        amount = 0
        for user in users:
            amount += user.amount
        amount = {
            "value" : str(amount),
            "type": "credit" if amount >= 0 else "debit"
        }
        # print(amount)
        
        transactions = TransactionSerializer(transactions, many=True)
        return render(request, "MainApp/hisab.html", {"transactions": transactions.data, "amount": amount})

def hisabView(request,id):
    transaction = Transaction.objects.get(id=id)
    if not request.user.is_staff and request.user != transaction.party:
        return redirect("MainApp:home")
    transaction = TransactionSerializer(transaction)
    # get the page url from where the request came
    previous_url = request.META.get('HTTP_REFERER')
    return render(request, "MainApp/hisabView.html",{"transaction": transaction.data, "previous_url": previous_url})

def deleteTransaction(request,id):
    previous_url = request.GET.get('next')
    # print("previous_url:",previous_url)
    if not request.user.is_staff:
        return redirect("MainApp:home")
    transaction = Transaction.objects.get(id=id)
    transaction.delete()
    if previous_url:
        return redirect(previous_url)
    else:
        return redirect("MainApp:hisab")
    
def editTransaction(request, id):
    if not request.user.is_staff:
        return redirect("MainApp:home")
    previous_url = request.GET.get('next')
    if not previous_url:
        previous_url = request.POST.get('next')
    transaction = Transaction.objects.get(id=id)
    # print("previous: ",previous_url)
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            if previous_url:
                return redirect(previous_url)
            else:
                return redirect("MainApp:hisab")
        else:
            return render(request, "MainApp/addTransaction.html", {"form": form, 'action_link': "editTransaction/" + str(id)+"?next="+previous_url})
    else:
        form = TransactionForm(instance=transaction)
        return render(request, "MainApp/addTransaction.html", {"form": form, 'action_link': "editTransaction/" + str(id)+"?next="+previous_url})
    
def updatePassword(request):
    return editUser(request,request.user.username)


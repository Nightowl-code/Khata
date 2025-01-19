from django.shortcuts import render, HttpResponse, HttpResponseRedirect,redirect
from .forms import TransactionForm, UserForm
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializers import CustomUserSerializer, TransactionSerializer, SiteSettingsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Transaction, CustomUser, SiteSettings
from datetime import timedelta,date


def home(request):
    print(request.user,request.user.is_authenticated,request.user.is_staff)
    if request.user.is_authenticated:
        if request.user.is_staff:
            return render(request, "MainApp/home.html")
        else:
            return redirect("MainApp:user",request.user.username)
    else:
        return HttpResponseRedirect("/login")

def recent(request):
    requested_date = date.today().strftime("%Y-%m-%d")
    if request.method == "POST":
        requested_date = request.POST.get("date")
        if not requested_date:
            requested_date = date.today().strftime("%Y-%m-%d")
    print(requested_date)
    if request.user.is_authenticated:
        if request.user.is_superuser:
            users = CustomUser.objects.filter(is_staff=False)
            # add amount of all users.amount in amount variable
            # user with highest credit amount and highest debit amount
            # if users has no 
            settings = SiteSettings.objects.first()
            settings = SiteSettingsSerializer(settings)
            
            transaction = Transaction.objects.filter(party__is_staff=False)

            # get transaction of the requested_date
            current_transaction = transaction.filter(date=requested_date).order_by('-date','-id')

            total_credit =0
            total_debit = 0
            for transaction in current_transaction:
                if transaction.type == "credit":
                    total_credit += transaction.amount
                else:
                    total_debit += transaction.amount
            amount = {
                "credit":total_credit,
                "debit":total_debit
            }

            scheme = request.scheme  # http or https
            host = request.get_host()  # subdomain.domain.com
    
            # Combine scheme and host
            base_url = f"{scheme}://{host}"

            return render(request, "MainApp/recent.html",{"amount": amount,"current_transaction": current_transaction,"settings":settings.data,"base_url":base_url,'current_date':requested_date})
        elif request.user.is_staff:
            users = CustomUser.objects.filter(is_staff=False)
            # add amount of all users.amount in amount variable
            # user with highest credit amount and highest debit amount
            # if users has no 
            
            transaction = Transaction.objects.filter(party__is_staff=False)
            # get transaction of last 1 week
            # get todays date
            todays_transaction = transaction.filter(date=requested_date).order_by('-date','-id')
            total_credit =0
            total_debit = 0
            for transaction in todays_transaction:
                if transaction.type == "credit":
                    total_credit += transaction.amount
                else:
                    total_debit += transaction.amount
            amount = {
                "credit":total_credit,
                "debit":total_debit
            }

            return render(request, "MainApp/recent.html",{"amount":amount,"current_transaction": todays_transaction,'current_date':requested_date})
        else:
            return redirect("MainApp:user",request.user.username)
    else:
        return HttpResponseRedirect("/login")
    
def addTransaction(request):
    if not request.user.is_staff:
        return redirect("MainApp:home")
    
    # Ensure previous_url is never None
    previous_url = request.GET.get('next', request.META.get('HTTP_REFERER'))
    
    # If previous_url is still None, assign a default value
    if previous_url is None:
        previous_url = "/default-redirect-url/"  # Replace with an appropriate default

    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            if request.POST.get('submit') == 'Add Another Transaction':
                # Pre-fill the party field with the previously entered value
                form = TransactionForm(initial={"party": form.cleaned_data['party'].id})
                return render(request, "MainApp/addTransaction.html", {
                    "form": form,
                    "action_link": "addtransaction" + "?next=" + previous_url
                })
            else:
                return redirect("MainApp:user", form.cleaned_data["party"].username)
        else:
            # Re-render the form with errors and pass the previous_url
            return render(request, "MainApp/addTransaction.html", {
                "form": form,
                "action_link": "addtransaction" + "?next=" + previous_url
            })
    else:
        party = request.GET.get("party")
        transaction_type = request.GET.get("type")
        if party and transaction_type:
            user = CustomUser.objects.get(username=party)
            form = TransactionForm(initial={"party": user.id, "type": transaction_type})
        elif transaction_type:
            form = TransactionForm(initial={"type": transaction_type})
        elif party:
            user = CustomUser.objects.get(username=party)
            form = TransactionForm(initial={"party": user.id})
        else:
            form = TransactionForm()
        
        return render(request, "MainApp/addTransaction.html", {
            "form": form,
            "action_link": "addtransaction" + "?next=" + previous_url
        })


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
        return Response({"users_data":user_serializer.data,"user_type":request.user.is_superuser})
    

def createUser(request):
    if not request.user.is_staff:
        return redirect("MainApp:home")
    
    if request.method == "POST":
        form = UserForm(request.POST, user=request.user)  # Pass the current user
        if form.is_valid():
            form.save(commit=True)
            return redirect("MainApp:users")
        else:
            return render(request, "MainApp/createUser.html", {"form": form, "error": form.errors, "action": 'createuser'})
    else:
        form = UserForm(user=request.user)  # Pass the current user
        return render(request, "MainApp/createUser.html", {"form": form, "action": 'createuser'})

    
def user(request, id):
    if not request.user.is_staff and request.user.username != id:
        return redirect("MainApp:home")
    user = CustomUser.objects.get(username=id)
    transactions = Transaction.objects.filter(party=user).order_by('-sequence_number')
    if request.user.is_staff and not request.user.is_superuser:
    
        transactions = {}
        user.amount = 0
    if not request.user.is_staff:
        block_date = user.block_date
        # get transaction after block date
        if block_date:
            transactions = transactions.filter(date__gte=block_date)
            last_transaction = transactions.last()
            if last_transaction:
                amount = last_transaction.running_total - (last_transaction.amount if last_transaction.type == "credit" else -last_transaction.amount) 
                print("amount:",amount,last_transaction)
                return render(request, "MainApp/user.html", {"user1": user, "transactions": transactions,"last_transaction":amount if block_date else None})
    return render(request, "MainApp/user.html", {"user1": user, "transactions": transactions})

def editUser(request,id):
    if not request.user.is_staff:
        return redirect("MainApp:home")
    user = CustomUser.objects.get(username=id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            if request.user.is_superuser:
                return redirect("MainApp:users")
            else:
                return redirect("MainApp:home")
        else:
            return render(request, "MainApp/createUser.html", {"form": form, "user1": user,"action":'edituser/{}'.format(id),"error": form.errors})
    else:
        form = UserForm(instance=user)
        return render(request, "MainApp/createUser.html", {"form": form, "user1": user,"action":'edituser/{}'.format(id)})
    
def deleteUser(request,id):
    if not request.user.is_staff:
        return redirect("MainApp:home")
    user = CustomUser.objects.get(username=id)
    user.delete()
    return redirect("MainApp:users")

@api_view(['GET', 'POST'])
def hisab(request):
    if not request.user.is_superuser:
        return redirect("MainApp:home")
    transactions = Transaction.objects.filter(party__is_staff=False)
    transactions = transactions.order_by('-sequence_number')
    users = CustomUser.objects.filter(is_staff=False).order_by('-amount')
    users_data = CustomUserSerializer(users, many=True)
    if request.method == "POST":
        # transactions = TransactionSerializer(transactions, many=True)
        # print(transactions.data)
        return Response(users_data.data)
    else:
        users = CustomUser.objects.filter(is_staff=False)
        # add amount of all users.amount in amount variable
        amount = 0
        debit_amout=0
        credit_amout=0
        for user in users:
            amount += user.amount
            if user.amount < 0:
                debit_amout += user.amount
            else:
                credit_amout += user.amount
        amount = {
            "value" : str(amount),
            "type": "credit" if amount >= 0 else "debit",
            "debit_amout":str(debit_amout),
            "credit_amout":str(credit_amout)
        }
        # print(amount)
        
        transactions = TransactionSerializer(transactions, many=True)
        return render(request, "MainApp/hisab.html", {"amount": amount,'parties':users_data.data})

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

def blockDate(request,username):
    if request.method == "POST":
        block_date = request.POST.get("block_date")
        if not request.user.is_staff:
            return redirect("MainApp:home")
        if username=="ALL":
            users = CustomUser.objects.filter(is_staff=False)
            for user in users:
                user.block_date = block_date
                user.save()
            return redirect("MainApp:users")
        user = CustomUser.objects.get(username=username)
        user.block_date = block_date
        user.save()
        return redirect("MainApp:user",username)
    
def clearBlockDate(request):
    if request.method == "POST":
        if not request.user.is_staff:
            return redirect("MainApp:home")
        username = request.POST.get("username")
        if username=="ALL":
            users = CustomUser.objects.filter(is_staff=False)
            for user in users:
                user.block_date = None
                user.save()
            return JsonResponse({"status":"Successfull updated block date"})
        user = CustomUser.objects.get(username=username)
        user.block_date = None
        user.save()
        return JsonResponse({"status":"Successfull updated block date"})
    return JsonResponse({"status":"Failed to update block date"})

def updateSettings(request):
    if request.method == "POST":
        if not request.user.is_superuser:
            return redirect("MainApp:home")
        site_status = True if request.POST.get("site_state").lower() == "true" else False
        superuser_login_url = request.POST.get("site_url")
        updateRequest = request.POST.get("updateRequest")
        settings = SiteSettings.objects.first()
        if updateRequest == "site_status":        
            settings.is_site_available = site_status
        else:
            settings.superuser_login_url = superuser_login_url
        settings.save()
        return JsonResponse({"status":"Successfull updated settings"})
    return JsonResponse({"status":"Failed to update settings"})

def siteUnavailable(request):
    settings = SiteSettings.objects.first()
    if settings.is_site_available:
        return redirect("MainApp:home")
    return render(request, "MainApp/siteUnavailable.html")


from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login,logout
from django.http import JsonResponse, HttpResponse
from MainApp.views import home
from MainApp.models import SiteSettings

# Create your views here.
def loginMe(request):
    return render(request, "LoginApp/login.html")


def signin(request):
    if request.method == 'POST':
        setting = SiteSettings.objects.first()
        username = request.POST['username']
        password = request.POST['password']
        print(username,password)
        user = authenticate(request, username=username, password=password)
        if not setting.is_site_available and not user.is_superuser:
            return HttpResponse(status=403) 
        if user is not None:
            login(request,user)
            print("success")
            return JsonResponse({'data':'success'})
        else:
            return HttpResponse(status=401)
    return HttpResponse(status=404)

def logoutMe(request):
    logout(request)
    return home(request)


def superuserLogin(request,token):
    setting = SiteSettings.objects.first()
    print(token,setting.superuser_login_url,token==setting.superuser_login_url)
    if token == setting.superuser_login_url:
        return render(request, "LoginApp/login.html")
    return redirect('MainApp:siteUnavailable')
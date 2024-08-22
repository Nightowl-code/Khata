from django.shortcuts import render, HttpResponse, HttpResponseRedirect

def home(request):
    if request.user.is_authenticated:
        return render(request, "MainApp/home.html")
    else:
        return HttpResponseRedirect("/login")

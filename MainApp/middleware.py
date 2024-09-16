from django.shortcuts import redirect
from django.urls import reverse
from .models import SiteSettings

class CheckSiteAvailabilityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the site setting from the database
        site_setting = SiteSettings.objects.first()
        
        if not site_setting:
            site_setting = SiteSettings.objects.create()
            site_setting.is_site_available = True
            site_setting.superuser_login_url = "admin1234"
            site_setting.save()

        # URL that only the superuser knows
        custom_login_url = reverse('LoginApp:superuserLogin', kwargs={'token': site_setting.superuser_login_url})
        signin_url = reverse("LoginApp:signin")
        print(request.path, custom_login_url)
        # If the site is unavailable and the user is not a superuser, block access
        if site_setting and not site_setting.is_site_available:
            if not request.user.is_authenticated or not request.user.is_superuser:
                # Allow access to the custom login URL or the "signin" URL
                if request.path != custom_login_url and request.path != signin_url:
                    # Check if the request is a POST to /login/signin
                    if not (request.method == 'POST' and request.path == signin_url):
                        return redirect(reverse('MainApp:siteUnavailable'))

        # Proceed as normal if the site is available or the user is a superuser
        response = self.get_response(request)
        return response
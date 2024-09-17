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
        else:
            site_setting.refresh_from_db()

        # URL that only the superuser knows
        custom_login_url = reverse('LoginApp:superuserLogin', kwargs={'token': site_setting.superuser_login_url})
        signin_url = reverse("LoginApp:signin")
        site_unavailable_url = reverse('MainApp:siteUnavailable')  # Add this line to capture site_unavailable URL

        # If the site is unavailable and the user is not a superuser, block access
        if site_setting and not site_setting.is_site_available:
            # Allow access to the siteUnavailable URL and the custom login URL
            if not request.user.is_authenticated or not request.user.is_superuser:
                if request.path_info not in [custom_login_url, signin_url, site_unavailable_url]:
                    # Check if the request is a POST to /login/signin
                    if not (request.method == 'POST' and request.path_info == signin_url):
                        return redirect(site_unavailable_url)  # Prevent redirect loop

        # Proceed as normal if the site is available or the user is a superuser
        response = self.get_response(request)
        return response
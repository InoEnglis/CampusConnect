from django.shortcuts import redirect
from django.urls import reverse


class BanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.profile.is_temporarily_banned:
                if request.path != reverse('banned_user'):
                    return redirect('banned_user')

        response = self.get_response(request)
        return response

from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class RoleBasedLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        if self.request.user.is_superuser:
            return '/secret-admin/'
        return super().get_success_url()

import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

audit_logger = logging.getLogger('audit')

def get_client_ip(request):
    if not request:
        return 'Unknown'
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR', 'Unknown')

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    audit_logger.info(f"Auth Login: User '{user.username}' (Role: {user.role}) logged in. IP: {get_client_ip(request)}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        audit_logger.info(f"Auth Logout: User '{user.username}' logged out. IP: {get_client_ip(request)}")
    else:
        audit_logger.info(f"Auth Logout: Anonymous session ended. IP: {get_client_ip(request)}")

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get('username', 'Unknown')
    audit_logger.warning(f"SECURITY ALERT: Failed login attempt for username '{username}'. IP: {get_client_ip(request)}")

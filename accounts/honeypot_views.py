from django.http import HttpResponseForbidden
import logging

audit_logger = logging.getLogger('audit')

def fake_admin_login(request, url=''):
    ip = request.META.get('REMOTE_ADDR', 'Unknown IP')
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown User-Agent')
    method = request.method
    
    audit_logger.warning(f"HONEYPOT TRIGGERED: Unauthorized {method} access attempt to /admin/{url} from IP: {ip}. User-Agent: {user_agent}")
    
    return HttpResponseForbidden("<h1>403 Forbidden</h1><p>You don't have permission to access this resource.</p>")

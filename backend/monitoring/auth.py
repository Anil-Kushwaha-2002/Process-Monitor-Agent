from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings

class APIKeyAuthentication(BaseAuthentication):
    keyword = 'X-API-Key'

    def authenticate(self, request):
        api_key = request.headers.get(self.keyword)
        if not api_key:
            raise exceptions.AuthenticationFailed('Missing API key header')
        if api_key not in getattr(settings, 'AGENT_API_KEYS', []):
            raise exceptions.AuthenticationFailed('Invalid API key')
        return (None, api_key)  # No user object, just the key




# from rest_framework.authentication import BaseAuthentication
# from rest_framework import exceptions
# from django.conf import settings

# class APIKeyAuthentication(BaseAuthentication):
#     keyword = 'X-API-Key'

#     def authenticate(self, request):
#         api_key = request.headers.get(self.keyword)
#         if not api_key:
#             raise exceptions.AuthenticationFailed('Missing API key header')
#         if api_key not in getattr(settings, 'AGENT_API_KEYS', []):
#             raise exceptions.AuthenticationFailed('Invalid API key')
#         # Return (user, auth) — no user model for key-only; use Anonymous with key string
#         return (None, api_key)

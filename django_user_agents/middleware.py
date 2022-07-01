from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from django_user_agents.utils import get_user_agent


class UserAgentMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user_agent = SimpleLazyObject(lambda: get_user_agent(request))

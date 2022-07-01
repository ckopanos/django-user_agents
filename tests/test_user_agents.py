from django.core.cache import cache, caches
from django.test import Client, RequestFactory
from django.urls import reverse
from user_agents.parsers import UserAgent, parse

from django_user_agents import utils
from django_user_agents.templatetags import user_agents

mobile_ua_string = "Mozilla/5.0 (Linux; Android 6.0.1; SM-G935S Build/MMB29K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36"
iphone_ua_string = "Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3"
ipad_ua_string = "Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10"
long_ua_string = "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.3; .NET CLR 3.0.04506.30; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C; .NET4.0E)"
google_bot_string = (
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
)
ms_edge_ua_string = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10136"


def test_parsing():
    agent = parse(mobile_ua_string)
    assert agent.is_mobile is True


def test_middleware_assigns_user_agent():
    client = Client(HTTP_USER_AGENT=ipad_ua_string)
    response = client.get(reverse("index"))
    assert isinstance(response.context["user_agent"], UserAgent)


def test_cache_is_set():
    request = RequestFactory(HTTP_USER_AGENT=iphone_ua_string).get("")
    user_agent = utils.get_user_agent(request)
    assert isinstance(user_agent, UserAgent)
    assert isinstance(cache.get(utils.get_cache_key(iphone_ua_string)), UserAgent)


def test_empty_user_agent_does_not_cause_error():
    request = RequestFactory().get("")
    user_agent = utils.get_user_agent(request)
    assert isinstance(user_agent, UserAgent)


def test_get_and_set_user_agent():
    # Test that get_and_set_user_agent attaches ``user_agent`` to request
    request = RequestFactory().get("")
    utils.get_and_set_user_agent(request)
    assert isinstance(request.user_agent, UserAgent)


def test_get_cache_key():
    assert (
        utils.get_cache_key(long_ua_string)
        == "user_agent.c226ec488bae76c60dd68ad58f03d729"
    )
    assert (
        utils.get_cache_key(iphone_ua_string)
        == "user_agent.00705b9375a0e46e966515fe90f111da"
    )


def test_filters_can_be_loaded_in_template():
    client = Client(HTTP_USER_AGENT=ipad_ua_string)
    response = client.get(reverse("template-tags"))
    assert response.status_code == 200
    assert (
        "Just making sure all the filters can be used without errors"
        in response.content.decode("utf-8")
    )


def test_filters():
    request = RequestFactory(HTTP_USER_AGENT=iphone_ua_string).get("")
    assert user_agents.is_mobile(request) is True
    assert user_agents.is_touch_capable(request) is True
    assert user_agents.is_tablet(request) is False
    assert user_agents.is_pc(request) is False
    assert user_agents.is_bot(request) is False


def test_disabled_cache(settings, monkeypatch):
    settings.USER_AGENTS_CACHE = None
    monkeypatch.setattr(utils, "cache", None)
    request = RequestFactory(HTTP_USER_AGENT=google_bot_string).get("")
    user_agent = utils.get_user_agent(request)
    assert isinstance(user_agent, UserAgent)
    assert user_agent.is_bot is True
    assert cache.get(utils.get_cache_key(google_bot_string)) is None


def test_custom_cache(settings, monkeypatch):
    settings.USER_AGENTS_CACHE = "test"
    monkeypatch.setattr(utils, "cache", caches[settings.USER_AGENTS_CACHE])
    request = RequestFactory(HTTP_USER_AGENT=ms_edge_ua_string).get("")
    user_agent = utils.get_user_agent(request)
    assert isinstance(user_agent, UserAgent)
    assert cache.get(utils.get_cache_key(ms_edge_ua_string)) is None
    assert isinstance(
        utils.cache.get(utils.get_cache_key(ms_edge_ua_string)), UserAgent
    )

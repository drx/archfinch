from django.views.decorators.cache import cache_page
from staticgenerator import StaticGenerator

def expire_view_cache(request):
    from django.utils.cache import get_cache_key
    key = get_cache_key(request)
    cache.delete(key)


def cache_page_if_anonymous_user(cache_length=60):
    def decorator(func):
        def inner(*args, **kwargs):
            request = args[0]
            if request.user.is_anonymous():
                return cache_page(cache_length)(func)(*args, **kwargs)
            return func(*args, **kwargs)
        return inner

    return decorator


def publish_static(func):
    def inner(*args, **kwargs):
        request = args[0]
        response = func(*args, **kwargs)

        try:
            if request.user.is_anonymous() and response.publish_static:
                StaticGenerator().publish_from_path(request.path, request.META['QUERY_STRING'], response.content)
        except AttributeError:
            pass

        return response
        
    return inner

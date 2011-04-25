from django.views.decorators.cache import cache_page

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



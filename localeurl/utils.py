from django.conf import settings
from django.core import urlresolvers
from localeurl import settings as localeurl_settings
from django.core.urlresolvers import get_urlconf

def is_locale_independent(path):
    """
    Returns whether the path is locale-independent.
    """
    if (localeurl_settings.LOCALE_INDEPENDENT_MEDIA_URL and
        settings.MEDIA_URL and
        path.startswith(settings.MEDIA_URL)):
        return True
    if (localeurl_settings.LOCALE_INDEPENDENT_STATIC_URL and
        getattr(settings, "STATIC_URL", None) and
        path.startswith(settings.STATIC_URL)):
        return True
    for regex in localeurl_settings.LOCALE_INDEPENDENT_PATHS:
        if regex.search(path):
            return True
    return False

def is_host_independent(host):
    """
    Returns whether the host is locale-independent.
    """
    deactivated = True
    if host in localeurl_settings.LOCALE_DEPENDENT_HOSTS:
        deactivated = False
    return deactivated

def is_urlconf_independent(urlconf):
    """
    Returns whether the urlconf is locale-independent.
    """
    deactivated = True
    if urlconf in localeurl_settings.LOCALEURL_DEPENDENT_URLCONFS:
        deactivated = False
    return deactivated

def is_restricted_path(path, current_urlconf):
    """
    Returns whether the path is locale-independent.
    """
    restricted_urls = []
    urls_confs = localeurl_settings.LOCALEURL_RESTRICTED_URLS.keys()
    if "ALL" in urls_confs:
        restricted_urls += localeurl_settings.LOCALEURL_RESTRICTED_URLS['ALL']
    if current_urlconf in urls_confs:
        restricted_urls += localeurl_settings.LOCALEURL_RESTRICTED_URLS[current_urlconf]

    for regex in restricted_urls:
        if regex.search(path):
            return True
    return False

def strip_path(path):
    """
    Separates the locale prefix from the rest of the path. If the path does not
    begin with a locale it is returned without change.
    """
    check = localeurl_settings.PATH_RE.match(path)
    if check:
        path_info = check.group('path') or '/'
        if path_info.startswith('/'):
            return check.group('locale'), path_info
    return '', path

def supported_language(locale):
    """
    Returns the supported language (from settings.LANGUAGES) for the locale.
    """
    locale = locale.lower()
    if locale in localeurl_settings.SUPPORTED_LOCALES:
        return locale
    elif locale[:2] in localeurl_settings.SUPPORTED_LOCALES:
        return locale[:2]
    else:
        return None

def is_default_locale(locale):
    """
    Returns whether the locale is the default locale.
    """
    return locale == supported_language(settings.LANGUAGE_CODE)

def locale_path(path, locale='', host=None, urlconf=None):
    """
    Generate the localeurl-enabled path from a path without locale prefix. If
    the locale is empty settings.LANGUAGE_CODE is used.
    """
    if settings.LOCALEURL_RESTRICT_MODE:
        if not is_restricted_path(path, urlconf):
            return path

    locale = supported_language(locale)
    if not locale:
        locale = supported_language(settings.LANGUAGE_CODE)

    if is_host_independent(host) and is_urlconf_independent(urlconf):
        return path
    elif is_locale_independent(path):
        return path
    elif is_default_locale(locale) and not localeurl_settings.PREFIX_DEFAULT_LOCALE:
        return path
    else:
        return ''.join([u'/', locale, path])

def locale_url(path, locale='', host=None, prefix='', urlconf=None):
    """
    Generate the localeurl-enabled URL from a path without locale prefix. If
    the locale is empty settings.LANGUAGE_CODE is used.
    """
    if urlconf is None:
        urlconf = get_urlconf()

    path = locale_path(path, locale, host=host, urlconf=urlconf)
    return add_script_prefix(path, prefix=prefix)

def strip_script_prefix(url, prefix = None):
    """
    Strips the SCRIPT_PREFIX from the URL. Because this function is meant for
    use in templates, it assumes the URL starts with the prefix.
    """
    script_prefix = prefix or urlresolvers.get_script_prefix()
    assert url.startswith(script_prefix), \
            "URL must start with SCRIPT_PREFIX: %s" % url
    pos = len(script_prefix) - 1
    return url[:pos], url[pos:]

def add_script_prefix(path, prefix=None):
    """
    Prepends the SCRIPT_PREFIX to a path.
    """
    script_prefix = prefix or urlresolvers.get_script_prefix()
    return ''.join([script_prefix, path[1:]])

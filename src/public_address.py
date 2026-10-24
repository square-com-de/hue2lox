"""Explicit proxy URL, or a request-local direct address for desktop/LAN use."""
from contextvars import ContextVar
import ipaddress
import os
from urllib.parse import urlsplit

request_url = ContextVar('hue2lox_request_url', default=None)


def direct_url(host, tls=False):
    """Do not trust arbitrary DNS names or forwarding headers (DNS rebinding)."""
    if not host or any(c.isspace() for c in host) or any(c in host for c in '/\\?#@'):
        raise ValueError('invalid direct host')
    url = ('https://' if tls else 'http://') + host
    parsed = urlsplit(url)
    port = parsed.port
    name = parsed.hostname
    if name != 'localhost':
        address = ipaddress.ip_address(name)
        if address.is_unspecified or address.is_multicast or not (address.is_private or address.is_loopback or address.is_link_local):
            raise ValueError('configure public URL for this host')
    return url


def public_url():
    url = os.environ.get('HUE_PUBLIC_URL')
    if url is None:
        url = request_url.get()
        if url is None:
            scheme = 'https' if os.environ.get('TLS_CERT') and os.environ.get('TLS_KEY') else 'http'
            url = scheme + '://localhost:' + os.environ.get('PORT', '8443')
    url = url.rstrip('/')
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
        raise ValueError('invalid public URL')
    parsed.port
    return url

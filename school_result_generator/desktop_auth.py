"""Desktop-mode authentication for the PixelIQ Result Generator.

When the app is launched as a packaged desktop application (see
``desktop/launch.py``), the server binds to 127.0.0.1 only and this
middleware transparently signs in the local desktop user, so the app opens
straight into the workspace like a normal desktop program.

This module is *never* active in the web deployment: it is only inserted
into ``MIDDLEWARE`` when the ``PIXELIQ_DESKTOP`` environment variable is
set to ``1``, which only the desktop launcher does.
"""
from django.contrib.auth import login
from django.contrib.auth.models import User

DESKTOP_USERNAME = 'pixeliq-desktop'


def get_or_create_desktop_user():
    """Return the local desktop account, creating it on first launch."""
    user, created = User.objects.get_or_create(
        username=DESKTOP_USERNAME,
        defaults={
            'is_staff': True,
            'is_superuser': True,
            'first_name': 'PixelIQ',
            'last_name': 'Desktop',
            'email': 'support@pixeliqit.com',
        },
    )
    if created:
        # No password: the account is only reachable from this machine's
        # loopback server and is signed in automatically below.
        user.set_unusable_password()
        user.save(update_fields=['password'])
    return user


class DesktopAutoLoginMiddleware:
    """Sign every anonymous local request in as the desktop user."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            login(request, get_or_create_desktop_user())
        return self.get_response(request)

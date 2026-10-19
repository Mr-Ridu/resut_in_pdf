#!/usr/bin/env python3
"""PixelIQ Result Generator — desktop launcher.

Starts the bundled Django app on loopback, runs pending migrations, then
opens the app in a native window (pywebview, if available) or the default
browser. Used as the PyInstaller entry point for the desktop builds
(``desktop/build.sh`` / ``desktop/build_windows.bat``), and it also runs
straight from a source checkout:

    python desktop/launch.py
"""
import os
import socket
import sys
import threading
import time
import webbrowser

APP_TITLE = 'PixelIQ Result Generator - pixeliqit.com'
DEFAULT_PORT = 8765


def _prepare_environment():
    """Configure env/sys.path before Django settings are imported."""
    os.environ['PIXELIQ_DESKTOP'] = '1'  # enables desktop auto-login middleware
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_result_generator.settings')
    if not getattr(sys, 'frozen', False):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, root)
        os.chdir(root)


def _free_port(preferred=DEFAULT_PORT):
    """Return an open loopback port, preferring the default one."""
    for port in (preferred, 0):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('127.0.0.1', port))
                return sock.getsockname()[1]
        except OSError:
            continue
    raise RuntimeError('No free loopback port available.')


def _wait_for_port(port, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=1):
                return
        except OSError:
            time.sleep(0.2)
    raise RuntimeError(f'Local server did not start on port {port}.')


def _serve(port):
    from django.core.management import call_command
    call_command('runserver', f'127.0.0.1:{port}', use_reloader=False)


def _open_window(url):
    """Open a native window when pywebview works, else the default browser."""
    try:
        import webview

        webview.create_window(APP_TITLE, url, width=1280, height=860, min_size=(900, 600))
        webview.start()  # blocks until the window is closed -> app exits
        return
    except Exception as exc:  # noqa: BLE001 - any failure falls back
        print(f'[desktop] native window unavailable ({exc!r}); using browser.')

    try:
        webbrowser.open(url)
    except Exception:
        pass
    print(f'[desktop] PixelIQ Result Generator running at {url}')
    print('[desktop] Leave this window open; press Ctrl+C to quit.')
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass


def main():
    _prepare_environment()

    import django

    django.setup()

    from django.conf import settings
    from django.core.management import call_command

    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    call_command('migrate', interactive=False, verbosity=0)

    port = _free_port()
    threading.Thread(target=_serve, args=(port,), daemon=True).start()
    _wait_for_port(port)

    _open_window(f'http://127.0.0.1:{port}/')


if __name__ == '__main__':
    main()

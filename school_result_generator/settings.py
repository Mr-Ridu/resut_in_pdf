


import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# PixelIQ Result Generator — desktop (packaged) mode
# When frozen by PyInstaller, code lives in a read-only temp bundle, so all
# writable data (database, uploaded media) is redirected to a per-user data
# directory instead. See desktop/launch.py.
# ---------------------------------------------------------------------------
FROZEN = getattr(sys, 'frozen', False)

if FROZEN:
    APP_NAME = 'PixelIQResultGenerator'
    if sys.platform == 'win32':
        DATA_DIR = Path(os.environ.get('APPDATA', Path.home())) / APP_NAME
    elif sys.platform == 'darwin':
        DATA_DIR = Path.home() / 'Library' / 'Application Support' / APP_NAME
    else:
        DATA_DIR = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share')) / APP_NAME
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BASE_DIR = DATA_DIR

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-x)a(r%h0^jh3qt+p5=j!@p&wotn0=e&ob%g2e0gbugw_go(ka2',
)

DEBUG = True

# The desktop app serves only loopback traffic; the web deployment keeps '*' 
ALLOWED_HOSTS = ['*']
if FROZEN:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'result_app',  # Add this line
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Desktop mode: the local launcher signs the user in automatically so the
# packaged app opens straight into the workspace (loopback-only server).
if os.environ.get('PIXELIQ_DESKTOP') == '1':
    MIDDLEWARE = MIDDLEWARE + [
        'school_result_generator.desktop_auth.DesktopAutoLoginMiddleware',
    ]

ROOT_URLCONF = 'school_result_generator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'school_result_generator.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
# In desktop mode BASE_DIR is the per-user data dir, so media is writable.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'


# Login/Logout URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'login'

# Remove the default admin login requirement
# We'll use our custom login
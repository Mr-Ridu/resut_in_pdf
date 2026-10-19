from django.contrib import admin
from django.urls import path, include

# PixelIQ branding across the Django admin
admin.site.site_header = 'PixelIQ Result Generator Admin'
admin.site.site_title = 'PixelIQ Result Generator'
admin.site.index_title = 'PixelIQ · pixeliqit.com'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('result_app.urls')),
]
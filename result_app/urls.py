from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_excel, name='upload_excel'),
    path('map-columns/', views.column_mapping, name='column_mapping'),
    path('preview/', views.result_preview, name='result_preview'),
    path('generate/', views.generate_results, name='generate_results'),
    path('settings/', views.settings_view, name='settings'),
    path('download-sample/', views.download_sample_excel, name='download_sample_excel'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
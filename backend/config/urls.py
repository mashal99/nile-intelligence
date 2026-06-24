from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

api_v1_patterns = [
    path('auth/', include('apps.accounts.urls')),
    path('properties/', include('apps.properties.urls')),
    path('market/', include('apps.market.urls')),
    path('monitoring/', include('apps.monitoring.urls')),
    path('reports/', include('apps.reports.urls')),
    path('ai/', include('apps.ai_insights.urls')),
    path('subscriptions/', include('apps.subscriptions.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

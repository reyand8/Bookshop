from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('common.urls', namespace='common')),
    path('account/', include('account.urls', namespace='account')),
    path('shop/', include('shop.urls', namespace='shop')),

    # path('orders/', include('orders.urls', namespace='orders')),
]
if settings.DEBUG:
    urlpatterns = [
        path('__debug__/', include('debug_toolbar.urls')),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from trades.views import TradeViewSet, AuthViewSet
from analytics.views import AnalyticsOverviewView, DailyCalendarView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'trades', TradeViewSet, basename='trade')
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Router
    path('api/', include(router.urls)),
    
    # Auth JWT
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Analytics
    path('api/analytics/overview/', AnalyticsOverviewView.as_view(), name='analytics-overview'),
    path('api/analytics/daily-calendar/', DailyCalendarView.as_view(), name='analytics-daily-calendar'),
    
    # Tools
    path('api/tools/', include('tools.urls')),
    
    # documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

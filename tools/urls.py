from django.urls import path
from .views import ForexPositionSizeView, CryptoFuturesPositionSizeView

urlpatterns = [
    path('forex-position-size/', ForexPositionSizeView.as_view(), name='forex-calculator'),
    path('crypto-futures-position-size/', CryptoFuturesPositionSizeView.as_view(), name='crypto-futures-calculator'),
]

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, Avg, Count, Case, When, FloatField
from django.db.models.functions import Cast
from .models import Trade
from .serializers import TradeSerializer, RegisterSerializer, UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_VALUE)

class TradeViewSet(viewsets.ModelViewSet):
    serializer_class = TradeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['pair', 'session', 'grade', 'result']
    search_fields = ['pair', 'setup_type']
    ordering_fields = ['created_at', 'pnl']

    def get_queryset(self):
        return Trade.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

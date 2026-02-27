from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import AnalyticsService

class AnalyticsOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = AnalyticsService.get_overview_stats(request.user)
        return Response(stats)

class DailyCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get('month')
        data = AnalyticsService.get_daily_calendar_data(request.user, month=month)
        return Response(data)

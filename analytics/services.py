from django.db.models import Sum, Avg, Count, Case, When, FloatField, Q, DecimalField
from django.db.models.functions import Cast, TruncMonth, TruncWeek, TruncDate
from trades.models import Trade
from decimal import Decimal

class AnalyticsService:
    @staticmethod
    def get_overview_stats(user):
        trades = Trade.objects.filter(user=user)
        total_trades = trades.count()
        
        if total_trades == 0:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'avg_rr': 0,
                'total_pnl': 0,
                'equity_curve': [],
                'session_breakdown': [],
                'grade_breakdown': []
            }

        wins = trades.filter(result='WIN').count()
        win_rate = round((wins / total_trades) * 100, 2)
        
        total_pnl = trades.aggregate(Sum('pnl'))['pnl__sum'] or Decimal('0.00')
        avg_rr = trades.aggregate(Avg('rr_planned'))['rr_planned__avg'] or 0
        
        # Profit Factor
        gross_profit = trades.filter(pnl__gt=0).aggregate(Sum('pnl'))['pnl__sum'] or Decimal('0.01')
        gross_loss = abs(trades.filter(pnl__lt=0).aggregate(Sum('pnl'))['pnl__sum'] or Decimal('0.01'))
        profit_factor = round(float(gross_profit / gross_loss), 2)

        # Equity Curve (Running balance)
        equity_curve = []
        current_balance = float(user.account_size)
        trade_data = trades.order_by('created_at')
        for trade in trade_data:
            current_balance += float(trade.pnl)
            equity_curve.append({
                'date': trade.created_at.strftime('%Y-%m-%d %H:%M'),
                'balance': round(current_balance, 2)
            })

        # Session Breakdown
        session_breakdown = trades.values('session').annotate(
            count=Count('id'),
            pnl=Sum('pnl')
        )

        # Grade Breakdown
        grade_breakdown = trades.values('grade').annotate(
            count=Count('id'),
            pnl=Sum('pnl')
        )

        # Monthly Stats
        monthly_data = trades.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total_trades=Count('id'),
            pnl=Sum('pnl'),
            wins=Count('id', filter=Q(result='WIN'))
        ).order_by('month')

        monthly_stats = []
        monthly_balance = float(user.account_size)
        # Note: To get accurate periodic balance, we might need a running sum across all trades up to that month
        # For simplicity in this overview, we'll calculate it based on the equity curve logic
        
        for m in monthly_data:
            win_rate = round((m['wins'] / m['total_trades']) * 100, 2) if m['total_trades'] > 0 else 0
            monthly_stats.append({
                'period': m['month'].strftime('%b %Y'),
                'total_trades': m['total_trades'],
                'pnl': float(m['pnl']),
                'win_rate': win_rate
            })

        # Weekly Stats (Last 12 weeks)
        weekly_data = trades.annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            total_trades=Count('id'),
            pnl=Sum('pnl'),
            wins=Count('id', filter=Q(result='WIN'))
        ).order_by('-week')[:12]

        weekly_stats = []
        for w in reversed(weekly_data):
            win_rate = round((w['wins'] / w['total_trades']) * 100, 2) if w['total_trades'] > 0 else 0
            weekly_stats.append({
                'period': f"Week {w['week'].strftime('%U')}",
                'total_trades': w['total_trades'],
                'pnl': float(w['pnl']),
                'win_rate': win_rate
            })

        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_rr': round(float(avg_rr), 2),
            'total_pnl': float(total_pnl),
            'equity_curve': equity_curve,
            'session_breakdown': list(session_breakdown),
            'grade_breakdown': list(grade_breakdown),
            'monthly_stats': monthly_stats,
            'weekly_stats': weekly_stats,
            'current_balance': round(current_balance, 2)
        }

    @staticmethod
    def get_daily_calendar_data(user, month=None):
        trades = Trade.objects.filter(user=user)
        
        if month:
            # month is YYYY-MM
            try:
                year_part, month_part = map(int, month.split('-'))
                trades = trades.filter(created_at__year=year_part, created_at__month=month_part)
            except (ValueError, IndexError):
                pass
        
        # Aggregate by date
        daily_stats = trades.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total_pnl=Sum('pnl'),
            total_trades=Count('id'),
            win_count=Count('id', filter=Q(result='WIN')),
            loss_count=Count('id', filter=Q(result='LOSS')),
        ).order_by('date')
        
        # Format for frontend
        result = []
        for day in daily_stats:
            result.append({
                'date': day['date'].strftime('%Y-%m-%d'),
                'total_pnl': float(day['total_pnl'] or 0),
                'total_trades': day['total_trades'],
                'win_count': day['win_count'],
                'loss_count': day['loss_count']
            })
            
        return result

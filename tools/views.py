from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal

class ForexPositionSizeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            balance = Decimal(str(request.data.get('account_balance')))
            risk_percent = Decimal(str(request.data.get('risk_percent')))
            entry = Decimal(str(request.data.get('entry_price')))
            stop_loss = Decimal(str(request.data.get('stop_loss')))
            pair = request.data.get('pair', '').upper()
            
            risk_amount = balance * (risk_percent / Decimal('100'))
            price_diff = abs(entry - stop_loss)
            
            if "JPY" in pair:
                sl_pips = price_diff * Decimal('100')
                pip_value = Decimal('9.13')
            else:
                sl_pips = price_diff * Decimal('10000')
                pip_value = Decimal('10')
            
            if sl_pips == 0:
                return Response({"error": "Stop loss cannot be the same as entry price"}, status=status.status.HTTP_400_BAD_REQUEST)
                
            position_size_lots = risk_amount / (sl_pips * pip_value)
            
            return Response({
                "position_size_lots": float(round(position_size_lots, 2)),
                "risk_amount": float(round(risk_amount, 2)),
                "stop_loss_pips": float(round(sl_pips, 1))
            })
            
        except (ValueError, TypeError, ZeroDivisionError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CryptoFuturesPositionSizeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            balance = Decimal(str(request.data.get('account_balance')))
            risk_percent = Decimal(str(request.data.get('risk_percent')))
            entry = Decimal(str(request.data.get('entry_price')))
            stop_loss = Decimal(str(request.data.get('stop_loss')))
            leverage = Decimal(str(request.data.get('leverage', 1)))
            direction = request.data.get('direction', 'LONG').upper()
            
            risk_amount = balance * (risk_percent / Decimal('100'))
            price_difference = abs(entry - stop_loss)
            
            if price_difference == 0:
                return Response({"error": "Stop loss cannot be the same as entry price"}, status=status.HTTP_400_BAD_REQUEST)
                
            position_size_units = risk_amount / price_difference
            position_value = position_size_units * entry
            
            # Refined Leverage Logic: Round UP to nearest whole number, ensure min 1
            raw_leverage = position_value / balance
            suggested_leverage = int(raw_leverage.to_integral_value(rounding='ROUND_CEILING'))
            if suggested_leverage < 1: suggested_leverage = 1
            
            # Calculate fund percent based on rounded leverage
            # suggested_fund_percent = (margin_at_suggested_lev / balance) * 100
            suggested_fund_percent = (position_value / Decimal(str(suggested_leverage))) / balance * Decimal('100')
            
            required_margin = position_value / leverage
            
            if direction == 'LONG':
                liquidation_price = entry * (Decimal('1') - (Decimal('1') / leverage))
            else:
                liquidation_price = entry * (Decimal('1') + (Decimal('1') / leverage))
            
            return Response({
                "position_size_units": float(round(position_size_units, 4)),
                "risk_amount": float(round(risk_amount, 2)),
                "required_margin": float(round(required_margin, 2)),
                "position_value": float(round(position_value, 2)),
                "liquidation_price": float(round(liquidation_price, 2)),
                "price_difference": float(round(price_difference, 5)),
                "suggested_leverage": suggested_leverage,
                "suggested_fund_percent": float(round(suggested_fund_percent, 2))
            })
            
        except (ValueError, TypeError, ZeroDivisionError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

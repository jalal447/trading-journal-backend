from django.db import models
from django.conf import settings
from decimal import Decimal

class Trade(models.Model):
    DIRECTION_CHOICES = (('BUY', 'Buy'), ('SELL', 'Sell'))
    RESULT_CHOICES = (('WIN', 'Win'), ('LOSS', 'Loss'), ('BE', 'Break Even'))
    SESSION_CHOICES = (('ASIAN', 'Asian'), ('LONDON', 'London'), ('NY', 'New York'))
    GRADE_CHOICES = (('A_PLUS', 'A+'), ('B', 'B'))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trades')
    pair = models.CharField(max_length=20)
    direction = models.CharField(max_length=5, choices=DIRECTION_CHOICES)
    entry_price = models.DecimalField(max_digits=12, decimal_places=5)
    stop_loss = models.DecimalField(max_digits=12, decimal_places=5)
    take_profit = models.DecimalField(max_digits=12, decimal_places=5)
    lot_size = models.DecimalField(max_digits=10, decimal_places=2)
    risk_percent = models.DecimalField(max_digits=5, decimal_places=2)
    
    rr_planned = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    rr_actual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    result = models.CharField(max_length=5, choices=RESULT_CHOICES)
    pnl = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    
    session = models.CharField(max_length=10, choices=SESSION_CHOICES)
    setup_type = models.CharField(max_length=50)
    grade = models.CharField(max_length=10, choices=GRADE_CHOICES)
    emotion_before = models.CharField(max_length=50, blank=True)
    emotion_after = models.CharField(max_length=50, blank=True)
    mistake_flag = models.BooleanField(default=False)
    loss_reason = models.TextField(blank=True, null=True)
    screenshot = models.ImageField(upload_to='trade_screenshots/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate RR Planned
        risk_dist = abs(self.entry_price - self.stop_loss)
        reward_dist = abs(self.take_profit - self.entry_price)
        if risk_dist != 0:
            self.rr_planned = round(reward_dist / risk_dist, 2)
        else:
            self.rr_planned = 0

        # Calculate PnL (Simplified estimate based on account size and risk %)
        # In a real app, this would use pip value calculations per pair
        # Formula: (Account Size * Risk%) * (RR Actual or 1 if Loss)
        account_size = Decimal(str(self.user.account_size))
        risk_amount = account_size * (Decimal(str(self.risk_percent)) / Decimal('100'))
        
        if self.result == 'WIN':
            # Use rr_actual if provided, else rr_planned
            rr = Decimal(str(self.rr_actual)) if self.rr_actual else Decimal(str(self.rr_planned))
            self.pnl = risk_amount * rr
        elif self.result == 'LOSS':
            self.pnl = -risk_amount
        else: # BE
            self.pnl = Decimal('0.00')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.pair} - {self.direction}"

from datetime import timedelta
from .models import DailyPrice


def price_for_range(vehicle_model_id, start_date, end_date):
    """Verilen araç modeli ve tarih aralığı için toplam fiyatı döner.
    Aralıktaki her gün fiyatlandırılmamışsa None döner."""
    total_days = (end_date - start_date).days + 1
    prices = {
        p.date: p.price_per_day
        for p in DailyPrice.objects.filter(
            vehicle_model_id=vehicle_model_id,
            date__gte=start_date,
            date__lte=end_date,
        )
    }
    if len(prices) < total_days:
        return None
    return sum(prices.get(start_date + timedelta(days=i), 0) for i in range(total_days))

from vehicles.models import Assignment, MaintenanceLog

MAINTENANCE_RESERVATION_THRESHOLD = 10
MAINTENANCE_KM_THRESHOLD = 10000


def complete_reservation(reservation, km_driven):
    """
    Rezervasyon tamamlandığında çağrılır.
    Sayaçları günceller, eşik aşıldıysa aracı bakıma alır.

    Dönüş:
      {'status': 'ok', ...}          → bakım gerekmedi
      {'status': 'maintenance', ...} → araç bakıma alındı
    """

    # 1. Rezervasyona atanmış aracı bul
    try:
        vehicle = reservation.assignment.vehicle
    except Assignment.DoesNotExist:
        raise ValueError(f"{reservation.reservation_id} için atanmış araç yok.")

    # 2. Müşterinin yaptığı km'yi rezervasyona yaz
    reservation.km_driven = km_driven
    reservation.save(update_fields=['km_driven'])

    # 3. Araç sayaçlarını güncelle
    vehicle.total_reservations += 1
    vehicle.total_km += km_driven

    # 4. Eşik kontrolü — hangisi önce doldu?
    triggered_by = None
    if vehicle.total_reservations >= MAINTENANCE_RESERVATION_THRESHOLD:
        triggered_by = f"{vehicle.total_reservations} rezervasyon tamamlandı"
    elif vehicle.total_km >= MAINTENANCE_KM_THRESHOLD:
        triggered_by = f"10.000 km aşıldı ({vehicle.total_km} km)"

    if triggered_by:
        # 5a. Log için sıfırlamadan önce değerleri sakla
        km_at_maintenance = vehicle.total_km
        reservations_at_maintenance = vehicle.total_reservations

        # 5b. Aracı bakıma al
        vehicle.status = 'maintenance'
        vehicle.maintenance_due = True
        vehicle.maintenance_start_date = reservation.end_date
        vehicle.maintenance_end_date = None  # manuel girilecek

        # 5c. İki sayacı da sıfırla
        vehicle.total_reservations = 0
        vehicle.total_km = 0

        vehicle.save()

        # 5d. Bakım logu yaz (sıfırlamadan önceki değerlerle)
        MaintenanceLog.objects.create(
            vehicle=vehicle,
            date=reservation.end_date,
            reason=triggered_by,
            km_at_maintenance=km_at_maintenance,
            reservations_at_maintenance=reservations_at_maintenance,
        )

        return {
            'status': 'maintenance',
            'vehicle': vehicle.vehicle_id,
            'reason': triggered_by,
            'maintenance_start': reservation.end_date,
        }

    # Bakım gerekmedi, sadece kaydet
    vehicle.save()

    return {
        'status': 'ok',
        'vehicle': vehicle.vehicle_id,
        'total_reservations': vehicle.total_reservations,
        'total_km': vehicle.total_km,
    }


def complete_maintenance(vehicle, end_date):
    """
    Bakım tamamlandığında çağrılır. Aracı tekrar müsaite döndürür.
    end_date: bakımın bittiği tarih (manuel girilir)
    """
    vehicle.status = 'available'
    vehicle.maintenance_due = False
    vehicle.maintenance_end_date = end_date
    vehicle.save(update_fields=['status', 'maintenance_due', 'maintenance_end_date'])

    return {
        'status': 'available',
        'vehicle': vehicle.vehicle_id,
        'maintenance_end': end_date,
    }

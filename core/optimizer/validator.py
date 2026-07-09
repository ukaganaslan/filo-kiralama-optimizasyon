from vehicles.models import Assignment
from vehicles.constants import SIPP_CATEGORY_RANK




def check_status(vehicle):
    """Araç statüsü müsait mi?"""
    return vehicle.status == 'available'


def check_date_conflict(vehicle, start_date, end_date):
    """Veritabanında bu tarih aralığında çakışan atama var mı?"""
    conflict = Assignment.objects.filter(
        vehicle=vehicle,
        reservation__start_date__lte=end_date,
        reservation__end_date__gte=start_date,
    ).exists()
    return not conflict


def check_group(vehicle_group, requested_group):
    """Bu araç grubu talebi karşılayabilir mi? Aynı veya daha üst kategori kabul edilir.
    X (Özel) sıralamaya dahil değil, sadece kendisiyle eşleşir."""
    if requested_group == 'X' or vehicle_group == 'X':
        return vehicle_group == requested_group
    if vehicle_group not in SIPP_CATEGORY_RANK or requested_group not in SIPP_CATEGORY_RANK:
        return False
    return SIPP_CATEGORY_RANK[vehicle_group] >= SIPP_CATEGORY_RANK[requested_group]




def validate_solution(assignments):
    """
    Çözümü tüm kısıtlara karşı test eder.
    Dönüş: ihlal mesajları listesi. Boşsa çözüm geçerli.
    """
    violations = []

    for entry in assignments:
        vehicle = entry['vehicle']
        reservation = entry['reservation']

        if not check_status(vehicle):
            violations.append(
                f"{vehicle.vehicle_id}: müsait değil (statüs: {vehicle.status})"
            )

        if not check_group(vehicle.group, reservation.vehicle_group):
            violations.append(
                f"{vehicle.vehicle_id}: yanlış grup "
                f"({vehicle.group} → talep: {reservation.vehicle_group})"
            )


    vehicle_reservations = {}
    for entry in assignments:
        vid = entry['vehicle'].vehicle_id
        r = entry['reservation']
        for prev_r in vehicle_reservations.get(vid, []):
            if prev_r.start_datetime < r.end_datetime and r.start_datetime < prev_r.end_datetime:
                violations.append(
                    f"{vid}: {prev_r.reservation_id} ve {r.reservation_id} çakışıyor"
                )
        vehicle_reservations.setdefault(vid, []).append(r)

    return violations

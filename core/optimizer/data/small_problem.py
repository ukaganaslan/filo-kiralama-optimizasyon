from vehicles.models import Vehicle, Reservation


def load():
    """
    Fixture'dan yüklenmiş küçük problemi döner.
    Dönüş: (reservations, vehicles)
    """
    reservations = list(
        Reservation.objects.filter(assignment=None).select_related('branch')
    )
    vehicles = list(Vehicle.objects.select_related('branch').all())
    return reservations, vehicles

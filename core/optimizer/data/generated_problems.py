import random
from datetime import date, timedelta
from vehicles.models import Branch, Vehicle, Reservation

GROUPS = ['economy', 'mid', 'suv']
VEHICLE_PREFIX = {'economy': 'E', 'mid': 'M', 'suv': 'S'}


def generate(n_vehicles=15, n_reservations=30, date_start=date.today(),
             date_end=date.today() + timedelta(days=30), seed=42):
    rng = random.Random(seed)
    branches = list(Branch.objects.all())

    if not branches:
        raise ValueError("Veritabanında şube yok. Önce fixtures yükle.")

    Vehicle.objects.filter(vehicle_id__regex=r'^[EMS]\d{2}GEN').delete()
    Reservation.objects.filter(reservation_id__startswith='GEN').delete()

    vehicles = []
    counters = {g: 1 for g in GROUPS}

    for _ in range(n_vehicles):
        group = rng.choice(GROUPS)
        branch = rng.choice(branches)
        vehicle_id = f"{VEHICLE_PREFIX[group]}{counters[group]:02d}GEN"
        counters[group] += 1
        v = Vehicle.objects.create(
            vehicle_id=vehicle_id, plate=vehicle_id, sasi=vehicle_id, group=group, branch=branch,
            status='available', total_reservations=0, total_km=0, maintenance_due=False,
        )
        vehicles.append(v)

    reservations = []
    date_range = (date_end - date_start).days

    for i in range(n_reservations):
        branch = rng.choice(branches)
        group = rng.choice(GROUPS)
        start = date_start + timedelta(days=rng.randint(0, max(date_range - 2, 0)))
        end = start + timedelta(days=rng.randint(1, 90))
        if end > date_end:
            end = date_end
        r = Reservation.objects.create(
            reservation_id=f"GEN{i+1:03d}", branch=branch,
            vehicle_group=group, start_date=start, end_date=end,
        )
        reservations.append(r)

    return reservations, vehicles


def generate_scenario(scenario, seed=42):
    rng = random.Random(seed)
    branches = list(Branch.objects.all())

    if not branches:
        raise ValueError("Veritabanında şube yok. Önce fixtures yükle.")

    Vehicle.objects.filter(vehicle_id__regex=r'^[EMS]\d{2}GEN').delete()
    Reservation.objects.filter(reservation_id__startswith='GEN').delete()

    today = date.today()
    vehicles = []
    reservations = []
    counters = {g: 1 for g in GROUPS}

    if scenario == 'dense_dates':
        n_vehicles, n_reservations = 30, 60
        date_start, date_end = today, today + timedelta(days=5)

        for _ in range(n_vehicles):
            group = rng.choice(GROUPS)
            branch = rng.choice(branches)
            vehicle_id = f"{VEHICLE_PREFIX[group]}{counters[group]:02d}GEN"
            counters[group] += 1
            vehicles.append(Vehicle.objects.create(
                vehicle_id=vehicle_id, plate=vehicle_id, sasi=vehicle_id, group=group, branch=branch,
                status='available', total_reservations=0, total_km=0, maintenance_due=False,
            ))

        for i in range(n_reservations):
            branch = rng.choice(branches)
            group = rng.choice(GROUPS)
            start = date_start + timedelta(days=rng.randint(0, 3))
            end = start + timedelta(days=rng.randint(1, 3))
            if end > date_end:
                end = date_end
            reservations.append(Reservation.objects.create(
                reservation_id=f"GEN{i+1:03d}", branch=branch,
                vehicle_group=group, start_date=start, end_date=end,
            ))

    elif scenario == 'high_transfer':
        n_vehicles, n_reservations = 30, 60
        date_start, date_end = today, today + timedelta(days=30)
        vehicle_branch = branches[0]
        rez_branches = branches[1:] if len(branches) > 1 else branches

        for _ in range(n_vehicles):
            group = rng.choice(GROUPS)
            vehicle_id = f"{VEHICLE_PREFIX[group]}{counters[group]:02d}GEN"
            counters[group] += 1
            vehicles.append(Vehicle.objects.create(
                vehicle_id=vehicle_id, plate=vehicle_id, sasi=vehicle_id, group=group, branch=vehicle_branch,
                status='available', total_reservations=0, total_km=0, maintenance_due=False,
            ))

        date_range = (date_end - date_start).days
        for i in range(n_reservations):
            branch = rng.choice(rez_branches)
            group = rng.choice(GROUPS)
            start = date_start + timedelta(days=rng.randint(0, date_range - 2))
            end = start + timedelta(days=rng.randint(1, 7))
            if end > date_end:
                end = date_end
            reservations.append(Reservation.objects.create(
                reservation_id=f"GEN{i+1:03d}", branch=branch,
                vehicle_group=group, start_date=start, end_date=end,
            ))

    elif scenario == 'low_vehicle_count':
        n_vehicles, n_reservations = 5, 50
        date_start, date_end = today, today + timedelta(days=30)

        for _ in range(n_vehicles):
            group = rng.choice(GROUPS)
            branch = rng.choice(branches)
            vehicle_id = f"{VEHICLE_PREFIX[group]}{counters[group]:02d}GEN"
            counters[group] += 1
            vehicles.append(Vehicle.objects.create(
                vehicle_id=vehicle_id, plate=vehicle_id, sasi=vehicle_id, group=group, branch=branch,
                status='available', total_reservations=0, total_km=0, maintenance_due=False,
            ))

        date_range = (date_end - date_start).days
        for i in range(n_reservations):
            branch = rng.choice(branches)
            group = rng.choice(GROUPS)
            start = date_start + timedelta(days=rng.randint(0, date_range - 2))
            end = start + timedelta(days=rng.randint(1, 7))
            if end > date_end:
                end = date_end
            reservations.append(Reservation.objects.create(
                reservation_id=f"GEN{i+1:03d}", branch=branch,
                vehicle_group=group, start_date=start, end_date=end,
            ))

    elif scenario == 'high_suv_demand':
        n_vehicles, n_reservations = 30, 60
        date_start, date_end = today, today + timedelta(days=30)

        for _ in range(n_vehicles):
            group = rng.choice(GROUPS)
            branch = rng.choice(branches)
            vehicle_id = f"{VEHICLE_PREFIX[group]}{counters[group]:02d}GEN"
            counters[group] += 1
            vehicles.append(Vehicle.objects.create(
                vehicle_id=vehicle_id, plate=vehicle_id, sasi=vehicle_id, group=group, branch=branch,
                status='available', total_reservations=0, total_km=0, maintenance_due=False,
            ))

        date_range = (date_end - date_start).days
        for i in range(n_reservations):
            branch = rng.choice(branches)
            group = 'suv' if rng.random() < 0.8 else rng.choice(['economy', 'mid'])
            start = date_start + timedelta(days=rng.randint(0, date_range - 2))
            end = start + timedelta(days=rng.randint(1, 7))
            if end > date_end:
                end = date_end
            reservations.append(Reservation.objects.create(
                reservation_id=f"GEN{i+1:03d}", branch=branch,
                vehicle_group=group, start_date=start, end_date=end,
            ))

    elif scenario == 'maintenance_heavy':
        n_vehicles, n_reservations = 30, 60
        date_start, date_end = today, today + timedelta(days=30)
        maintenance_count = int(n_vehicles * 0.4)

        for i in range(n_vehicles):
            group = rng.choice(GROUPS)
            branch = rng.choice(branches)
            vehicle_id = f"{VEHICLE_PREFIX[group]}{counters[group]:02d}GEN"
            counters[group] += 1
            status = 'maintenance' if i < maintenance_count else 'available'
            vehicles.append(Vehicle.objects.create(
                vehicle_id=vehicle_id, plate=vehicle_id, sasi=vehicle_id, group=group, branch=branch,
                status=status, total_reservations=0, total_km=0, maintenance_due=False,
            ))

        date_range = (date_end - date_start).days
        for i in range(n_reservations):
            branch = rng.choice(branches)
            group = rng.choice(GROUPS)
            start = date_start + timedelta(days=rng.randint(0, date_range - 2))
            end = start + timedelta(days=rng.randint(1, 7))
            if end > date_end:
                end = date_end
            reservations.append(Reservation.objects.create(
                reservation_id=f"GEN{i+1:03d}", branch=branch,
                vehicle_group=group, start_date=start, end_date=end,
            ))

    else:
        raise ValueError(f"Bilinmeyen senaryo: {scenario}")

    return reservations, vehicles

from vehicles.models import TransferCost
from ..validator import check_group, check_status, check_date_conflict

GROUP_PRIORITY = {'suv': 0, 'mid': 1, 'economy': 2}


def get_transfer_cost(from_branch, to_branch):
    if from_branch == to_branch:
        return 0
    try:
        tc = TransferCost.objects.get(from_branch=from_branch, to_branch=to_branch)
        return float(tc.cost)
    except TransferCost.DoesNotExist:
        return float('inf')


def score_vehicle(vehicle, reservation):
    transfer_cost = get_transfer_cost(vehicle.branch, reservation.branch)
    upgrade_penalty = 0 if vehicle.group == reservation.vehicle_group else 10
    return transfer_cost + upgrade_penalty


def has_memory_conflict(vehicle, start_date, end_date, occupied):
    for (s, e) in occupied.get(vehicle.vehicle_id, []):
        if s <= end_date and start_date <= e:
            return True
    return False


def solve(reservations, all_vehicles):
    reservations = sorted(
        reservations,
        key=lambda r: (GROUP_PRIORITY[r.vehicle_group], r.end_date)
    )

    assignments = []
    unassigned = []
    occupied = {}  

    for reservation in reservations:
        candidates = [
            v for v in all_vehicles
            if check_group(v.group, reservation.vehicle_group)
            and check_status(v)
            and check_date_conflict(v, reservation.start_date, reservation.end_date)
            and not has_memory_conflict(v, reservation.start_date, reservation.end_date, occupied)
        ]

        if not candidates:
            unassigned.append(reservation)
            continue

        best = min(candidates, key=lambda v: score_vehicle(v, reservation))
        transfer_cost = get_transfer_cost(best.branch, reservation.branch)

        assignments.append({
            'reservation': reservation,
            'vehicle': best,
            'transfer_cost': transfer_cost,
            'is_upgrade': best.group != reservation.vehicle_group,
        })

        occupied.setdefault(best.vehicle_id, []).append(
            (reservation.start_date, reservation.end_date)
        )

    return assignments, unassigned

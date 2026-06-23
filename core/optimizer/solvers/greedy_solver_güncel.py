from vehicles.models import TransferCost
from ..validator import check_group, check_status, check_date_conflict


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


def post_swap(assignments, unassigned, all_vehicles, occupied):
    rescued = []

    for rez_x in unassigned:
        for assignment in assignments:
            vehicle = assignment['vehicle']
            rez_y = assignment['reservation']
            rez_y_dates = (rez_y.start_date, rez_y.end_date)


            if not check_group(vehicle.group, rez_x.vehicle_group):
                continue


            temp = [d for d in occupied.get(vehicle.vehicle_id, []) if d != rez_y_dates]
            if any(s <= rez_x.end_date and rez_x.start_date <= e for s, e in temp):
                continue

            alt_occupied = {k: list(v) for k, v in occupied.items()}
            alt_occupied[vehicle.vehicle_id] = temp
            alt_candidates = [
                v for v in all_vehicles
                if v.vehicle_id != vehicle.vehicle_id
                and check_group(v.group, rez_y.vehicle_group)
                and check_status(v)
                and not has_memory_conflict(v, rez_y.start_date, rez_y.end_date, alt_occupied)
            ]

            if not alt_candidates:
                continue

            best_alt = min(alt_candidates, key=lambda v: score_vehicle(v, rez_y))

            occupied[vehicle.vehicle_id] = temp
            occupied.setdefault(best_alt.vehicle_id, []).append(rez_y_dates)
            occupied.setdefault(vehicle.vehicle_id, []).append((rez_x.start_date, rez_x.end_date))

            assignment['vehicle'] = best_alt
            assignment['transfer_cost'] = get_transfer_cost(best_alt.branch, rez_y.branch)
            assignment['is_upgrade'] = best_alt.group != rez_y.vehicle_group

            assignments.append({
                'reservation': rez_x,
                'vehicle': vehicle,
                'transfer_cost': get_transfer_cost(vehicle.branch, rez_x.branch),
                'is_upgrade': vehicle.group != rez_x.vehicle_group,
            })
 
            rescued.append(rez_x)
            break

    for r in rescued:
        unassigned.remove(r)

    return assignments, unassigned


def solve(reservations, all_vehicles):
    reservations = sorted(reservations, key=lambda r: r.end_date)

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

    assignments, unassigned = post_swap(assignments, unassigned, all_vehicles, occupied)

    return assignments, unassigned

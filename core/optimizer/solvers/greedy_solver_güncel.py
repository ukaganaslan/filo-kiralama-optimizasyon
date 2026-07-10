from vehicles.models import TransferCost
from ..validator import check_group, check_status


def get_transfer_cost(from_branch, to_branch):
    if from_branch == to_branch:
        return 0
    try:
        tc = TransferCost.objects.get(from_branch=from_branch, to_branch=to_branch)
        return float(tc.cost)
    except TransferCost.DoesNotExist:
        return 0


def return_transfer_cost(reservation):
    if not reservation.return_branch_id:
        return 0
    if reservation.return_branch_id == reservation.branch_id:
        return 0
    return get_transfer_cost(reservation.branch, reservation.return_branch)


def score_vehicle(vehicle, reservation):
    if vehicle.group != reservation.vehicle_group:
        return 10
    preferred = getattr(reservation, 'preferred_vehicle_model', None)
    if not preferred:
        return 0
    if vehicle.catalog_id == preferred.id:
        return 0
    if vehicle.catalog_id and vehicle.catalog.sipp_code == preferred.sipp_code:
        return 0.5
    return 1


def has_memory_conflict(vehicle, start_dt, end_dt, occupied):
    for (s, e) in occupied.get(vehicle.vehicle_id, []):
        if s < end_dt and start_dt < e:
            return True
    return False


def post_swap(assignments, unassigned, all_vehicles, occupied):
    rescued = []

    for rez_x in unassigned:
        for assignment in assignments:
            vehicle = assignment['vehicle']
            rez_y = assignment['reservation']
            rez_y_dates = (rez_y.start_datetime, rez_y.end_datetime)


            if vehicle.branch_id != rez_x.branch_id:
                continue

            if not check_group(vehicle.group, rez_x.vehicle_group):
                continue

            temp = [d for d in occupied.get(vehicle.vehicle_id, []) if d != rez_y_dates]
            if any(s < rez_x.end_datetime and rez_x.start_datetime < e for s, e in temp):
                continue

            alt_occupied = {k: list(v) for k, v in occupied.items()}
            alt_occupied[vehicle.vehicle_id] = temp
            alt_candidates = [
                v for v in all_vehicles
                if v.vehicle_id != vehicle.vehicle_id
                and v.branch_id == rez_y.branch_id
                and check_group(v.group, rez_y.vehicle_group)
                and check_status(v)
                and not has_memory_conflict(v, rez_y.start_datetime, rez_y.end_datetime, alt_occupied)
            ]

            if not alt_candidates:
                continue

            best_alt = min(alt_candidates, key=lambda v: score_vehicle(v, rez_y))

            occupied[vehicle.vehicle_id] = temp
            occupied.setdefault(best_alt.vehicle_id, []).append(rez_y_dates)
            occupied.setdefault(vehicle.vehicle_id, []).append((rez_x.start_datetime, rez_x.end_datetime))

            assignment['vehicle'] = best_alt
            assignment['transfer_cost'] = return_transfer_cost(rez_y)
            assignment['is_upgrade'] = best_alt.group != rez_y.vehicle_group

            assignments.append({
                'reservation': rez_x,
                'vehicle': vehicle,
                'transfer_cost': return_transfer_cost(rez_x),
                'is_upgrade': vehicle.group != rez_x.vehicle_group,
            })

            rescued.append(rez_x)
            break

    for r in rescued:
        unassigned.remove(r)

    return assignments, unassigned


def solve(reservations, all_vehicles, initial_occupied=None):
    reservations = sorted(reservations, key=lambda r: r.end_datetime)

    assignments = []
    unassigned = []
    occupied = {k: list(v) for k, v in initial_occupied.items()} if initial_occupied else {}

    for reservation in reservations:
        candidates = [
            v for v in all_vehicles
            if v.branch_id == reservation.branch_id
            and check_group(v.group, reservation.vehicle_group)
            and check_status(v)
            and not has_memory_conflict(v, reservation.start_datetime, reservation.end_datetime, occupied)
        ]

        if not candidates:
            unassigned.append(reservation)
            continue

        best = min(candidates, key=lambda v: score_vehicle(v, reservation))

        assignments.append({
            'reservation': reservation,
            'vehicle': best,
            'transfer_cost': return_transfer_cost(reservation),
            'is_upgrade': best.group != reservation.vehicle_group,
        })

        occupied.setdefault(best.vehicle_id, []).append(
            (reservation.start_datetime, reservation.end_datetime)
        )

    assignments, unassigned = post_swap(assignments, unassigned, all_vehicles, occupied)

    return assignments, unassigned

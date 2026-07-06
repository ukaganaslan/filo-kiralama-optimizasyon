from vehicles.models import Vehicle, Reservation, Assignment
from .solvers import greedy_solver
from .objective import calculate_score
from .validator import validate_solution


def assign_vehicles(queryset=None):
    """
    Rezervasyonları alır, greedy ile çözer, doğrular, veritabanına kaydeder.
    """
    if queryset is None:
        queryset = Reservation.objects.filter(assignment=None).select_related('branch')

    reservations = list(queryset)
    all_vehicles = list(Vehicle.objects.select_related('branch').all())

    assignments, unassigned = greedy_solver.solve(reservations, all_vehicles)
    violations = validate_solution(assignments)
    score = calculate_score(assignments, unassigned, all_vehicles)

    created = []
    for entry in assignments:
        a = Assignment.objects.create(
            reservation=entry['reservation'],
            vehicle=entry['vehicle'],
            transfer_cost=entry['transfer_cost'],
        )
        created.append(a)

    fulfilled = len(assignments)
    unfulfilled = len(unassigned)

    return {
        'assignments': created,
        'unassigned': unassigned,
        'violations': violations,
        'stats': {
            'total': fulfilled + unfulfilled,
            'fulfilled': fulfilled,
            'unfulfilled': unfulfilled,
            'transfer_count': sum(1 for a in assignments if a['transfer_cost'] > 0),
            'transfer_cost': sum(a['transfer_cost'] for a in assignments),
            'upgrade_count': sum(1 for a in assignments if a['is_upgrade']),
            'score': score,
        }
    }

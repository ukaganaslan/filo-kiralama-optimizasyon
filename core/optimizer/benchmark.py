from .data import small_problem, generated_problems
from .solvers import greedy_solver
from .solvers import greedy_solver_güncel
from .objective import calculate_score
from .validator import validate_solution

FIXED_PROBLEMS = [
    {'label': 'small',  'n_vehicles': 10, 'n_reservations': 20,  'seed': 5},
    {'label': 'medium', 'n_vehicles': 30, 'n_reservations': 60,  'seed': 25},
    {'label': 'large',  'n_vehicles': 90, 'n_reservations': 180, 'seed': 125},
]

SCENARIO_PROBLEMS = [
    'dense_dates',
    'high_transfer',
    'low_vehicle_count',
    'high_suv_demand',
    'maintenance_heavy',
]


def _run_on_data(solver_fn, reservations, vehicles):
    assignments, unassigned = solver_fn(reservations, vehicles)
    total = len(reservations)
    fulfilled = len(assignments)
    upgrade_count = sum(1 for a in assignments if a['is_upgrade'])
    assigned_ids = {a['vehicle'].vehicle_id for a in assignments}
    idle_count = sum(1 for v in vehicles if v.vehicle_id not in assigned_ids)
    return {
        'score': calculate_score(assignments, unassigned, vehicles),
        'fulfilled': fulfilled,
        'unfulfilled': len(unassigned),
        'fulfillment_pct': round(fulfilled / total * 100) if total else 0,
        'transfer_cost': sum(a['transfer_cost'] for a in assignments),
        'upgrade_pct': round(upgrade_count / fulfilled * 100) if fulfilled else 0,
        'idle_pct': round(idle_count / len(vehicles) * 100) if vehicles else 0,
    }


def run():
    solvers = {'greedy': greedy_solver.solve, 'güncel': greedy_solver_güncel.solve}
    problems = []

    reservations, vehicles = small_problem.load()
    problems.append({
        'label': 'fixture', 'seed': '-',
        'n_vehicles': len(vehicles), 'n_reservations': len(reservations),
        'reservations': reservations, 'vehicles': vehicles,
    })

    for fp in FIXED_PROBLEMS:
        reservations, vehicles = generated_problems.generate(
            n_vehicles=fp['n_vehicles'], n_reservations=fp['n_reservations'], seed=fp['seed'],
        )
        problems.append({
            'label': fp['label'], 'seed': str(fp['seed']),
            'n_vehicles': len(vehicles), 'n_reservations': len(reservations),
            'reservations': reservations, 'vehicles': vehicles,
        })

    for scenario in SCENARIO_PROBLEMS:
        reservations, vehicles = generated_problems.generate_scenario(scenario, seed=42)
        problems.append({
            'label': scenario, 'seed': '42',
            'n_vehicles': len(vehicles), 'n_reservations': len(reservations),
            'reservations': reservations, 'vehicles': vehicles,
        })

    results = []
    for problem in problems:
        for solver_adı, solver_fn in solvers.items():
            sonuç = _run_on_data(solver_fn, problem['reservations'], problem['vehicles'])
            results.append({
                'problem': problem['label'], 'seed': problem['seed'],
                'solver': solver_adı,
                'n_vehicles': problem['n_vehicles'], 'n_reservations': problem['n_reservations'],
                **sonuç,
            })

    return results


def print_report():
    results = run()
    print(
        f"{'Problem':>18} {'Solver':>8} {'Araç/Rez':>10} {'Skor':>7} "
        f"{'Karşılanan%':>12} {'Kaçırılan':>10} {'Transfer':>10} {'Upgrade%':>9} {'Boşta%':>7}"
    )
    print("-" * 115)
    last_problem = None
    for r in results:
        if r['problem'] != last_problem and last_problem is not None:
            print()
        last_problem = r['problem']
        araç_rez = f"{r['n_vehicles']}/{r['n_reservations']}"
        print(
            f"{r['problem']:>18} {r['solver']:>8} {araç_rez:>10} {r['score']:>7.0f} "
            f"{r['fulfillment_pct']:>11}% {r['unfulfilled']:>10} "
            f"{r['transfer_cost']:>10.0f} {r['upgrade_pct']:>8}% {r['idle_pct']:>6}%"
        )

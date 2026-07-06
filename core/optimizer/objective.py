import statistics
from collections import defaultdict

from .validator import validate_solution, check_group, check_status

GROUP_LEVEL = {'economy': 0, 'mid': 1, 'suv': 2}

WEIGHTS = {
    'avoidable_miss': 35,       # kriter 1: uygun araç varken karşılanmamış rezervasyon
    'avoidable_upgrade': 20,    # kriter 5: branch içi tam segment müsaitken gereksiz upgrade
    'segment_distance': 15,     # kriter 6: üst segment gereksiz tüketimi
    'low_value_upgrade': 15,    # kriter 7: kısa/düşük değerli rezervasyona pahalı araç
    'branch_inefficiency': 10,  # kriter 8: branch içi genel verimsizlik
    'improvable_swap': 5,       # kriter 9: daha iyi kombinasyon varken kötüsü seçilmesi
}
HARD_VIOLATION_PENALTY = 40
SHORT_DURATION_DAYS = 3


def calculate_score(assignments, unassigned, all_vehicles):
    """
    100 üzerinden algoritma kalite skoru.
    Sert ihlaller (yanlış statüs/grup/çakışma) zaten solver tarafından engellenir;
    yine de oluşurlarsa sabit ağır ceza uygulanır. Geri kalan puan, algoritmanın
    kaçırdığı daha iyi seçeneklere göre düşürülür.
    """
    total = len(assignments) + len(unassigned)
    if total == 0:
        return 100

    occupied = _build_occupied(assignments)
    hard_violations = validate_solution(assignments)

    rates = {
        'avoidable_miss': _avoidable_miss_rate(unassigned, all_vehicles, occupied, total),
        'avoidable_upgrade': _avoidable_upgrade_rate(assignments, all_vehicles, occupied, total),
        'segment_distance': _segment_distance_rate(assignments, total),
        'low_value_upgrade': _low_value_upgrade_rate(assignments, total),
        'branch_inefficiency': _branch_inefficiency_rate(assignments, all_vehicles),
        'improvable_swap': _improvable_swap_rate(assignments, total),
    }

    soft_penalty = sum(rates[key] * WEIGHTS[key] for key in rates)
    hard_penalty = len(hard_violations) * HARD_VIOLATION_PENALTY

    return max(0, min(100, round(100 - soft_penalty - hard_penalty)))


def _build_occupied(assignments):
    occupied = {}
    for a in assignments:
        occupied.setdefault(a['vehicle'].vehicle_id, []).append(
            (a['reservation'].start_date, a['reservation'].end_date)
        )
    return occupied


def _has_conflict(vehicle_id, start_date, end_date, occupied):
    for s, e in occupied.get(vehicle_id, []):
        if s <= end_date and start_date <= e:
            return True
    return False


def _avoidable_miss_rate(unassigned, all_vehicles, occupied, total):
    """Karşılanmayan rezervasyon için gerçekten uygun (müsait, çakışmasız) araç var mıydı?"""
    count = 0
    for r in unassigned:
        for v in all_vehicles:
            if v.branch_id != r.branch_id:
                continue
            if not check_status(v):
                continue
            if not check_group(v.group, r.vehicle_group):
                continue
            if _has_conflict(v.vehicle_id, r.start_date, r.end_date, occupied):
                continue
            count += 1
            break
    return count / total


def _avoidable_upgrade_rate(assignments, all_vehicles, occupied, total):
    """Upgrade yapılan atama için aynı branch'te tam segment eşleşen boş araç var mıydı?"""
    count = 0
    for a in assignments:
        if not a['is_upgrade']:
            continue
        r = a['reservation']
        used_vehicle_id = a['vehicle'].vehicle_id
        for v in all_vehicles:
            if v.vehicle_id == used_vehicle_id:
                continue
            if v.branch_id != r.branch_id:
                continue
            if v.group != r.vehicle_group:
                continue
            if not check_status(v):
                continue
            if _has_conflict(v.vehicle_id, r.start_date, r.end_date, occupied):
                continue
            count += 1
            break
    return count / total


def _segment_distance_rate(assignments, total):
    """Upgrade'in segment mesafesi ağırlıklı toplamı (economy->suv en ağır)."""
    total_distance = 0
    for a in assignments:
        if a['is_upgrade']:
            total_distance += GROUP_LEVEL[a['vehicle'].group] - GROUP_LEVEL[a['reservation'].vehicle_group]
    return total_distance / (total * 2)


def _low_value_upgrade_rate(assignments, total):
    """Upgrade edilen rezervasyon düşük fiyatlı (medyan altı) veya kısa süreli mi?"""
    prices = [float(a['reservation'].total_price) for a in assignments if a['reservation'].total_price is not None]
    median_price = statistics.median(prices) if prices else None

    count = 0
    for a in assignments:
        if not a['is_upgrade']:
            continue
        r = a['reservation']
        duration = (r.end_date - r.start_date).days
        is_low_price = median_price is not None and r.total_price is not None and float(r.total_price) < median_price
        is_short = duration < SHORT_DURATION_DAYS
        if is_low_price or is_short:
            count += 1
    return count / total


def _branch_inefficiency_rate(assignments, all_vehicles):
    """Upgrade yapılan branch'lerde atıl müsait araç oranı.

    Transfer maliyeti buraya dahil edilmez: iade şubesi müşteri/temsilci
    tarafından seçilir, solver yalnızca rezervasyonun alış şubesindeki
    araçlar arasından seçim yapar (bkz. greedy_solver_güncel.solve) — yani
    transfer algoritmanın kontrolünde olmayan bir girdi, cezalandırılmamalı.
    """
    used_ids = {a['vehicle'].vehicle_id for a in assignments}

    active_branches = set()
    for a in assignments:
        if a['is_upgrade']:
            active_branches.add(a['vehicle'].branch_id)

    vehicles_by_branch = defaultdict(list)
    for v in all_vehicles:
        if v.status == 'available':
            vehicles_by_branch[v.branch_id].append(v)

    ratios = []
    for branch_id in active_branches:
        pool = vehicles_by_branch.get(branch_id, [])
        if not pool:
            continue
        idle = sum(1 for v in pool if v.vehicle_id not in used_ids)
        ratios.append(idle / len(pool))

    return sum(ratios) / len(ratios) if ratios else 0


def _swap_distance(vehicle_group, reservation_group):
    if not check_group(vehicle_group, reservation_group):
        return None
    return GROUP_LEVEL[vehicle_group] - GROUP_LEVEL[reservation_group]


def _improvable_swap_rate(assignments, total):
    """Aynı branch'teki iki atamanın aracı takas edilseydi toplam ceza azalır mıydı?"""
    by_branch = defaultdict(list)
    for a in assignments:
        by_branch[a['reservation'].branch_id].append(a)

    count = 0
    for group in by_branch.values():
        n = len(group)
        for i in range(n):
            for j in range(i + 1, n):
                a1, a2 = group[i], group[j]
                d1 = _swap_distance(a1['vehicle'].group, a1['reservation'].vehicle_group)
                d2 = _swap_distance(a2['vehicle'].group, a2['reservation'].vehicle_group)
                swapped_d1 = _swap_distance(a2['vehicle'].group, a1['reservation'].vehicle_group)
                swapped_d2 = _swap_distance(a1['vehicle'].group, a2['reservation'].vehicle_group)
                if swapped_d1 is None or swapped_d2 is None:
                    continue
                if (swapped_d1 + swapped_d2) < (d1 + d2):
                    count += 1
    return count / total

def calculate_score(assignments, unassigned, all_vehicles=None): 
    fulfilled = len(assignments)
    unfulfilled = len(unassigned)
    transfer_cost = sum(a['transfer_cost'] for a in assignments)
    upgrade_count = sum(1 for a in assignments if a['is_upgrade'])

    idle_count = 0
    if all_vehicles:
        assigned_ids = {a['vehicle'].vehicle_id for a in assignments}
        idle_count = sum(1 for v in all_vehicles if v.vehicle_id not in assigned_ids)

    return (fulfilled * 500) - (unfulfilled * 300) - (transfer_cost * 20) - (upgrade_count * 50) - (idle_count * 10)

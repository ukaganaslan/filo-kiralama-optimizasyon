def calculate_score(assignments, unassigned):
    fulfilled = len(assignments)
    unfulfilled = len(unassigned)
    transfer_cost = sum(a['transfer_cost'] for a in assignments)
    upgrade_count = sum(1 for a in assignments if a['is_upgrade'])

    return (fulfilled * 500) - (unfulfilled * 300) - (transfer_cost * 20) - (upgrade_count * 50)

from rest_framework import serializers
from .models import Branch, Vehicle, Reservation, Assignment, TransferCost


class TransferCostSerializer(serializers.ModelSerializer):
    from_branch_name = serializers.CharField(source='from_branch.name', read_only=True)
    to_branch_name = serializers.CharField(source='to_branch.name', read_only=True)

    class Meta:
        model = TransferCost
        fields = ['id', 'from_branch', 'from_branch_name', 'to_branch', 'to_branch_name', 'cost']


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'title']


class VehicleSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    vehicle_id = serializers.CharField(read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'vehicle_id', 'group', 'brand', 'model', 'plate', 'sasi', 'branch', 'branch_name',
            'status', 'total_reservations', 'total_km', 'maintenance_due',
        ]


class ReservationSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    return_branch_name = serializers.CharField(source='return_branch.name', read_only=True, default=None)
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    reservation_id = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    assigned_vehicle_id = serializers.SerializerMethodField()

    def get_assigned_vehicle_id(self, obj):
        result = obj.assignmentresult_set.order_by('-run__created_at').first()
        return result.vehicle.vehicle_id if result else None

    class Meta:
        model = Reservation
        fields = [
            'id', 'reservation_id', 'branch', 'branch_name',
            'return_branch', 'return_branch_name',
            'vehicle_group', 'start_date', 'end_date', 'status',
            'customer_username', 'assigned_vehicle_id',
            'guest_name', 'guest_phone', 'guest_email',
        ]


class AssignmentSerializer(serializers.ModelSerializer):
    reservation = ReservationSerializer(read_only=True)
    vehicle = VehicleSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'reservation', 'vehicle', 'transfer_cost']

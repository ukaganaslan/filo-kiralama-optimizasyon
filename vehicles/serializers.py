from rest_framework import serializers
from .models import Branch, Vehicle, Reservation, Assignment, TransferCost, MaintenanceLog, DailyPrice
from datetime import date




class TransferCostSerializer(serializers.ModelSerializer):
    from_branch_name = serializers.CharField(source='from_branch.name', read_only=True)
    to_branch_name = serializers.CharField(source='to_branch.name', read_only=True)

    class Meta:
        model = TransferCost
        fields = ['id', 'from_branch', 'from_branch_name', 'to_branch', 'to_branch_name', 'cost',]


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'title']


class VehicleSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    branch_title = serializers.CharField(source='branch.title', read_only=True)
    vehicle_id = serializers.CharField(read_only=True)
    current_status = serializers.SerializerMethodField()

    def get_current_status(self, obj):
        if obj.status in ('maintenance', 'service', 'inactive'):
            return obj.status
        today = date.today()
        is_rented = obj.assignmentresult_set.filter(
            reservation__status='assigned',
            reservation__start_date__lte=today,
            reservation__end_date__gte=today,
        ).exists()
        return 'rented' if is_rented else 'available'

    class Meta:
        model = Vehicle
        fields = [
            'id', 'vehicle_id', 'group', 'brand', 'model', 'plate', 'sasi', 'branch', 'branch_name', 'branch_title',
            'status', 'current_status', 'total_reservations', 'total_km', 'maintenance_due',
        ]


class ReservationSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    branch_title = serializers.CharField(source='branch.title', read_only=True)
    return_branch_name = serializers.CharField(source='return_branch.name', read_only=True, default=None)
    return_branch_title = serializers.CharField(source='return_branch.title', read_only=True, default=None)
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    reservation_id = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=False, required=False)
    assigned_vehicle_id = serializers.SerializerMethodField()
    assigned_vehicle_info = serializers.SerializerMethodField()
    current_status = serializers.SerializerMethodField()
    delivery_info = serializers.SerializerMethodField()

    def get_assigned_vehicle_id(self, obj):
        result = obj.assignmentresult_set.order_by('-run__created_at').first()
        return result.vehicle.vehicle_id if result else None

    def get_assigned_vehicle_info(self, obj):
        from datetime import date
        if obj.status != 'assigned' or obj.start_date > date.today():
            return None
        result = obj.assignmentresult_set.order_by('-run__created_at').first()
        if not result:
            return None
        v = result.vehicle
        return {'plate': v.plate, 'brand': v.brand, 'model': v.model, 'total_km': v.total_km, 'damage_map': v.damage_map}

    def get_delivery_info(self, obj):
        logs = {log.event_type: log for log in obj.delivery_logs.all()}
        delivered = logs.get('delivered')
        returned = logs.get('returned')
        return {
            'delivered': bool(delivered) and delivered.stage == 'approved',
            'delivered_stage': delivered.stage if delivered else None,
            'delivered_at': delivered.logged_at.isoformat() if delivered else None,
            'delivered_doc': delivered.document.url if delivered and delivered.document else None,
            'delivered_photo': delivered.photo.url if delivered and delivered.photo else None,
            'delivered_km': delivered.delivery_km if delivered else None,
            'delivered_fuel': delivered.fuel_level if delivered else None,
            'delivered_damage': delivered.damage_items if delivered else [],
            'delivered_notes': delivered.notes if delivered else '',
            'returned': bool(returned) and returned.stage == 'approved',
            'returned_stage': returned.stage if returned else None,
            'returned_at': returned.logged_at.isoformat() if returned else None,
            'returned_doc': returned.document.url if returned and returned.document else None,
            'returned_photo': returned.photo.url if returned and returned.photo else None,
            'returned_km': returned.delivery_km if returned else None, 
            'returned_fuel': returned.fuel_level if returned else None,
            'returned_damage': returned.damage_items if returned else [],
            'returned_notes': returned.notes if returned else '',
    }

    def get_current_status(self, obj):
        from datetime import date
        today = date.today()
        if obj.status == 'cancelled':
            return 'cancelled'
        if obj.status == 'assigned':
            if obj.start_date <= today and obj.end_date >= today:
                return 'active'
            if obj.end_date < today:
                return 'completed'
        return obj.status

    class Meta:
        model = Reservation
        fields = [
            'id', 'reservation_id', 'branch', 'branch_name', 'branch_title',
            'return_branch', 'return_branch_name', 'return_branch_title',
            'vehicle_group', 'start_date', 'end_date', 'status',
            'customer_username', 'assigned_vehicle_id', 'assigned_vehicle_info', 'current_status',
            'guest_name', 'guest_phone', 'guest_email', 'total_price', 'delivery_info',
        ]


class AssignmentSerializer(serializers.ModelSerializer):
    reservation = ReservationSerializer(read_only=True)
    vehicle = VehicleSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'reservation', 'vehicle', 'transfer_cost']

class MaintenanceLogSerializer(serializers.ModelSerializer):
    vehicle_id = serializers.CharField(source='vehicle.vehicle_id', read_only=True)
    vehicle_plate = serializers.CharField(source='vehicle.plate', read_only=True)
    vehicle_group = serializers.CharField(source='vehicle.group', read_only=True)
    vehicle_branch_name = serializers.CharField(source='vehicle.branch.name', read_only=True)
    vehicle_branch_title = serializers.CharField(source='vehicle.branch.title', read_only=True)

    class Meta:
        model = MaintenanceLog
        fields = [
            'id', 'vehicle', 'vehicle_id', 'vehicle_plate', 'vehicle_group', 'vehicle_branch_name', 'vehicle_branch_title',
            'current_km', 'reason', 'start_date', 'end_date', 'notes'
        ]

class DailyPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPrice
        fields = ['id', 'date', 'vehicle_group', 'price_per_day']
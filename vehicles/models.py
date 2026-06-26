from django.db import models
from django.contrib.auth.models import User


class Branch(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=200, blank=True, default='')

    def __str__(self):
        return f"{self.name} - {self.title}" if self.title else self.name


class TransferCost(models.Model):
    from_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='transfers_from')
    to_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='transfers_to')
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.from_branch} → {self.to_branch}: {self.cost}"


class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('available', 'Müsait'),
        ('maintenance', 'Bakımda'),
        ('service', 'Serviste'),
        ('inactive', 'Pasif'),
        ('reserved', 'Rezerve Edildi'),
    ]

    GROUP_CHOICES = [
        ('economy', 'Ekonomi'),
        ('mid', 'Orta Sınıf'),
        ('suv', 'SUV'),
    ]

    vehicle_id = models.CharField(max_length=10, unique=True)
    sasi = models.CharField(max_length=20, unique=True)
    group = models.CharField(max_length=20, choices=GROUP_CHOICES)
    brand = models.CharField(max_length=50, default='')
    model = models.CharField(max_length=50, default='')
    plate = models.CharField(max_length=20, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='vehicles')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    total_reservations = models.IntegerField(default=0)
    total_km = models.IntegerField(default=0)
    maintenance_due = models.BooleanField(default=False)

    maintenance_start_date = models.DateField(null=True, blank=True)
    maintenance_end_date = models.DateField(null=True, blank=True)
    service_start_date = models.DateField(null=True, blank=True)
    service_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle_id} ({self.get_group_display()}) - {self.branch}"


class Reservation(models.Model):
    GROUP_CHOICES = [
        ('economy', 'Ekonomi'),
        ('mid', 'Orta Sınıf'),
        ('suv', 'SUV'),
    ]

    reservation_id = models.CharField(max_length=10, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='reservations')
    vehicle_group = models.CharField(max_length=20, choices=GROUP_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    km_driven = models.IntegerField(null=True, blank=True)

    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('assigned', 'Atandı'),
        ('cancelled', 'İptal'),
    ]

    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations')
    return_branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='return_reservations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    guest_name = models.CharField(max_length=20, blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)
    guest_email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.reservation_id} - {self.branch} - {self.get_vehicle_group_display()}"


class Assignment(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='assignment')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='assignments')
    transfer_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.reservation} → {self.vehicle}"


class MaintenanceLog(models.Model):
    EVENT_CHOICES = [('routine', 'Rutin Bakım'), ('cleaning', 'Temizlik'), ('repair', 'Hasar Onarım')] 
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_logs')
    current_km = models.IntegerField()
    reason = models.CharField(max_length=50, choices=EVENT_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.vehicle} - {self.date}"


class CustomerProfile(models.Model):
    ROLE_CHOICES = [
        ('customer', 'Müşteri'),
        ('representative', 'Temsilci'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True, default=None)
    full_name = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='representatives')

    def __str__(self):
        return self.full_name
    
class PenaltyConfig(models.Model):
    name = models.CharField(max_length=100)
    served_reward = models.IntegerField(default=100)
    missed_penalty = models.IntegerField(default=200)
    upgrade_penalty = models.IntegerField(default=10)
    transfer_weight = models.IntegerField(default=1)
    idle_penalty = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class OptimizationRun(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    solver = models.CharField(max_length=50)
    total_score = models.IntegerField()
    served_count = models.IntegerField()
    missed_count = models.IntegerField()
    penalty_config = models.ForeignKey(PenaltyConfig, on_delete=models.SET_NULL, null=True)
    unassigned_reservations = models.ManyToManyField('Reservation', blank=True, related_name='missed_in_runs')

    def __str__(self):
        return f"{self.solver} - {self.created_at:%Y-%m-%d %H:%M}"


class AssignmentResult(models.Model):
    run = models.ForeignKey(OptimizationRun, on_delete=models.CASCADE, related_name='results')
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE)
    transfer_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_upgrade = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.reservation} → {self.vehicle}"

class DeliveryLog(models.Model):
    EVENT_CHOICES = [
        ('delivered', 'Teslim Edildi'),
        ('returned', 'İade Alındı'),
    ]
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='delivery_logs')
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reservation', 'event_type')

    def __str__(self):
        return f"{self.reservation} - {self.event_type} - {self.logged_at}"


from django.db import models
from django.contrib.auth.models import User
from datetime import time, datetime
from .constants import SIPP_CATEGORY_CHOICES, SIPP_BODY_TYPE_CHOICES


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

class VehicleTypeCode(models.Model):
    """Resmi marka/tip kodu referans listesi (yıllık TSB tip kodu dosyasından
    içe aktarılır, bkz. import_type_codes komutu). Katalog girişinde marka/model
    seçimini serbest metin yerine bu listeden yaptırıp yazım hatalarını önlemek
    ve tip kodunu saklamak için kullanılır."""
    marka_kodu = models.IntegerField()
    tip_kodu = models.IntegerField()
    marka_adi = models.CharField(max_length=50)
    tip_adi = models.CharField(max_length=150)
    ilk_yil = models.IntegerField(null=True, blank=True)
    son_yil = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('marka_kodu', 'tip_kodu')
        indexes = [
            models.Index(fields=['marka_adi']),
        ]

    def __str__(self):
        return f"{self.marka_adi} {self.tip_adi} ({self.tip_kodu})"


class VehicleModel(models.Model):
    GROUP_CHOICES = SIPP_CATEGORY_CHOICES

    FUEL_CHOICES = [
        ('benzin', 'Benzin'), ('dizel', 'Dizel'), ('hibrit', 'Hibrit'),
        ('elektrik', 'Elektrik')
    ]

    TRANSMISSION_CHOICES = [('manuel', 'Manuel'), ('otomatik', 'Otomatik')]

    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    type_code = models.ForeignKey(
        VehicleTypeCode, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicle_models',
    )
    group = models.CharField(max_length=20, choices=GROUP_CHOICES)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    body_type = models.CharField(max_length=1, choices=SIPP_BODY_TYPE_CHOICES, default='D')
    is_4wd = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=True)
    image = models.ImageField(upload_to='vehicle_models/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('brand', 'model', 'fuel_type', 'transmission')

    @property
    def sipp_code(self):
        transmission_code = {
            ('manuel', False): 'M', ('otomatik', False): 'A',
            ('manuel', True): 'N', ('otomatik', True): 'C',
        }.get((self.transmission, self.is_4wd), '?')
        fuel_ac = {
            ('benzin', False): 'R', ('benzin', True): 'N',
            ('lpg', False): 'R', ('lpg', True): 'N',
            ('dizel', False): 'D', ('dizel', True): 'Q',
            ('hibrit', False): 'H', ('hibrit', True): 'H',
            ('elektrik', False): 'E', ('elektrik', True): 'E',
        }.get((self.fuel_type, self.has_ac), '?')
        return f"{self.group}{self.body_type}{transmission_code}{fuel_ac}"

    def __str__(self):
        return f"{self.brand} {self.model} ({self.get_fuel_type_display()}, {self.get_transmission_display()})"


class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('available', 'Müsait'),
        ('maintenance', 'Bakımda'),
        ('service', 'Serviste'),
        ('inactive', 'Pasif'),
        ('reserved', 'Rezerve Edildi'),
    ]

    GROUP_CHOICES = SIPP_CATEGORY_CHOICES

    vehicle_id = models.CharField(max_length=10, unique=True)
    sasi = models.CharField(max_length=20, unique=True)
    group = models.CharField(max_length=20, choices=GROUP_CHOICES)
    brand = models.CharField(max_length=50, default='')
    model = models.CharField(max_length=50, default='')
    catalog = models.ForeignKey('VehicleModel', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles')
    plate = models.CharField(max_length=20, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='vehicles')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    total_reservations = models.IntegerField(default=0)
    total_km = models.IntegerField(default=0)
    damage_map = models.JSONField(default=dict, blank=True)  
    maintenance_due = models.BooleanField(default=False)

    maintenance_start_date = models.DateField(null=True, blank=True)
    maintenance_end_date = models.DateField(null=True, blank=True)
    service_start_date = models.DateField(null=True, blank=True)
    service_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle_id} ({self.get_group_display()}) - {self.branch}"


class Reservation(models.Model):
    GROUP_CHOICES = SIPP_CATEGORY_CHOICES

    reservation_id = models.CharField(max_length=10, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='reservations')
    vehicle_group = models.CharField(max_length=20, choices=GROUP_CHOICES)
    preferred_vehicle_model = models.ForeignKey('VehicleModel', on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations')
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(default=time(10, 0))
    end_time = models.TimeField(default=time(10, 0))
    km_driven = models.IntegerField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    manually_locked = models.BooleanField(default=False)

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

    BILLING_TYPE_CHOICES = [
        ('bireysel', 'Bireysel'),
        ('kurumsal', 'Kurumsal'),
    ]

    billing_type = models.CharField(max_length=20, choices=BILLING_TYPE_CHOICES, default='bireysel', blank=True)
    billing_name = models.CharField(max_length=30, blank=True)
    billing_tckn = models.CharField(max_length=11, blank=True)
    billing_tax_office = models.CharField(max_length=50, blank=True)
    billing_tax_no = models.CharField(max_length=10, blank=True)
    billing_address = models.TextField(blank=True)
    billing_neighborhood = models.CharField(max_length=100, blank=True)
    billing_district = models.CharField(max_length=30, blank=True)
    billing_city = models.CharField(max_length=30, blank=True)
    billing_phone = models.CharField(max_length=20, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'start_date', 'end_date']),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(end_date__gt=models.F('start_date')) |
                    models.Q(end_date=models.F('start_date'), end_time__gt=models.F('start_time'))
                ),
                name='reservation_end_after_start',
            ),
        ]
        ordering = ['-updated_at']


    def __str__(self):
        return f"{self.reservation_id} - {self.branch} - {self.get_vehicle_group_display()}"

    @property
    def start_datetime(self):
        return datetime.combine(self.start_date, self.start_time)

    @property
    def end_datetime(self):
        return datetime.combine(self.end_date, self.end_time)


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

    class Meta:
        indexes = [
            models.Index(fields=['vehicle', 'end_date']),
        ]

    def __str__(self):
        return f"{self.vehicle} - {self.date}"


class ReservationExtension(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    ]
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='extensions')
    requested_end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reject_reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.reservation.reservation_id} → {self.requested_end_date} ({self.status})"


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
    billing_type = models.CharField(max_length=20, choices=Reservation.BILLING_TYPE_CHOICES, default='bireysel', blank=True)
    billing_name = models.CharField(max_length=30, blank=True)
    billing_tckn = models.CharField(max_length=11, blank=True)
    billing_tax_office = models.CharField(max_length=50, blank=True)
    billing_tax_no = models.CharField(max_length=10, blank=True)
    billing_address = models.TextField(blank=True)
    billing_neighborhood = models.CharField(max_length=100, blank=True)
    billing_district = models.CharField(max_length=30, blank=True)
    billing_city = models.CharField(max_length=30, blank=True)
    billing_phone = models.CharField(max_length=20, blank=True)

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

    STAGE_CHOICES = [
        ('pending', 'Belge Bekleniyor'),
        ('photo_pending', 'Fotoğraf Bekleniyor'),
        ('approved', 'Onaylandı'),
    ]

    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='delivery_logs')
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='approved')
    photo = models.ImageField(upload_to='delivery_photos/', null=True, blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)
    document = models.FileField(upload_to='delivery_docs/', null=True, blank=True)
    delivery_km = models.IntegerField(null=True, blank=True)
    fuel_level = models.IntegerField(null=True, blank=True)
    damage_items = models.JSONField(default=list, blank=True) 
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('reservation', 'event_type')

    def __str__(self):
        return f"{self.reservation} - {self.event_type} - {self.logged_at}"

class DailyPrice(models.Model):
    date = models.DateField()
    vehicle_model = models.ForeignKey('VehicleModel', on_delete=models.CASCADE, related_name='daily_prices')
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('date', 'vehicle_model')

class Payment(models.Model):
    STATUS_CHOICES = [
        ('succeeded', 'Tamamlandı'),
        ('failed', 'Başarısız'),
    ]
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='succeeded')
    paid_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.reservation} - {self.amount} - {self.status}"
    
class Notification(models.Model):
    TYPE_CHOICES = [
        ('reservation', 'Rezervasyon'),
        ('extension', 'Uzatma'),
        ('system', 'Sistem'),
    ]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True, default='')
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
        ]
    def __str__(self):
        return f"{self.recipient} - {self.title}"
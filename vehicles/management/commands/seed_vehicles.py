import random
import string

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from vehicles.models import Branch, Vehicle, VehicleModel

# Şube adı (Branch.name = şehir) -> Türkiye plaka il kodu. Eşleşme yoksa '99' kullanılır.
CITY_PLATE_CODES = {
    'İstanbul': '34',
    'Ankara': '06',
    'İzmir': '35',
    'Bursa': '16',
}


def _random_letters(n):
    return ''.join(random.choices(string.ascii_uppercase, k=n))


def _random_digits(n):
    return ''.join(random.choices(string.digits, k=n))


def _unique_plate(city):
    code = CITY_PLATE_CODES.get(city, '99')
    while True:
        candidate = f"{code}{_random_letters(3)}{_random_digits(3)}"
        if not Vehicle.objects.filter(plate=candidate).exists():
            return candidate


def _unique_sasi():
    while True:
        candidate = _random_letters(3) + _random_digits(14)
        if not Vehicle.objects.filter(sasi=candidate).exists():
            return candidate


def _next_vehicle_id(group, taken):
    prefix = group
    suffix = 'GEN'
    existing = Vehicle.objects.filter(vehicle_id__startswith=prefix, vehicle_id__endswith=suffix)
    numbers = []
    for v in existing:
        mid = v.vehicle_id[len(prefix):-len(suffix)]
        if mid.isdigit():
            numbers.append(int(mid))
    for vehicle_id in taken:
        if vehicle_id.startswith(prefix) and vehicle_id.endswith(suffix):
            mid = vehicle_id[len(prefix):-len(suffix)]
            if mid.isdigit():
                numbers.append(int(mid))
    next_num = max(numbers, default=0) + 1
    vehicle_id = f"{prefix}{next_num:02d}{suffix}"
    taken.add(vehicle_id)
    return vehicle_id


class Command(BaseCommand):
    help = (
        "Mevcut şubelere ve aktif katalog modellerine, rastgele dağıtılmış "
        "fiziksel Vehicle kayıtları oluşturur."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Oluşturulacak toplam araç sayısı (varsayılan: 100).',
        )

    def handle(self, *args, **options):
        count = options['count']

        branches = list(Branch.objects.all())
        catalogs = list(VehicleModel.objects.filter(is_active=True))

        if not branches:
            raise CommandError('Hiç şube bulunamadı, önce şube oluşturulmalı.')
        if not catalogs:
            raise CommandError('Hiç aktif katalog modeli bulunamadı, önce VehicleModel oluşturulmalı.')

        taken_vehicle_ids = set()
        created = 0

        with transaction.atomic():
            for _ in range(count):
                branch = random.choice(branches)
                catalog = random.choice(catalogs)

                vehicle_id = _next_vehicle_id(catalog.group, taken_vehicle_ids)
                plate = _unique_plate(branch.name)
                sasi = _unique_sasi()

                Vehicle.objects.create(
                    vehicle_id=vehicle_id,
                    sasi=sasi,
                    group=catalog.group,
                    brand=catalog.brand,
                    model=catalog.model,
                    catalog=catalog,
                    plate=plate,
                    branch=branch,
                    status='available',
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"{created} araç oluşturuldu."))

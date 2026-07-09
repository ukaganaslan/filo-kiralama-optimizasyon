from django.core.management.base import BaseCommand
from django.db import transaction

from vehicles.models import Reservation, Vehicle, VehicleModel


class Command(BaseCommand):
    help = (
        "Reservation, Vehicle ve VehicleModel kayıtlarını tamamen siler. "
        "Branch ve kullanıcı hesaplarına dokunmaz. "
        "--confirm verilmeden hiçbir şey silmez, sadece mevcut sayıları gösterir."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Bu flag verilmeden komut sadece mevcut kayıt sayılarını gösterir, silme yapmaz.',
        )

    def handle(self, *args, **options):
        reservation_count = Reservation.objects.count()
        vehicle_count = Vehicle.objects.count()
        vehicle_model_count = VehicleModel.objects.count()

        self.stdout.write(
            f"Mevcut durum: {reservation_count} Reservation, "
            f"{vehicle_count} Vehicle, {vehicle_model_count} VehicleModel."
        )

        if not options['confirm']:
            self.stdout.write(self.style.WARNING(
                "Hiçbir şey silinmedi. Silmek için --confirm ekleyerek tekrar çalıştır."
            ))
            return

        with transaction.atomic():
            deleted_count, _ = Reservation.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"Reservation: {deleted_count} kayıt silindi."))

            deleted_count, _ = Vehicle.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"Vehicle: {deleted_count} kayıt silindi."))

            deleted_count, _ = VehicleModel.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"VehicleModel: {deleted_count} kayıt silindi."))

        self.stdout.write(self.style.SUCCESS("Temizlik tamamlandı."))

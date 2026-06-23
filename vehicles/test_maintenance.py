from django.test import TestCase
from datetime import date
from vehicles.models import Branch, Vehicle, Reservation, Assignment, MaintenanceLog
from core.maintenance import complete_reservation, complete_maintenance


class CompleteReservationTestleri(TestCase):

    def setUp(self):
        self.şube = Branch.objects.create(name="Ankara")
        self.araç = Vehicle.objects.create(
            vehicle_id="M1", group="mid", branch=self.şube,
            status="available", total_reservations=0, total_km=0
        )
        self.rezervasyon = Reservation.objects.create(
            reservation_id="R001", branch=self.şube, vehicle_group="mid",
            start_date=date(2026, 8, 1), end_date=date(2026, 8, 5)
        )
        Assignment.objects.create(
            reservation=self.rezervasyon, vehicle=self.araç, transfer_cost=0
        )

    def test_sayaçlar_güncellenir(self):
        complete_reservation(self.rezervasyon, km_driven=300)
        self.araç.refresh_from_db()
        self.assertEqual(self.araç.total_reservations, 1)
        self.assertEqual(self.araç.total_km, 300)

    def test_km_rezervasyona_yazılır(self):
        complete_reservation(self.rezervasyon, km_driven=450)
        self.rezervasyon.refresh_from_db()
        self.assertEqual(self.rezervasyon.km_driven, 450)

    def test_bakım_tetiklenmez_eşik_altında(self):
        result = complete_reservation(self.rezervasyon, km_driven=300)
        self.assertEqual(result['status'], 'ok')
        self.araç.refresh_from_db()
        self.assertEqual(self.araç.status, 'available')

    def test_10_rezervasyonda_bakım_tetiklenir(self):
        self.araç.total_reservations = 9
        self.araç.save()
        result = complete_reservation(self.rezervasyon, km_driven=300)
        self.assertEqual(result['status'], 'maintenance')
        self.araç.refresh_from_db()
        self.assertEqual(self.araç.status, 'maintenance')

    def test_10000_km_de_bakım_tetiklenir(self):
        self.araç.total_km = 9700
        self.araç.save()
        result = complete_reservation(self.rezervasyon, km_driven=400)
        self.assertEqual(result['status'], 'maintenance')
        self.araç.refresh_from_db()
        self.assertEqual(self.araç.status, 'maintenance')

    def test_bakım_sonrası_sayaçlar_sıfırlanır(self):
        self.araç.total_reservations = 9
        self.araç.save()
        complete_reservation(self.rezervasyon, km_driven=300)
        self.araç.refresh_from_db()
        self.assertEqual(self.araç.total_reservations, 0)
        self.assertEqual(self.araç.total_km, 0)

    def test_bakım_logu_oluşturulur(self):
        self.araç.total_reservations = 9
        self.araç.save()
        complete_reservation(self.rezervasyon, km_driven=300)
        log = MaintenanceLog.objects.filter(vehicle=self.araç).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.reservations_at_maintenance, 10)

    def test_atanmamış_rezervasyon_hata_fırlatır(self):
        rezervasyon2 = Reservation.objects.create(
            reservation_id="R002", branch=self.şube, vehicle_group="mid",
            start_date=date(2026, 8, 6), end_date=date(2026, 8, 8)
        )
        with self.assertRaises(ValueError):
            complete_reservation(rezervasyon2, km_driven=100)


class CompleteMaintenance(TestCase):

    def setUp(self):
        self.şube = Branch.objects.create(name="Ankara")
        self.araç = Vehicle.objects.create(
            vehicle_id="M1", group="mid", branch=self.şube,
            status="maintenance", maintenance_due=True,
            maintenance_start_date=date(2026, 8, 5)
        )

    def test_araç_müsaite_döner(self):
        complete_maintenance(self.araç, end_date=date(2026, 8, 10))
        self.araç.refresh_from_db()
        self.assertEqual(self.araç.status, 'available')

    def test_bakım_bitiş_tarihi_kaydedilir(self):
        complete_maintenance(self.araç, end_date=date(2026, 8, 10))
        self.araç.refresh_from_db()
        self.assertEqual(self.araç.maintenance_end_date, date(2026, 8, 10))

    def test_maintenance_due_false_olur(self):
        complete_maintenance(self.araç, end_date=date(2026, 8, 10))
        self.araç.refresh_from_db()
        self.assertFalse(self.araç.maintenance_due)

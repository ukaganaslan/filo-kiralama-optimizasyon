from django.test import TestCase
from datetime import date
from vehicles.models import Branch, Vehicle, Reservation, Assignment, TransferCost
from core.optimizer.validator import check_status, check_group, check_date_conflict


class CheckStatusTestleri(TestCase):

    def setUp(self):
        self.şube = Branch.objects.create(name="Ankara")

    def test_müsait_araç_true_döner(self):
        araç = Vehicle.objects.create(
            vehicle_id="E1", group="economy", branch=self.şube, status="available"
        )
        self.assertTrue(check_status(araç))

    def test_bakımdaki_araç_false_döner(self):
        araç = Vehicle.objects.create(
            vehicle_id="E2", group="economy", branch=self.şube, status="maintenance"
        )
        self.assertFalse(check_status(araç))

    def test_servisteki_araç_false_döner(self):
        araç = Vehicle.objects.create(
            vehicle_id="E3", group="economy", branch=self.şube, status="service"
        )
        self.assertFalse(check_status(araç))

    def test_inaktif_araç_false_döner(self):
        araç = Vehicle.objects.create(
            vehicle_id="E4", group="economy", branch=self.şube, status="inactive"
        )
        self.assertFalse(check_status(araç))


class CheckGroupTestleri(TestCase):

    def test_economy_isteğine_economy_atanabilir(self):
        self.assertTrue(check_group("economy", "economy"))

    def test_economy_isteğine_mid_atanabilir(self):
        self.assertTrue(check_group("mid", "economy"))

    def test_economy_isteğine_suv_atanabilir(self):
        self.assertTrue(check_group("suv", "economy"))

    def test_mid_isteğine_economy_atanamaz(self):
        self.assertFalse(check_group("economy", "mid"))

    def test_mid_isteğine_mid_atanabilir(self):
        self.assertTrue(check_group("mid", "mid"))

    def test_mid_isteğine_suv_atanabilir(self):
        self.assertTrue(check_group("suv", "mid"))

    def test_suv_isteğine_sadece_suv_atanabilir(self):
        self.assertTrue(check_group("suv", "suv"))
        self.assertFalse(check_group("mid", "suv"))
        self.assertFalse(check_group("economy", "suv"))


class CheckDateConflictTestleri(TestCase):

    def setUp(self):
        self.şube = Branch.objects.create(name="Ankara")
        self.araç = Vehicle.objects.create(
            vehicle_id="E1", group="economy", branch=self.şube, status="available"
        )
        # Araç 5-10 Ağustos arasında rezervasyona atandı
        self.rezervasyon = Reservation.objects.create(
            reservation_id="R001", branch=self.şube, vehicle_group="economy",
            start_date=date(2026, 8, 5), end_date=date(2026, 8, 10)
        )
        Assignment.objects.create(
            reservation=self.rezervasyon, vehicle=self.araç, transfer_cost=0
        )

    def test_çakışmayan_tarih_müsait(self):
        # 1-4 Ağustos → çakışmaz
        self.assertTrue(
            check_date_conflict(self.araç, date(2026, 8, 1), date(2026, 8, 4))
        )

    def test_çakışan_tarih_müsait_değil(self):
        # 7-12 Ağustos → çakışır
        self.assertFalse(
            check_date_conflict(self.araç, date(2026, 8, 7), date(2026, 8, 12))
        )

    def test_aynı_gün_biten_başlayan_çakışır(self):
        # 10 Ağustos'ta bitti, 10 Ağustos'ta yeni rezervasyon → çakışmalı (lte/gte)
        self.assertFalse(
            check_date_conflict(self.araç, date(2026, 8, 10), date(2026, 8, 12))
        )

    def test_bitişten_sonra_müsait(self):
        # 11 Ağustos'tan itibaren → müsait
        self.assertTrue(
            check_date_conflict(self.araç, date(2026, 8, 11), date(2026, 8, 15))
        )

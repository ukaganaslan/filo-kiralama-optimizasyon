from django.test import TestCase
from django.db import IntegrityError, transaction
from datetime import date, time
from vehicles.models import Branch, Vehicle, Reservation, Assignment, TransferCost
from vehicles.views import _has_capacity_for_range
from core.optimizer.validator import check_status, check_group, check_date_conflict, validate_solution
from core.optimizer.solvers import greedy_solver_güncel


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


class ReservationSaatKısıtıTestleri(TestCase):
    """Aynı gün içinde end_time > start_time zorunluluğu (CheckConstraint)."""

    def setUp(self):
        self.şube = Branch.objects.create(name="Ankara")

    def test_aynı_gün_iade_saati_alış_saatinden_erken_reddedilir(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Reservation.objects.create(
                    reservation_id="R100", branch=self.şube, vehicle_group="economy",
                    start_date=date(2026, 8, 5), end_date=date(2026, 8, 5),
                    start_time=time(14, 0), end_time=time(10, 0),
                )

    def test_aynı_gün_iade_saati_alış_saatinden_geç_kabul_edilir(self):
        r = Reservation.objects.create(
            reservation_id="R101", branch=self.şube, vehicle_group="economy",
            start_date=date(2026, 8, 5), end_date=date(2026, 8, 5),
            start_time=time(10, 0), end_time=time(14, 0),
        )
        self.assertEqual(r.reservation_id, "R101")


class HasCapacityForRangeTestleri(TestCase):
    """views._has_capacity_for_range sweep-line kapasite kontrolü."""

    def setUp(self):
        self.şube = Branch.objects.create(name="Ankara")
        Vehicle.objects.create(vehicle_id="E1", group="economy", branch=self.şube, status="available")
        # Kapasite = 1, mevcut rezervasyon 5 Ağustos'ta 10:00'da bitiyor
        Reservation.objects.create(
            reservation_id="R200", branch=self.şube, vehicle_group="economy",
            start_date=date(2026, 8, 1), end_date=date(2026, 8, 5),
            start_time=time(10, 0), end_time=time(10, 0), status="assigned",
        )

    def test_aynı_gün_dokunan_saatlerde_yeni_rezervasyon_kabul_edilir(self):
        # İade 10:00, yeni alış 10:00 aynı gün → artık kapasite var
        self.assertTrue(
            _has_capacity_for_range(
                self.şube.id, "economy", date(2026, 8, 5), date(2026, 8, 8),
                time(10, 0), time(10, 0),
            )
        )

    def test_bir_dakika_gerçek_çakışma_reddedilir(self):
        # İade 10:00, yeni alış 09:59 aynı gün → hâlâ çakışıyor
        self.assertFalse(
            _has_capacity_for_range(
                self.şube.id, "economy", date(2026, 8, 5), date(2026, 8, 8),
                time(9, 59), time(10, 0),
            )
        )


class GüncelSolverSaatFarkındalığıTestleri(TestCase):
    """greedy_solver_güncel + validate_solution aynı gün arka arkaya rezervasyonları
    aynı araca atayabiliyor mu, ve bunu hatalı çakışma saymıyor mu."""

    def setUp(self):
        self.şube = Branch.objects.create(name="Ankara")
        self.araç = Vehicle.objects.create(
            vehicle_id="E1", group="E", branch=self.şube, status="available"
        )
        self.r1 = Reservation.objects.create(
            reservation_id="R300", branch=self.şube, vehicle_group="E",
            start_date=date(2026, 8, 1), end_date=date(2026, 8, 5),
            start_time=time(10, 0), end_time=time(10, 0),
        )
        self.r2 = Reservation.objects.create(
            reservation_id="R301", branch=self.şube, vehicle_group="E",
            start_date=date(2026, 8, 5), end_date=date(2026, 8, 10),
            start_time=time(10, 0), end_time=time(10, 0),
        )

    def test_aynı_gün_dokunan_rezervasyonlar_aynı_araca_atanır(self):
        assignments, unassigned = greedy_solver_güncel.solve(
            [self.r1, self.r2], [self.araç]
        )
        self.assertEqual(len(unassigned), 0)
        vehicle_ids = {a['vehicle'].vehicle_id for a in assignments}
        self.assertEqual(vehicle_ids, {"E1"})

    def test_dokunan_atamalar_ihlal_üretmez(self):
        assignments, unassigned = greedy_solver_güncel.solve(
            [self.r1, self.r2], [self.araç]
        )
        violations = validate_solution(assignments)
        self.assertEqual(violations, [])

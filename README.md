# Araç Kiralama Rezervasyon ve Optimizasyon Sistemi

Araç kiralama şirketleri için geliştirilmiş, rezervasyon yönetimi ve filo optimizasyonu sağlayan tam yığın web uygulaması. Üç farklı kullanıcı rolüne (müşteri, temsilci, operatör) sahip panel sistemi içerir.

## Teknolojiler

**Backend**
- Python 3 / Django 4
- Django REST Framework (Token tabanlı auth)
- PostgreSQL

**Frontend**
- Vue 3 (Composition API)
- Vite
- Pinia (state management)
- Vue Router (nested routes + layout inheritance)
- Axios
- FullCalendar (ResourceTimeline — Gantt görünümü)
- V-Calendar (tarih seçici)
- Inter font (Google Fonts)

## Kullanıcı Rolleri ve Özellikler

### Müşteri
- Şube seçerek araç grubu (Ekonomi / Orta Sınıf / SUV) bazlı rezervasyon oluşturma
- Farklı iade şubesi seçimi ve transfer ücreti önizlemesi
- Müsait günleri takvim üzerinde görme
- Rezervasyonları listeleme ve iptal etme
- Profil bilgilerini düzenleme (ad soyad, e-posta, telefon, şifre)

### Temsilci
- Kendi şubesine ait rezervasyonları liste veya Gantt takviminde görme
- Müşteri adına rezervasyon oluşturma (yalnızca kendi şubesi için)
- Şubesine ait araç listesini görme ve araç durumu takibi
- Profil bilgilerini düzenleme

### Operatör (Admin)
- Tüm şubelerdeki rezervasyonları liste veya Gantt takviminde görme
- Tek tıkla greedy optimizasyonu çalıştırma
- Optimizasyon sonuçlarını (skor, atamalar, karşılanamayan rezervasyonlar) inceleme
- Araç yönetimi: ekleme, düzenleme, silme (marka/model/plaka/şasi/grup/şube/durum)
- Şube yönetimi: ekleme, düzenleme (81 il dropdown)
- Kullanıcı yönetimi: listeleme, rol atama, aktif/pasif toggle
- Şubeler arası transfer ücreti tanımlama ve yönetimi

## Optimizasyon Algoritması

Akıllı Greedy algoritması + post-swap iyileştirmesi:

1. Rezervasyonları bitiş tarihine göre sırala (EDF)
2. Her rezervasyon için uygun araçları bul — **yalnızca aynı şubedeki araçlar** adaydır
3. En düşük maliyetli aracı seç (aynı grup → 0 puan, upgrade → -10 puan)
4. Transfer maliyeti yalnızca **iade şubesi** farklıysa uygulanır (alış şubesi ≠ iade şubesi)
5. Atama yapılamayan rezervasyonlar için post-swap: mevcut atamaları takasa sokarak yeni slot aç

**Puan sistemi:**

| Durum | Puan |
|-------|------|
| Karşılanan rezervasyon | +100 |
| Karşılanamayan rezervasyon | -200 |
| Transfer maliyeti (iade şubesi farkı) | gerçek maliyet |
| Upgrade (üst gruba atama) | -10 |

## Kurulum

### Gereksinimler
- Python 3.9+
- Node.js 18+
- PostgreSQL

### Backend

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata vehicles/fixtures/initial_data.json
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Uygulama `http://localhost:5173` adresinde açılır.

### Admin hesabı oluşturma

```bash
python manage.py createsuperuser
```

Superuser oluşturulduktan sonra `/api/admin/` panelinden kullanıcılara `admin` / `representative` rolü atanabilir. Temsilcilere şube bağlamak için de aynı panel kullanılır.

## Proje Yapısı

```
├── core/
│   ├── optimizer/
│   │   ├── solvers/
│   │   │   └── greedy_solver_güncel.py   # Ana algoritma (şube kısıtlı)
│   │   ├── objective.py                  # Skor hesaplama
│   │   └── validator.py                  # Kısıt kontrolü
│   ├── settings.py
│   └── urls.py
├── vehicles/
│   ├── models.py           # Branch, Vehicle, Reservation, TransferCost, UserProfile
│   ├── serializers.py
│   ├── views.py            # API endpoint'leri
│   └── fixtures/
│       └── initial_data.json
└── frontend/
    └── src/
        ├── layouts/        # AdminLayout, RepresentativeLayout, CustomerLayout
        ├── views/          # Tüm sayfa bileşenleri
        ├── stores/         # auth, optimization (Pinia)
        └── router/         # Rol tabanlı route koruması
```

## API Endpoint'leri

| Method | URL | Açıklama |
|--------|-----|----------|
| POST | `/api/login/` | Giriş |
| POST | `/api/register/` | Kayıt |
| GET/PATCH | `/api/profile/` | Profil görüntüle / güncelle |
| GET | `/api/branches/` | Şube listesi |
| GET/POST/PATCH/DELETE | `/api/vehicles/` | Araç CRUD |
| GET/POST | `/api/reservations/` | Rezervasyon listesi / oluşturma |
| POST | `/api/reservations/{id}/cancel/` | Rezervasyon iptal |
| GET | `/api/availability/` | Şube + grup bazlı müsait günler |
| GET | `/api/transfer-cost/` | İki şube arası transfer ücreti |
| GET/POST/PATCH/DELETE | `/api/transfer-costs/` | Transfer ücreti CRUD (admin) |
| POST | `/api/optimize/` | Optimizasyon çalıştır |
| GET | `/api/optimize/latest/` | Son optimizasyon sonucu |

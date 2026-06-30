# Araç Kiralama Rezervasyon ve Optimizasyon Sistemi

Araç kiralama şirketleri için geliştirilmiş, rezervasyon yönetimi ve filo optimizasyonu sağlayan tam yığın web uygulaması. Üç farklı kullanıcı rolüne (müşteri, temsilci, admin) sahip panel sistemi ve hesap gerektirmeyen misafir rezervasyon akışı içerir.

## Teknolojiler

**Backend**
- Python 3 / Django 4
- Django REST Framework (Token tabanlı auth)
- PostgreSQL

**Frontend**
- Vue 3 (Composition API + `<script setup>`)
- Vite
- Pinia (state management)
- Vue Router (nested routes + layout inheritance)
- Axios
- PrimeVue 4 (Aura teması — FileUpload, Toast, Stepper)
- FullCalendar (ResourceTimeline — Gantt görünümü)
- V-Calendar (iki aylı tarih aralığı seçici)
- html2canvas + jsPDF (PDF export)
- Inter font (Google Fonts)

## Kullanıcı Rolleri ve Özellikler

### Misafir (Hesapsız)
- Hesap oluşturmadan araç rezervasyonu yapma
- Şube, araç grubu ve tarih seçimi
- Rezervasyon kodu ile sorgulama ve iptal (kod + e-posta doğrulaması)
- Rezervasyon koduna tıklayarak panoya kopyalama

### Müşteri
- Şube ve araç grubu (Ekonomi / Orta Sınıf / SUV) seçerek rezervasyon oluşturma
- Farklı iade şubesi seçimi ve transfer ücreti önizlemesi
- Müsait günleri iki aylı takvim üzerinde görme
- Rezervasyonları listeleme ve iptal etme
- Profil bilgilerini düzenleme (kullanıcı adı, ad soyad, e-posta, telefon, şifre)

### Temsilci
- Kendi şubesine ait rezervasyonları liste veya Gantt takviminde görme
- Takvimde araç satırına sürükleyerek tarih + araç grubu otomatik dolu rezervasyon oluşturma
- Müşteri adına rezervasyon oluşturma (searchable dropdown ile müşteri seçimi)
- Şubesine ait araçları listeleme — gerçek zamanlı durum gösterimi (Müsait / Kiralandı / Bakımda / Serviste)
- Araç geçmişi modalı (rezervasyon + bakım logları, toplam KM)
- **Araç Teslimi:** KM, yakıt seviyesi, SVG tabanlı hasar haritası, notlar, belge yükleme → PDF export
- **Araç İadesi:** Teslim kaydıyla yan yana readonly karşılaştırma, KM/yakıt/hasar/notlar girişi → PDF export
- Teslimat logları listeleme
- Bakım kayıtları oluşturma ve takip
- Günün özeti: bugün teslim / bugün iade / bakımda araç kartları
- Profil bilgilerini düzenleme

### Admin (Operatör)
- Tüm şubelerdeki rezervasyonları liste veya Gantt takviminde görme
- İstatistik kartları: Aktif Rezervasyon, Bekleyen, Atandı, Araç Filosu
- Tek tıkla greedy optimizasyonu çalıştırma
- Optimizasyon sonuçlarını (skor, atamalar, karşılanamayan rezervasyonlar) inceleme
- Araç yönetimi: ekleme, düzenleme, silme (marka / model / plaka / şasi / grup / şube / durum)
- Araç gerçek zamanlı durum takibi (`current_status`: Müsait / Kiralandı / Bakımda / Serviste)
- Araç geçmişi modalı (rezervasyon + bakım logları)
- Şube yönetimi: ekleme, düzenleme (81 il dropdown)
- Kullanıcı yönetimi: listeleme, rol atama (müşteri / temsilci / admin), şube atama, aktif/pasif toggle
- Şubeler arası transfer ücreti tanımlama ve yönetimi
- Fiyatlandırma: FullCalendar üzerinde araç grubu ve tarih aralığı bazlı günlük fiyat tanımlama
- Bakım kayıtları yönetimi
- Teslimat logları görüntüleme

## Araç Teslim / İade Akışı

Temsilci ve admin panelinde rezervasyon detayından açılan ayrı sayfalardır.

**Teslim Formu (`/representative/teslim/:id`)**
- Teslim KM, yakıt seviyesi (kaydırıcı, 1/8 hassasiyet)
- SVG tabanlı interaktif hasar haritası (13 araç bölgesi, 7 hasar tipi: Orijinal / Sürtme / Göçük / Çizik / Leke / Çatlak / Eksik)
- Notlar ve belge yükleme (PDF, DOCX, JPG, PNG)
- İşlem sonrası PDF export

**İade Formu (`/representative/iade/:id`)**
- Sol panel: teslim anındaki KM, yakıt, notlar ve hasar haritası (readonly karşılaştırma)
- Sağ panel: iade KM, yakıt, hasar haritası, notlar, belge yükleme
- İşlem sonrası PDF export (her iki panel dahil)

## Optimizasyon Algoritması

Akıllı Greedy algoritması + post-swap iyileştirmesi:

1. Rezervasyonları bitiş tarihine göre sırala (EDF)
2. Her rezervasyon için uygun araçları bul — **yalnızca aynı şubedeki araçlar** adaydır
3. En düşük maliyetli aracı seç (aynı grup → 0 puan, upgrade → -10 puan)
4. Transfer maliyeti yalnızca **iade şubesi** farklıysa uygulanır
5. Atama yapılamayan rezervasyonlar için post-swap: mevcut atamaları takasa sokarak yeni slot aç
6. Aktif rezervasyonlar (bugün müşterideki araçlar) kilitlenir — optimizer tarafından değiştirilemez

**Puan sistemi:**

| Durum | Puan |
|-------|------|
| Karşılanan rezervasyon | +500 |
| Karşılanamayan rezervasyon | -300 |
| Transfer maliyeti (iade şubesi farkı) | gerçek maliyet × 20 |
| Upgrade (üst gruba atama) | -50 |

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

### Ortam değişkenleri

`frontend/.env` dosyası oluştur:
```
VITE_API_BASE=http://127.0.0.1:8000
```

### Admin hesabı oluşturma

```bash
python manage.py createsuperuser
```

Superuser oluşturduktan sonra `/api/admin/` panelinden kullanıcılara `admin` / `representative` rolü atanabilir. Temsilcilere şube bağlamak için de aynı panel kullanılır.

## Proje Yapısı

```
├── core/
│   ├── optimizer/
│   │   ├── solvers/
│   │   │   └── greedy_solver_güncel.py   # Ana algoritma (şube kısıtlı + post-swap)
│   │   ├── objective.py                  # Skor hesaplama
│   │   └── validator.py                  # Kısıt kontrolü
│   ├── settings.py
│   └── urls.py
├── vehicles/
│   ├── models.py           # Branch, Vehicle, Reservation, DeliveryLog, MaintenanceLog, DailyPrice...
│   ├── serializers.py      # current_status, delivery_info dahil tüm serializer'lar
│   ├── views.py            # Tüm API endpoint'leri
│   └── fixtures/
│       └── initial_data.json
└── frontend/
    └── src/
        ├── assets/
        │   └── cardamage_frame.svg       # SVG hasar haritası çizimi
        ├── components/
        │   └── CarDamageMap.vue          # İnteraktif hasar haritası bileşeni
        ├── layouts/        # AdminLayout, RepresentativeLayout, CustomerLayout
        ├── views/          # Tüm sayfa bileşenleri
        ├── stores/         # auth, optimization (Pinia)
        ├── router/         # Rol tabanlı route koruması
        └── style.css       # Global badge renk standardı
```

## API Endpoint'leri

| Method | URL | Açıklama | Yetki |
|--------|-----|----------|-------|
| POST | `/api/login/` | Giriş | Herkese açık |
| POST | `/api/logout/` | Çıkış | Auth |
| POST | `/api/register/` | Müşteri kaydı | Herkese açık |
| GET/PATCH | `/api/profile/` | Profil görüntüle / güncelle | Auth |
| GET | `/api/branches/` | Şube listesi | Auth |
| GET/POST/PATCH/DELETE | `/api/vehicles/` | Araç CRUD | Okuma: Auth, Yazma: Admin |
| GET | `/api/vehicles/{id}/history/` | Araç rezervasyon + bakım geçmişi | Auth |
| GET/POST | `/api/reservations/` | Rezervasyon listesi / oluşturma | Auth |
| DELETE | `/api/reservations/{id}/` | Rezervasyon silme | Admin |
| POST | `/api/reservations/{id}/deliver/` | Araç teslim kaydı | Temsilci / Admin |
| POST | `/api/reservations/{id}/return/` | Araç iade kaydı | Temsilci / Admin |
| GET | `/api/availability/` | Şube + grup bazlı müsait günler | Herkese açık |
| GET | `/api/transfer-cost/` | İki şube arası transfer ücreti | Auth |
| GET/POST/PATCH/DELETE | `/api/transfer-costs/` | Transfer ücreti CRUD | Admin |
| GET | `/api/daily-prices/` | Günlük fiyat listesi | Auth |
| POST | `/api/daily-prices/bulk_set/` | Tarih aralığı toplu fiyat tanımlama | Admin |
| DELETE | `/api/daily-prices/{id}/` | Fiyat kaydı silme | Admin |
| GET | `/api/delivery-logs/` | Teslimat logları | Temsilci / Admin |
| GET/POST/PATCH/DELETE | `/api/maintenance-logs/` | Bakım kayıtları CRUD | Temsilci / Admin |
| POST | `/api/optimize/` | Optimizasyon çalıştır | Admin |
| GET | `/api/optimize/latest/` | Son optimizasyon sonucu | Admin |
| GET | `/api/users/` | Kullanıcı listesi | Admin / Temsilci |
| POST | `/api/users/create/` | Kullanıcı oluşturma | Admin |
| PATCH | `/api/users/{id}/update/` | Kullanıcı güncelleme | Admin |
| POST | `/api/users/{id}/toggle-active/` | Aktif/pasif toggle | Admin |
| POST | `/api/guest-reservation/` | Misafir rezervasyon oluşturma | Herkese açık |
| GET | `/api/guest-reservation/query/` | Rezervasyon kodu ile sorgulama | Herkese açık |
| POST | `/api/guest-reservation/cancel/` | Misafir rezervasyon iptali | Herkese açık |

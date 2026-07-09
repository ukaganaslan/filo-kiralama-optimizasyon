# Araç Kiralama Rezervasyon ve Optimizasyon Sistemi

Araç kiralama şirketleri için geliştirilmiş, rezervasyon yönetimi ve filo optimizasyonu sağlayan tam yığın web uygulaması. Üç farklı kullanıcı rolüne (müşteri, temsilci, admin) sahip panel sistemi ve hesap gerektirmeyen misafir rezervasyon akışı içerir.

## Teknolojiler

**Backend**
- Python 3 / Django 4
- Django REST Framework (Token tabanlı auth)
- PostgreSQL
- xhtml2pdf (sunucu taraflı PDF üretimi — teslim/iade belgeleri)
- Pillow (araç fotoğrafı `ImageField` desteği)
- Gunicorn + WhiteNoise + dj-database-url (production/Railway)

**Frontend**
- Vue 3 (Composition API + `<script setup>`)
- Vite
- Pinia (state management)
- Vue Router (nested routes + layout inheritance)
- Axios
- PrimeVue 4 (Aura teması — FileUpload, Toast, Stepper) + PrimeIcons
- FullCalendar (ResourceTimeline — Gantt görünümü)
- V-Calendar (iki aylı tarih aralığı seçici)
- ApexCharts (vue3-apexcharts) — istatistik grafikleri
- Inter font (Google Fonts)

**Deployment**
- Backend: Railway (Django + PostgreSQL + Gunicorn)
- Frontend: Vercel

## Kullanıcı Rolleri ve Özellikler

### Misafir (Hesapsız)
- Hesap oluşturmadan araç rezervasyonu yapma
- Şube ve tarih seçiminin ardından, resimli/filtrelenebilir bir katalogdan marka/model seçimi (bkz. "Araç Kataloğu ve SIPP Kodu" bölümü) — seçilen modelin o tarih aralığı için kesin fiyatı kartta gösterilir
- Rezervasyon kodu ile sorgulama ve iptal (kod + e-posta doğrulaması)
- Rezervasyon koduna tıklayarak panoya kopyalama
- Detay modalı: talep edilen model ("ya da eşdeğeri" notuyla), araç bilgisi (teslim günü geldiyse plaka/marka/model, farklı bir modelle karşılandıysa bilgilendirme notu), teslim/iade KM-yakıt-not, hasar haritası ve yüklenen belge — kayıtlı müşteriyle aynı görünüm

### Müşteri
- Şube → tarih → araç modeli sırasıyla rezervasyon oluşturma: resimli kartlarla marka/model seçimi, grup/yakıt/vites filtreleri, her kartta o tarih aralığı için kesin fiyat ve "ya da eşdeğeri" uyarısı (bkz. "Araç Kataloğu ve SIPP Kodu")
- Farklı iade şubesi seçimi ve transfer ücreti önizlemesi
- Müsait günleri iki aylı takvim üzerinde görme
- Rezervasyonları listeleme ve iptal etme
- Rezervasyon detay modalı: talep edilen model, atanan araç bilgisi (farklı bir modelle karşılandıysa bilgilendirme notu), teslim/iade KM-yakıt-not, hasar haritası (readonly), belge; durum etiketi teslim/iade durumuna göre dinamik
- Profil bilgilerini düzenleme (kullanıcı adı, ad soyad, e-posta, telefon, şifre)

### Temsilci
- Kendi şubesine ait rezervasyonları liste veya Gantt takviminde görme (kaynak etiketleri: marka/model · plaka · SIPP kodu)
- Takvimde araç satırına sürükleyerek tarih + araç grubu otomatik dolu rezervasyon oluşturma
- Müşteri adına rezervasyon oluşturma (searchable dropdown ile müşteri seçimi, katalogdan araç modeli seçimi zorunlu)
- Şubesine ait araçları listeleme — gerçek zamanlı durum gösterimi (Müsait / Kiralandı / Bakımda / Serviste); araç eklerken/düzenlerken katalog modeli seçilir, marka/model/grup otomatik gelir
- Araç geçmişi modalı (rezervasyon + bakım logları, toplam KM)
- **Araç Teslimi / İadesi:** 3 aşamalı onay süreci (bkz. "Araç Teslim / İade Akışı" bölümü)
- Sayfa yarım kalmış bir süreçle tekrar açıldığında kaldığı adıma otomatik yönlendirme
- Günün özeti kartlarındaki teslim/iade satırlarına tıklayınca ilgili forma yönlendirme
- Teslimat logları listeleme
- Bakım kayıtları oluşturma ve takip
- Günün özeti: bugün teslim / bugün iade / bakımda araç kartları
- **İstatistik sayfası:** kendi şubesiyle sınırlı ciro/doluluk/talep dağılımı grafikleri (admin sayfasıyla aynı yapıda, şube kıyaslama grafiği hariç)
- Profil bilgilerini düzenleme

### Admin (Operatör)
- Tüm şubelerdeki rezervasyonları liste veya Gantt takviminde görme (kaynak etiketleri: marka/model · plaka · SIPP kodu)
- İstatistik kartları: Aktif Rezervasyon, Bekleyen, Atandı, Araç Filosu
- Tek tıkla greedy optimizasyonu çalıştırma
- Optimizasyon sonuçlarını (skor, atamalar, karşılanamayan rezervasyonlar) inceleme
- **Araç Modelleri (katalog):** marka, model, grup, yakıt, vites, kaporta tipi, çekiş, klima, resim tanımlama; her modelin SIPP kodu (örn. `EDMN`) otomatik hesaplanır
- Araç yönetimi: ekleme, düzenleme, silme (plaka / şasi / katalog modeli / şube / durum — marka/model/grup artık katalogdan otomatik gelir, elle girilmez)
- Araç gerçek zamanlı durum takibi (`current_status`: Müsait / Kiralandı / Bakımda / Serviste)
- Araç geçmişi modalı (rezervasyon + bakım logları)
- Şube yönetimi: ekleme, düzenleme (81 il dropdown)
- Kullanıcı yönetimi: listeleme, rol atama (müşteri / temsilci / admin), şube atama, aktif/pasif toggle
- Şubeler arası transfer ücreti tanımlama ve yönetimi
- Fiyatlandırma: FullCalendar üzerinde **araç modeli** ve tarih aralığı bazlı günlük fiyat tanımlama
- Bakım kayıtları yönetimi
- Teslimat logları görüntüleme
- **İstatistik sayfası:** bu ay ciro, ortalama doluluk, toplam araç kartları; aylık ciro trendi (son 12 ay), günlük doluluk trendi (son 30 gün), şube bazlı doluluk ve araç grubu talep dağılımı grafikleri (ApexCharts, carousel); tarih aralığı ve şube filtreleme

## Araç Kataloğu ve SIPP Kodu

Fiziksel araçlar (`Vehicle`, plaka bazlı) bir **katalog kaydına** (`VehicleModel` — marka, model, yakıt, vites, kaporta tipi, çekiş, klima, resim) bağlanır; aynı marka/model birden fazla plaka arasında paylaşılır. Her katalog kaydının kiralama sektörü standardı **SIPP kodu** (4 karakter: kategori + kaporta tipi + şanzıman/çekiş + yakıt/klima, örn. `EDMN`) `VehicleModel.sipp_code` property'si ile otomatik hesaplanır.

**Araç sınıfı (grup) 9 SIPP kategorisine göre**: Mini / Ekonomi / Kompakt / Orta / Standart / Tam Boyut / Premium / Lüks / Özel (`M`/`E`/`C`/`I`/`S`/`F`/`P`/`L`/`X`). Yükseltme sıralaması M→L doğrusaldır; Özel (`X`) bu zincirin dışındadır, sadece kendisiyle eşleşir ve otomatik yükseltilmez.

**Müşteri/misafir seçim akışı**: rezervasyon sihirbazı Lokasyon → Tarih → **Araç Modeli** sırasıyla ilerler. Tarih seçildikten sonra, o tarih aralığında fiziksel aracı olan modeller (grup/yakıt/vites filtrelenebilir) resimli kartlar halinde, kesin toplam fiyatıyla listelenir; kartta her zaman "ya da eşdeğeri" notu bulunur — seçim **kesin talep değil, yumuşak tercihtir** (`Reservation.preferred_vehicle_model`).

**Overbook / eşleştirme önceliği** (`greedy_solver_güncel.py::score_vehicle`): talep edilen model her zaman öncelenir (skor 0). Müsait değilse sırasıyla: aynı SIPP koduna sahip başka bir marka/model (skor 0.5 — örn. aynı kaporta+şanzıman+yakıt/klima kombinasyonuna sahip iki farklı marka birbirinin yerine geçebilir), aynı sınıftaki (grup) herhangi bir araç (skor 1), üst sınıfa yükseltme (skor 10). Rezervasyon oluşturma anındaki kapasite kontrolü kasıtlı olarak **grup bazlı** kalır (belirli bir plaka kilitlenmez) — asıl model eşleştirmesi atama zamanında yapılır; bu, sistemin bilinçli bir "overbook payı"dır.

**Fiyatlandırma tamamen model bazlıdır** (`DailyPrice.vehicle_model`) — aynı gruptaki farklı modeller farklı günlük fiyata sahip olabilir.

## Araç Teslim / İade Akışı

Temsilci ve admin panelinde rezervasyon detayından açılan, fiziksel imza sürecine uygun **3 aşamalı** bir onay süreci:

| Aşama | `stage` | Açıklama |
|-------|---------|----------|
| 1 | `pending` | KM, yakıt seviyesi, SVG hasar haritası, notlar girilir → belge (imzasız) PDF olarak indirilir |
| 2 | `photo_pending` | Fiziksel olarak imzalanan belge taranıp/fotoğraflanıp sisteme geri yüklenir |
| 3 | `approved` | Aracın son hali fotoğraflanıp yüklenir ve "Teslim Et"/"İade Al" ile süreç onaylanır |

Rezervasyonun/aracın gerçek durumu (KM, hasar haritası güncellemesi, "teslim edildi" sayılması) **yalnızca 3. aşamada** tetiklenir — süreç yarım kalırsa "Teslim İşlemde"/"İade İşlemde" ara rozeti gösterilir. Sayfa yarım kalmış bir süreçle tekrar açılırsa kullanıcı otomatik olarak kaldığı adıma yönlendirilir. İade süreci, ilgili teslimin `approved` durumuna ulaşmasını şart koşar.

**Teslim Formu (`/representative/teslim/:id`)**
- 1. aşama: KM, yakıt seviyesi (kaydırıcı, 1/8 hassasiyet), SVG tabanlı interaktif hasar haritası (13 araç bölgesi, 7 hasar tipi), notlar — aracın son KM'si ve mevcut hasar haritası forma otomatik ön dolu gelir
- 2. aşama: imzalı belge yükleme (PDF, DOCX, JPG, PNG)
- 3. aşama: araç fotoğrafı yükleme (JPG, PNG) + onay

**İade Formu (`/representative/iade/:id`)**
- Sol panel: teslim anındaki KM, yakıt, notlar ve hasar haritası (readonly referans)
- Sağ panel: aynı 3 aşamalı süreç (KM/yakıt/hasar/not → belge → fotoğraf + onay)

**PDF belgeleri** (`/api/reservations/{id}/pdf/{teslim|iade}/`) tek sayfalık, kurumsal bir "tutanak" formatında üretilir — antetli üst bant, KM'nin "kilometre sayacı" gibi gösterildiği ve yakıt seviyesinin segmentli bir gösterge olarak sunulduğu bir bilgi bloğu, SVG hasar haritası + renkli lejant, ve imza satırları içerir. Belge, hangi aşamada indirilirse indirilsin **aynı içeriği** üretir (fiziksel imzalanan kağıtla sistemdeki nihai belge arasında tutarsızlık olmaması için) — araç fotoğrafı bu yüzden PDF'e hiç dahil edilmez, yalnızca sistemde iç kayıt olarak saklanır. KM doğrulama kuralları (teslim KM ≥ aracın mevcut KM'si, iade KM > teslim KM) 1. aşamada uygulanır.

## Optimizasyon Algoritması

Akıllı Greedy algoritması + post-swap iyileştirmesi:

1. Rezervasyonları bitiş tarihine göre sırala (EDF)
2. Her rezervasyon için uygun araçları bul — **yalnızca aynı şubedeki araçlar** adaydır
3. En düşük maliyetli aracı seç — talep edilen model → 0 puan, aynı SIPP koduna sahip farklı marka → 0.5 puan, aynı grup farklı model → 1 puan, farklı grup (upgrade) → 10 puan
4. Transfer maliyeti yalnızca **iade şubesi** farklıysa uygulanır
5. Atama yapılamayan rezervasyonlar için post-swap: mevcut atamaları takasa sokarak yeni slot aç
6. Başlangıç tarihi bugün veya öncesinde olan rezervasyonlar (aktif veya tamamlanmış) kilitlenir — sadece **gelecekteki** rezervasyonlar optimizer tarafından yeniden atanabilir

**Puan sistemi (0-100):**

Skor 100 puandan başlar; algoritmanın kaçırdığı daha iyi seçeneklere göre puan düşer. Segment/statüs/çakışma gibi sert kısıtlar zaten solver tarafından yapısal olarak engellenir (bkz. `validator.py`) — yine de oluşurlarsa ihlal başına sabit **-40** ceza uygulanır. Geri kalan 100 puan, aşağıdaki 6 yumuşak kritere ağırlıklı olarak bölünmüştür:

| Kriter | Açıklama | Ağırlık |
|--------|----------|---------|
| Önlenebilir kayıp | Uygun (müsait, çakışmasız) araç varken karşılanmayan rezervasyon | 35 |
| Önlenebilir upgrade | Aynı şubede tam segment eşleşen araç müsaitken üst gruba atama yapılması | 20 |
| Segment mesafesi | Upgrade'in SIPP kategori mesafesi (Mini→Lüks, Mini→Ekonomi'den daha ağır cezalanır) | 15 |
| Düşük değerli upgrade | Medyan altı fiyatlı veya kısa süreli (3 günden az) rezervasyona pahalı araç verilmesi | 15 |
| Şube verimsizliği | Upgrade yapılan şubelerde atıl müsait araç oranı (transfer dahil değil — iade şubesini müşteri seçer, algoritmanın kontrolünde değildir) | 10 |
| Kaçırılan takas | Aynı şubedeki iki atamanın aracı takas edilseydi toplam ceza azalacaksa | 5 |

Hesaplama: `core/optimizer/objective.py` içindeki `calculate_score()`.

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
│   ├── models.py           # Branch, Vehicle, VehicleModel (katalog + SIPP kodu), Reservation, DeliveryLog (stage/photo dahil), MaintenanceLog, DailyPrice (model bazlı)...
│   ├── constants.py        # SIPP kategori/kaporta tipi sabitleri (SIPP_CATEGORY_CHOICES, SIPP_CATEGORY_RANK, ...)
│   ├── pricing.py          # price_for_range() — model bazlı ortak fiyat hesaplama
│   ├── serializers.py      # current_status, delivery_info, sipp_code dahil tüm serializer'lar
│   ├── views.py            # Tüm API endpoint'leri
│   └── fixtures/
│       └── initial_data.json
├── templates/
│   └── pdfs/
│       ├── teslim_belgesi.html    # xhtml2pdf ile üretilen teslim belgesi
│       └── iade_belgesi.html      # xhtml2pdf ile üretilen iade belgesi
├── media/                  # Yüklenen teslim/iade belgeleri (delivery_docs/), araç kataloğu resimleri (vehicle_models/)
└── frontend/
    └── src/
        ├── assets/
        │   └── cardamage_frame.svg       # SVG hasar haritası çizimi
        ├── components/
        │   └── CarDamageMap.vue          # İnteraktif hasar haritası bileşeni
        ├── constants/
        │   └── sipp.js                    # SIPP kategori etiket/renk/sıralama sabitleri (frontend genelinde paylaşılır)
        ├── layouts/        # AdminLayout, RepresentativeLayout, CustomerLayout
        ├── views/          # Tüm sayfa bileşenleri (AracModelleri.vue — katalog yönetimi, AdminIstatistikleri.vue, RepresentativeIstatistikleri.vue dahil)
        ├── stores/         # auth, optimization (Pinia)
        ├── router/         # Rol tabanlı route koruması
        └── style.css       # Global badge renk standardı (pending/assigned/cancelled/delivered/returned/processing)
```

## API Endpoint'leri

| Method | URL | Açıklama | Yetki |
|--------|-----|----------|-------|
| POST | `/api/login/` | Giriş | Herkese açık |
| POST | `/api/logout/` | Çıkış | Auth |
| POST | `/api/register/` | Müşteri kaydı | Herkese açık |
| GET/PATCH | `/api/profile/` | Profil görüntüle / güncelle | Auth |
| GET/POST/PATCH/DELETE | `/api/branches/` | Şube CRUD | Okuma: Herkese açık, Yazma: Admin |
| GET/POST/PATCH/DELETE | `/api/vehicles/` | Araç CRUD (katalog modeli zorunlu, marka/model/grup oradan senkronlanır) | Okuma: Auth, Yazma: Admin |
| GET/POST/PATCH/DELETE | `/api/vehicle-models/` | Araç kataloğu CRUD — marka/model/yakıt/vites/kaporta/çekiş/klima/resim, SIPP kodu otomatik hesaplanır; `branch`/`group`/`fuel_type`/`transmission`/`start_date`/`end_date` filtreleri | Okuma: Herkese açık, Yazma: Admin |
| GET | `/api/vehicles/{id}/history/` | Araç rezervasyon + bakım geçmişi | Auth |
| GET/POST/DELETE | `/api/reservations/` | Rezervasyon listesi / oluşturma / silme (`preferred_vehicle_model` zorunlu) | Auth |
| POST | `/api/reservations/{reservation_id}/cancel/` | Rezervasyon iptali | Auth |
| POST | `/api/reservations/{id}/deliver/` | Teslim 1. aşama — KM/yakıt/hasar/not kaydı | Temsilci / Admin |
| POST | `/api/reservations/{id}/deliver/document/` | Teslim 2. aşama — imzalı belge yükleme | Temsilci / Admin |
| POST | `/api/reservations/{id}/deliver/photo/` | Teslim 3. aşama — araç fotoğrafı yükleme + onay | Temsilci / Admin |
| POST | `/api/reservations/{id}/return/` | İade 1. aşama — KM/yakıt/hasar/not kaydı | Temsilci / Admin |
| POST | `/api/reservations/{id}/return/document/` | İade 2. aşama — imzalı belge yükleme | Temsilci / Admin |
| POST | `/api/reservations/{id}/return/photo/` | İade 3. aşama — araç fotoğrafı yükleme + onay | Temsilci / Admin |
| GET | `/api/reservations/{id}/pdf/{teslim\|iade}/` | Teslim/iade PDF belgesi indirme | Auth |
| GET | `/api/admin-stats/` | İstatistik verisi (ciro, doluluk, grup dağılımı) — `start`/`end`/`branch` filtreleri | Admin (tüm şubeler) / Temsilci (kendi şubesiyle sınırlı) |
| GET | `/api/availability/` | Şube bazlı müsait günler (şubedeki tüm katalog modelleri taranır) | Herkese açık |
| GET | `/api/transfer-cost/` | İki şube arası transfer ücreti | Auth |
| GET/POST/PATCH/DELETE | `/api/transfer-costs/` | Transfer ücreti CRUD | Admin |
| GET | `/api/daily-prices/` | Günlük fiyat listesi (araç modeli bazlı) | Auth |
| POST | `/api/daily-prices/bulk_set/` | Tarih aralığı + araç modeli bazlı toplu fiyat tanımlama | Admin |
| DELETE | `/api/daily-prices/{id}/` | Fiyat kaydı silme | Admin |
| GET | `/api/delivery-logs/` | Teslimat logları | Temsilci / Admin |
| GET/POST/PATCH/DELETE | `/api/maintenance-logs/` | Bakım kayıtları CRUD | Temsilci / Admin |
| POST | `/api/optimize/` | Optimizasyon çalıştır | Admin |
| GET | `/api/optimize/latest/` | Son optimizasyon sonucu | Admin |
| GET | `/api/users/` | Kullanıcı listesi | Admin / Temsilci |
| POST | `/api/users/create/` | Kullanıcı oluşturma | Admin |
| PATCH | `/api/users/{id}/update/` | Kullanıcı güncelleme | Admin |
| POST | `/api/users/{id}/toggle-active/` | Aktif/pasif toggle | Admin |
| POST | `/api/guest-reservation/` | Misafir rezervasyon oluşturma (`preferred_vehicle_model` zorunlu) | Herkese açık |
| GET | `/api/guest-reservation/query/` | Rezervasyon kodu ile sorgulama (araç, teslim/iade bilgisi dahil) | Herkese açık |
| POST | `/api/guest-reservation/cancel/` | Misafir rezervasyon iptali | Herkese açık |

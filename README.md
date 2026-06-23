# Araç Kiralama Rezervasyon ve Optimizasyon Sistemi

Araç kiralama şirketleri için geliştirilmiş, rezervasyon yönetimi ve filo optimizasyonu sağlayan tam yığın web uygulaması.

## Proje Hakkında

Müşteriler online rezervasyon oluşturur; operatör, greedy optimizasyon algoritması ile araçları rezervasyonlara otomatik atar. Sistem hangi aracın nereye, ne zaman atanacağını transfer maliyetlerini ve araç gruplarını göz önünde bulundurarak hesaplar.

## Teknolojiler

**Backend**
- Python 3 / Django 4
- Django REST Framework (Token tabanlı auth)
- PostgreSQL

**Frontend**
- Vue 3 (Composition API)
- Vite
- Pinia (state management)
- Vue Router
- Axios

## Özellikler

### Müşteri
- Şube ve araç grubu (Ekonomi / Orta Sınıf / SUV) seçerek rezervasyon oluşturma
- Müsait günleri takvim üzerinde görme
- Rezervasyonları listeleme ve iptal etme
- Profil bilgilerini düzenleme (ad soyad, e-posta, telefon, şifre)

### Operatör
- Tüm rezervasyonları liste veya Gantt takviminde görme
- Tek tıkla greedy optimizasyonu çalıştırma
- Optimizasyon sonuçlarını (skor, atamalar, karşılanamayan rezervasyonlar) inceleme
- Araç yönetimi: ekleme, düzenleme, silme (marka/model/plaka/grup/şube/durum)
- Şube yönetimi: ekleme, düzenleme (81 il dropdown)
- Kullanıcı yönetimi: listeleme, aktif/pasif toggle

## Optimizasyon Algoritması

Akıllı Greedy algoritması + post-swap iyileştirmesi:

1. Rezervasyonları bitiş tarihine göre sırala (EDF)
2. Her rezervasyon için uygun araçları bul (grup + müsait + tarih çakışması yok)
3. En düşük maliyetli aracı seç (aynı şube → 0, transfer → gerçek maliyet, upgrade → +10)
4. Atama yapılamayan rezervasyonlar için post-swap: mevcut atamaları takasa sokarak yeni slot aç

**Ceza sistemi:**
| Durum | Puan |
|-------|------|
| Karşılanan rezervasyon | +100 |
| Karşılanamayan rezervasyon | -200 |
| Transfer maliyeti | gerçek maliyet |
| Upgrade | -10 |

## Kurulum

### Gereksinimler
- Python 3.9+
- Node.js 18+

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

### Operatör hesabı oluşturma

```bash
python manage.py createsuperuser
```

## Proje Yapısı

```
├── core/
│   ├── optimizer/
│   │   ├── solvers/
│   │   │   └── greedy_solver_güncel.py   # Ana algoritma
│   │   ├── objective.py                  # Skor hesaplama
│   │   └── validator.py                  # Kısıt kontrolü
│   ├── settings.py
│   └── urls.py
├── vehicles/
│   ├── models.py                         # Branch, Vehicle, Reservation...
│   ├── serializers.py
│   ├── views.py                          # API endpoint'leri
│   └── fixtures/
│       └── initial_data.json             # Test verisi
└── frontend/
    └── src/
        ├── views/                        # Tüm sayfalar
        ├── stores/                       # Pinia store'ları
        └── router/                       # Vue Router
```

## API Endpoint'leri

| Method | URL | Açıklama |
|--------|-----|----------|
| POST | `/api/login/` | Giriş |
| POST | `/api/register/` | Kayıt |
| GET | `/api/branches/` | Şube listesi |
| GET/POST | `/api/vehicles/` | Araç listesi / ekleme |
| GET/POST | `/api/reservations/` | Rezervasyon listesi / oluşturma |
| GET | `/api/availability/` | Müsait günler |
| POST | `/api/optimize/` | Optimizasyon çalıştır |
| GET | `/api/optimize/latest/` | Son optimizasyon sonucu |
| GET/PATCH | `/api/profile/` | Profil görüntüle / güncelle |

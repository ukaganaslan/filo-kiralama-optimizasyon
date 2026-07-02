from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from vehicles.views import BranchViewSet, VehicleViewSet, ReservationViewSet, TransferCostViewSet, optimize, latest_optimization, login_view, logout_view, register_view, availability, cancel_reservation, user_list, toggle_user_active, profile_view, create_user, update_user, transfer_cost_view, guest_reservation, guest_reservation_detail, guest_cancel, delivery_logs, MaintenanceLogViewSet, DailyPriceViewSet, deliver_reservation, deliver_document, deliver_photo, return_reservation, return_document, return_photo, vehicle_history, reservation_pdf, admin_stats

from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()
router.register(r'branches', BranchViewSet)
router.register(r'vehicles', VehicleViewSet)
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'transfer-costs', TransferCostViewSet, basename='transfer-cost')
router.register(r'maintenance-logs', MaintenanceLogViewSet, basename='maintenance-log')
router.register(r'daily-prices', DailyPriceViewSet, basename='daily-price')  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/optimize/', optimize),
    path('api/optimize/latest/', latest_optimization),
    path('api/login/', login_view),
    path('api/logout/', logout_view),
    path('api/register/', register_view),
    path('api/availability/', availability),
    path('api/transfer-cost/', transfer_cost_view),
    path('api/reservations/<str:reservation_id>/cancel/', cancel_reservation),
    path('api/users/', user_list),
    path('api/users/<int:user_id>/toggle-active/', toggle_user_active),
    path('api/profile/', profile_view),
    path('api/users/create/', create_user),
    path('api/users/<int:user_id>/update/', update_user),
    path('api/guest-reservation/', guest_reservation),
    path('api/guest-reservation/query/', guest_reservation_detail),
    path('api/guest-reservation/cancel/', guest_cancel),
    path('api/delivery-logs/', delivery_logs),
    path('api/reservations/<int:pk>/deliver/', deliver_reservation),
    path('api/reservations/<int:pk>/deliver/document/', deliver_document),
    path('api/reservations/<int:pk>/deliver/photo/', deliver_photo),
    path('api/reservations/<int:pk>/return/', return_reservation),
    path('api/reservations/<int:pk>/return/document/', return_document),
    path('api/reservations/<int:pk>/return/photo/', return_photo),
    path('api/vehicles/<str:vehicle_id>/history/', vehicle_history),
    path('api/reservations/<int:pk>/pdf/<str:pdf_type>/', reservation_pdf),
    path('api/admin-stats/', admin_stats),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

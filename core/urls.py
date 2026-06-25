from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from vehicles.views import BranchViewSet, VehicleViewSet, ReservationViewSet, TransferCostViewSet, optimize, latest_optimization, login_view, logout_view, register_view, availability, cancel_reservation, user_list, toggle_user_active, profile_view, create_user, update_user, transfer_cost_view, guest_reservation, guest_reservation_detail, guest_cancel, delivery_logs

router = DefaultRouter()
router.register(r'branches', BranchViewSet)
router.register(r'vehicles', VehicleViewSet)
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'transfer-costs', TransferCostViewSet, basename='transfer-cost')

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
]

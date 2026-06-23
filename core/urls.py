from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from vehicles.views import BranchViewSet, VehicleViewSet, ReservationViewSet, optimize, latest_optimization, login_view, logout_view, register_view, availability, cancel_reservation, user_list, toggle_user_active

router = DefaultRouter()
router.register(r'branches', BranchViewSet)
router.register(r'vehicles', VehicleViewSet)
router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/optimize/', optimize),
    path('api/optimize/latest/', latest_optimization),
    path('api/login/', login_view),
    path('api/logout/', logout_view),
    path('api/register/', register_view),
    path('api/availability/', availability),
    path('api/reservations/<str:reservation_id>/cancel/', cancel_reservation),
    path('api/users/', user_list),
    path('api/users/<int:user_id>/toggle-active/', toggle_user_active),
]

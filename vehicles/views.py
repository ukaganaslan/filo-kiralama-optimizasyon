import json
import re
import uuid
from datetime import date, timedelta
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from io import BytesIO
from xhtml2pdf import pisa

from .models import Branch, Vehicle, Reservation, CustomerProfile, OptimizationRun, AssignmentResult, PenaltyConfig, TransferCost, DeliveryLog, MaintenanceLog, DailyPrice, Assignment
from .serializers import BranchSerializer, VehicleSerializer, ReservationSerializer, TransferCostSerializer, MaintenanceLogSerializer, DailyPriceSerializer
from core.optimizer.solvers import greedy_solver_güncel
from core.optimizer.objective import calculate_score

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class TransferCostViewSet(viewsets.ModelViewSet):
    queryset = TransferCost.objects.select_related('from_branch', 'to_branch').all()
    serializer_class = TransferCostSerializer
    permission_classes = [permissions.IsAdminUser]


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def get_queryset(self):
        _sync_maintenance()
        profile = getattr(self.request.user, 'profile', None)
        if profile and profile.role == 'representative' and profile.branch:
            return Vehicle.objects.filter(branch=profile.branch)
        return Vehicle.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'create']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def perform_update(self, serializer):
        user = self.request.user
        profile = getattr(user, 'profile', None)
        if not user.is_staff and profile and profile.role == 'representative':
            if serializer.instance.branch != profile.branch:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('Bu araca erişim yetkiniz yok.')
            serializer.save(branch=serializer.instance.branch)
        else:
            serializer.save()

    def perform_create(self, serializer):
        from rest_framework.exceptions import PermissionDenied, ValidationError
        from datetime import date
        vehicle = serializer.validated_data.get('vehicle')
        current_km = serializer.validated_data.get('current_km')
        user = self.request.user
        profile = getattr(user, 'profile', None)
        if not user.is_staff and profile and profile.role == 'representative':
            if not profile.branch:
                raise PermissionDenied('Şubeniz tanımlı değil.')
            branch = profile.branch
        else:
            branch = serializer.validated_data.get('branch')
        group = serializer.validated_data.get('group')
        prefix = {'economy': 'E', 'mid': 'M', 'suv': 'S'}.get(group, 'X')
        suffix = 'GEN'
        existing = Vehicle.objects.filter(vehicle_id__startswith=prefix, vehicle_id__endswith=suffix)
        numbers = []
        for v in existing:
            mid = v.vehicle_id[len(prefix):-len(suffix)]
            if mid.isdigit():
                numbers.append(int(mid))
        next_num = max(numbers, default=0) + 1
        vehicle_id = f"{prefix}{next_num:02d}{suffix}"
        serializer.save(vehicle_id=vehicle_id, branch=branch)



class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Reservation.objects.all()
        profile = getattr(user, 'profile', None)
        if profile and profile.role == 'representative':
            return Reservation.objects.filter(branch=profile.branch)
        return Reservation.objects.filter(customer=user)

    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError
        user = self.request.user
        profile = getattr(user, 'profile', None)
        customer = user
        if profile and profile.role in ['representative', 'admin']:
            customer_id = self.request.data.get('customer_id')
            if customer_id:
                try:
                    customer = User.objects.get(id=customer_id)
                except User.DoesNotExist:
                    pass
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')
        overlap = Reservation.objects.filter(
            customer=customer,
            status__in=['pending', 'assigned'],
            start_date__lt=end_date,
            end_date__gt=start_date,
        ).exists()
        if overlap:
            raise ValidationError({'non_field_errors': ['Seçilen tarih aralığında aktif bir rezervasyon var.']})
        reservation_id = 'R' + uuid.uuid4().hex[:6].upper()
        group = serializer.validated_data.get('vehicle_group')
        total_days = (end_date - start_date).days + 1
        prices = {
            p.date: p.price_per_day
            for p in DailyPrice.objects.filter(
                vehicle_group=group,
                date__gte=start_date,
                date__lte=end_date,
            )
        }
        if len(prices) < total_days:
            raise ValidationError({'non_field_errors': ['Seçilen tarih aralığında fiyatlandırılmamış günler var. Lütfen fiyat tanımlı bir aralık seçin.']})
        total = sum(prices.get(start_date + timedelta(days=i), 0)
                    for i in range(total_days))
        save_kwargs = {'customer': customer, 'status': 'pending', 'reservation_id': reservation_id, 'total_price': total or None}
        if profile and profile.role == 'representative' and profile.branch:
            save_kwargs['branch'] = profile.branch
        serializer.save(**save_kwargs)
        _run_optimization()
    
    def perform_update(self, serializer):
        from rest_framework.exceptions import PermissionDenied, ValidationError
        new_status = serializer.validated_data.get('status')
        if new_status and new_status != 'cancelled':
            raise ValidationError('Sadece iptal işlemi yapılabilir.')
        instance = serializer.instance
        profile = getattr(self.request.user, 'profile', None)
        if profile and profile.role == 'representative':
            if instance.branch != profile.branch:
                raise PermissionDenied('Bu rezervasyona erişim yetkiniz yok.')
            if instance.start_date.isoformat() <= date.today().isoformat():
                raise ValidationError('Başlamış rezervasyon iptal edilemez.')
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()
        _run_optimization()

class MaintenanceLogViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return MaintenanceLog.objects.all()
        profile = getattr(user, 'profile', None)
        if profile and profile.role == 'representative' and profile.branch:
            return MaintenanceLog.objects.filter(vehicle__branch=profile.branch)
        if profile and profile.role == 'admin':
            return MaintenanceLog.objects.all()
        return MaintenanceLog.objects.none()

    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError
        vehicle = serializer.validated_data.get('vehicle')
        current_km = serializer.validated_data.get('current_km')

        aktif_atama = AssignmentResult.objects.filter(
            vehicle=vehicle,
            reservation__start_date__lte=date.today(),
            reservation__end_date__gte=date.today(),
            reservation__status='assigned'
        ).exists()
        if aktif_atama:
            raise ValidationError('Bu araç şu an müşteridedir, önce iade alınmalıdır.')

        if current_km < vehicle.total_km:
            raise ValidationError('Girilen KM aracın mevcut KM değerinden düşük olamaz.')
        
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')
        if end_date and end_date < start_date:
            raise ValidationError('Bitiş tarihi başlangıç tarihinden önce olamaz.')

        log = serializer.save()
        log.vehicle.status = 'maintenance'
        log.vehicle.save(update_fields=['status'])

    def perform_update(self, serializer):
        log = serializer.save()
        if log.end_date and log.end_date <= date.today():
            log.vehicle.status = 'available'
            log.vehicle.save(update_fields=['status'])

def _sync_maintenance():
    today = date.today()
    done_logs = MaintenanceLog.objects.filter(
        end_date__lte=today,
        vehicle__status='maintenance',
    ).select_related('vehicle')
    for log in done_logs:
        log.vehicle.status = 'available'
        log.vehicle.save(update_fields=['status'])

def _sync_delivery_logs():
    today = date.today()
    active = Reservation.objects.filter(status='assigned', start_date__lte=today, end_date__gte=today)
    for r in active:
        DeliveryLog.objects.get_or_create(reservation=r, event_type='delivered')
    completed = Reservation.objects.filter(status='assigned', end_date__lt=today)
    for r in completed:
        DeliveryLog.objects.get_or_create(reservation=r, event_type='delivered')
        DeliveryLog.objects.get_or_create(reservation=r, event_type='returned')

def _run_optimization():
    from datetime import date
    today = date.today()
    locked = list(Reservation.objects.filter(
        status='assigned',
        start_date__lte=today,
        end_date__gte=today
    ))
    locked_ids = [r.id for r in locked]
    free = list(Reservation.objects.exclude(status='cancelled').exclude(id__in=locked_ids))
    vehicles = list(Vehicle.objects.all())

    initial_occupied = {}
    for r in locked:
        ar = AssignmentResult.objects.filter(reservation=r).order_by('-run__created_at').first()
        if ar:
            initial_occupied.setdefault(ar.vehicle.vehicle_id, []).append((r.start_date, r.end_date))

    assignments, unassigned = greedy_solver_güncel.solve(free, vehicles, initial_occupied)
    score = calculate_score(assignments, unassigned)

    Reservation.objects.filter(id__in=[r.id for r in free]).update(status='pending')
    for a in assignments:
        a['reservation'].status = 'assigned'
        a['reservation'].save()

    penalty_config = PenaltyConfig.objects.first()
    run = OptimizationRun.objects.create(
        solver='greedy_güncel',
        total_score=score,
        served_count=len(assignments),
        missed_count=len(unassigned),
        penalty_config=penalty_config,
    )
    for a in assignments:
        AssignmentResult.objects.create(
            run=run,
            reservation=a['reservation'],
            vehicle=a['vehicle'],
            transfer_cost=a['transfer_cost'],
            is_upgrade=a['is_upgrade'],
        )
    run.unassigned_reservations.set(unassigned)
    return run, assignments, unassigned

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def optimize(request):
    run, assignments, unassigned = _run_optimization()

    result = _build_result(run, assignments, unassigned)
    return Response(result)


def _build_result(run, assignments, unassigned):
    return {
        'score': run.total_score,
        'fulfilled': run.served_count,
        'unfulfilled': run.missed_count,
        'run_id': run.id,
        'created_at': run.created_at.strftime('%Y-%m-%d %H:%M'),
        'assignments': [
            {
                'reservation_id': a['reservation'].reservation_id,
                'customer_username': a['reservation'].customer.username if a['reservation'].customer else None,
                'guest_name': a['reservation'].guest_name,
                'vehicle_id': a['vehicle'].vehicle_id,
                'start_date': str(a['reservation'].start_date),
                'end_date': str(a['reservation'].end_date),
                'transfer_cost': a['transfer_cost'],
                'is_upgrade': a['is_upgrade'],
            }
            for a in assignments
        ],
        'unassigned': [
            {
                'reservation_id': r.reservation_id,
                'customer_username': r.customer.username if r.customer else None,
                'start_date': str(r.start_date),
                'end_date': str(r.end_date),
                'vehicle_group': r.vehicle_group,
                'branch_name': r.branch.name,
            }
            for r in unassigned
        ],
    }


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def latest_optimization(request):
    run = OptimizationRun.objects.order_by('-created_at').first()
    if not run:
        return Response(None)

    assignment_results = run.results.select_related('reservation', 'reservation__customer', 'vehicle', 'reservation__branch')
    unassigned_reservations = run.unassigned_reservations.select_related('customer', 'branch')

    assignments = [
        {
            'reservation_id': ar.reservation.reservation_id,
            'customer_username': ar.reservation.customer.username if ar.reservation.customer else None,
            'guest_name': ar.reservation.guest_name,
            'vehicle_id': ar.vehicle.vehicle_id,
            'start_date': str(ar.reservation.start_date),
            'end_date': str(ar.reservation.end_date),
            'transfer_cost': ar.transfer_cost,
            'is_upgrade': ar.is_upgrade,
        }
        for ar in assignment_results
    ]
    unassigned = [
        {
            'reservation_id': r.reservation_id,
            'customer_username': r.customer.username if r.customer else None,
            'start_date': str(r.start_date),
            'end_date': str(r.end_date),
            'vehicle_group': r.vehicle_group,
            'branch_name': r.branch.name,
        }
        for r in unassigned_reservations
    ]

    return Response({
        'score': run.total_score,
        'fulfilled': run.served_count,
        'unfulfilled': run.missed_count,
        'run_id': run.id,
        'created_at': run.created_at.strftime('%Y-%m-%d %H:%M'),
        'assignments': assignments,
        'unassigned': unassigned,
    })

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def transfer_cost_view(request):
    from_id = request.query_params.get('from')
    to_id = request.query_params.get('to')
    if not from_id or not to_id or str(from_id) == str(to_id):
        return Response({'cost': 0})
    from .models import TransferCost
    try:
        tc = TransferCost.objects.get(from_branch_id=from_id, to_branch_id=to_id)
    except TransferCost.DoesNotExist:
        try:
            tc = TransferCost.objects.get(from_branch_id=to_id, to_branch_id=from_id)
        except TransferCost.DoesNotExist:
            return Response({'cost': None})
    return Response({'cost': str(tc.cost)})

@api_view(['GET'])
def availability(request):
    branch_id = request.query_params.get('branch')
    group = request.query_params.get('group')

    if not branch_id or not group:
        return Response({'error': 'branch ve group gerekli'}, status=400)

    toplam = Vehicle.objects.filter(
        branch_id=branch_id, group=group, status='available'
    ).count()

    bugun = date.today()
    musait_gunler = []
    fiyatli_gunler = set(
        DailyPrice.objects.filter(
            vehicle_group=group,
            date__gte=bugun,
            date__lt=bugun + timedelta(days=90)
        ).values_list('date', flat=True)
    )

    for i in range(90):
        gun = bugun + timedelta(days=i)
        if gun not in fiyatli_gunler:
            continue
        dolu = Reservation.objects.filter(
            branch_id=branch_id,
            vehicle_group=group,
            status__in=['pending', 'assigned'],
            start_date__lte=gun,
            end_date__gte=gun
        ).count()
        if dolu < toplam:
            musait_gunler.append(str(gun))

    return Response({'available_dates': musait_gunler})


@api_view(['POST'])
def cancel_reservation(request, reservation_id):
    try:
        reservation = Reservation.objects.get(reservation_id=reservation_id, customer=request.user)
    except Reservation.DoesNotExist:
        return Response({'error': 'Rezervasyon bulunamadı'}, status=404)
    from datetime import date
    if reservation.start_date <= date.today():
        return Response({'error': 'Başlamış rezervasyon iptal edilemez'}, status=400)
    reservation.status = 'cancelled'
    reservation.save()
    return Response({'message': 'Rezervasyon iptal edildi'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_user(request):
    if not request.user.is_staff:
        return Response({'error': 'Yetkisiz'}, status=403)
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    full_name = request.data.get('full_name', '')
    phone = request.data.get('phone', '')
    if not username or not password:
        return Response({'error': 'Kullanıcı adı ve şifre zorunlu'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Bu kullanıcı adı alınmış'}, status=400)
    role = request.data.get('role', 'customer')
    branch_id = request.data.get('branch', None)
    if role not in ['customer', 'representative', 'admin']:
        return Response({'error': 'Geçersiz rol'}, status=400)
    user = User.objects.create_user(username=username, password=password, email=email)
    if role == 'admin':
        user.is_staff = True
        user.save()
    profile = CustomerProfile.objects.create(user=user, full_name=full_name, phone=phone, role=role)
    if branch_id and role == 'representative':
        try:
            profile.branch = Branch.objects.get(id=branch_id)
            profile.save()
        except Branch.DoesNotExist:
            pass
    return Response({'id': user.id, 'username': user.username, 'role': role}, status=201)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_user(request, user_id):
    if not request.user.is_staff:
        return Response({'error': 'Yetkisiz'}, status=403)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Kullanıcı bulunamadı'}, status=404)
    data = request.data
    if 'username' in data and data['username']:
        if User.objects.exclude(pk=user.pk).filter(username=data['username']).exists():
            return Response({'error': 'Bu kullanıcı adı alınmış'}, status=400)
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    user.save()
    profile = getattr(user, 'profile', None)
    if not profile:
        profile = CustomerProfile.objects.create(user=user)
    if 'full_name' in data:
        profile.full_name = data['full_name']
    if 'phone' in data:
        profile.phone = data['phone']
    if 'role' in data and data['role'] in ['customer', 'representative', 'admin']:
        profile.role = data['role']
        if data['role'] == 'admin':
            user.is_staff = True
            user.save()
        elif user.is_staff:
            user.is_staff = False
            user.save()
    if 'branch_id' in data:
        try:
            profile.branch = Branch.objects.get(id=data['branch_id']) if data['branch_id'] else None
        except Branch.DoesNotExist:
            pass
    profile.save()
    return Response({'message': 'Kullanıcı güncellendi'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_list(request):
    profile = getattr(request.user, 'profile', None)
    is_representative = profile and profile.role == 'representative'
    if not request.user.is_staff and not is_representative:
        return Response({'error': 'Yetkisiz'}, status=403)
    if is_representative:
        users = User.objects.filter(is_superuser=False, profile__role='customer').select_related('profile')
    else:
        users = User.objects.filter(is_superuser=False).select_related('profile')
    data = []
    for u in users:
        profile = getattr(u, 'profile', None)
        data.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'full_name': profile.full_name if profile else '',
            'phone': profile.phone if profile else '',
            'role': profile.role if profile else 'customer',
            'branch_id': profile.branch_id if profile else None,
            'reservation_count': u.reservations.count(),
            'date_joined': u.date_joined.strftime('%Y-%m-%d'),
            'is_active': u.is_active,
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_user_active(request, user_id):
    if not request.user.is_staff:
        return Response({'error': 'Yetkisiz'}, status=403)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Kullanıcı bulunamadı'}, status=404)
    user.is_active = not user.is_active
    user.save()
    return Response({'is_active': user.is_active})


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    if request.method == 'GET':
        return Response({
            'username': user.username,
            'email': user.email,
            'full_name': profile.full_name if profile else '',
            'phone': profile.phone if profile else '',
            'role': profile.role if profile else ('admin' if user.is_staff else 'customer'),
            'branch_id': profile.branch_id if profile else None,
        })
    data = request.data
    if 'username' in data and data['username']:
        if User.objects.exclude(pk=user.pk).filter(username=data['username']).exists():
            return Response({'error': 'Bu kullanıcı adı alınmış'}, status=400)
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'full_name' in data or 'phone' in data:
        if not profile:
            profile = CustomerProfile.objects.create(user=user)
        if 'full_name' in data:
            profile.full_name = data['full_name']
        if 'phone' in data:
            profile.phone = data['phone']
        profile.save()
    new_token = None
    if 'new_password' in data and data['new_password']:
        user.set_password(data['new_password'])
        user.auth_token.delete()
        new_token = Token.objects.create(user=user).key
    user.save()
    response = {'message': 'Profil güncellendi'}
    if new_token:
        response['token'] = new_token
    return Response(response)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Kullanıcı adı veya şifre yanlış'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token, _ = Token.objects.get_or_create(user=user)
    profile = getattr(user, 'profile', None)
    if user.is_staff:
        role = 'admin'
    elif profile:
        role = profile.role
    else:
        role = 'customer'
    return Response({
        'token': token.key,
        'username': user.username,
        'role': role,
    })

@api_view(['POST'])
def logout_view(request):
    if request.user.is_authenticated:
        request.user.auth_token.delete()
    return Response({'message': 'Çıkış Yapıldı'})

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def guest_reservation(request):
    guest_name = request.data.get('guest_name')
    guest_phone = request.data.get('guest_phone', '')
    guest_email = request.data.get('guest_email')
    branch_id = request.data.get('branch')
    vehicle_group = request.data.get('vehicle_group')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')

    if not all([guest_name, guest_email, branch_id, vehicle_group, start_date, end_date]):
        return Response({'error': 'Tüm alanları doldurun'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        return Response({'error': 'Şube bulunamadı'}, status=status.HTTP_400_BAD_REQUEST)

    reservation_id = 'G' + uuid.uuid4().hex[:7].upper()

    from datetime import datetime
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end   = datetime.strptime(end_date,   '%Y-%m-%d').date()
    total_days = (end - start).days + 1
    prices = {
        p.date: p.price_per_day
        for p in DailyPrice.objects.filter(
            vehicle_group=vehicle_group,
            date__gte=start,
            date__lte=end,
        )
    }
    if len(prices) < total_days:
        return Response({'error': 'Seçilen tarih aralığında fiyatlandırılmamış günler var. Lütfen fiyat tanımlı bir aralık seçin.'}, status=status.HTTP_400_BAD_REQUEST)
    total = sum(prices.get(start + timedelta(days=i), 0)
                for i in range(total_days))

    return_branch_id = request.data.get('return_branch')
    return_branch = None
    if return_branch_id and str(return_branch_id) != str(branch_id):
        try:
            return_branch = Branch.objects.get(id=return_branch_id)
        except Branch.DoesNotExist:
            pass

    reservation = Reservation.objects.create(
        reservation_id=reservation_id,
        customer=None,
        guest_name=guest_name,
        guest_phone=guest_phone,
        guest_email=guest_email,
        branch=branch,
        return_branch=return_branch,
        vehicle_group=vehicle_group,
        start_date=start_date,
        end_date=end_date,
        status='pending',
        total_price=total or None,
    )

    _run_optimization()

    return Response({
        'code': reservation.reservation_id[:8].upper(),
        'message': 'Rezervasyonunuz alındı.',
        'total_price': str(reservation.total_price) if reservation.total_price else None,
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    full_name = request.data.get('full_name', '')
    phone = request.data.get('phone', '')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Bu kullanıcı adı alınmış'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, email=email)
    CustomerProfile.objects.create(user=user, full_name=full_name, phone=phone, role='customer')

    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'username': user.username,
        'role': 'customer',
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def guest_reservation_detail(request):
    code = request.query_params.get('code', '').strip().upper()
    if not code:
        return Response({'error': 'Kod gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    reservation = Reservation.objects.filter(
        reservation_id__istartswith=code,
        customer=None,
    ).first()

    if not reservation:
        return Response({'error': 'Rezervasyon bulunamadı'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'reservation_id': reservation.reservation_id,
        'code': reservation.reservation_id[:8].upper(),
        'guest_name': reservation.guest_name,
        'branch': reservation.branch.title or reservation.branch.name,
        'vehicle_group': reservation.vehicle_group,
        'start_date': str(reservation.start_date),
        'end_date': str(reservation.end_date),
        'status': reservation.status,
        'total_price': str(reservation.total_price) if reservation.total_price else None,
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def guest_cancel(request):
    code = request.data.get('code', '').strip().upper()
    email = request.data.get('email', '').strip().lower()

    if not code or not email:
        return Response({'error': 'Kod ve e-posta gerekli'}, status=status.HTTP_400_BAD_REQUEST)

    reservation = Reservation.objects.filter(
        reservation_id__istartswith=code,
        customer=None,
        guest_email__iexact=email,
    ).first()

    if not reservation:
        return Response({'error': 'Rezervasyon bulunamadı'}, status=status.HTTP_404_NOT_FOUND)

    if reservation.status == 'cancelled':
        return Response({'error': 'Bu rezervasyon zaten iptal edilmiş'}, status=status.HTTP_400_BAD_REQUEST)

    reservation.status = 'cancelled'
    reservation.save()
    return Response({'message': 'Rezervasyon iptal edildi'})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def delivery_logs(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    if user.is_staff:
        logs = DeliveryLog.objects.select_related(
            'reservation', 'reservation__branch', 'reservation__customer'
        ).order_by('-logged_at')
    elif profile and profile.role == 'representative' and profile.branch:
        logs = DeliveryLog.objects.filter(
            reservation__branch=profile.branch
        ).select_related(
            'reservation', 'reservation__branch', 'reservation__customer'
        ).order_by('-logged_at')
    else:
        return Response({'error': 'Yetkisiz'}, status=403)

    data = []
    for log in logs:
        result = log.reservation.assignmentresult_set.order_by('-run__created_at').first()
        plate = result.vehicle.plate if result else None
        data.append({
            'reservation_id': log.reservation.reservation_id,
            'branch_name': log.reservation.branch.title or log.reservation.branch.name,
            'vehicle_group': log.reservation.vehicle_group,
            'customer': log.reservation.customer.username if log.reservation.customer else log.reservation.guest_name,
            'start_date': log.reservation.start_date,
            'end_date': log.reservation.end_date,
            'event_type': log.event_type,
            'logged_at': log.logged_at,
            'assigned_vehicle_plate': plate,
            'total_price': log.reservation.total_price,
        })

    return Response(data)

class DailyPriceViewSet(viewsets.ModelViewSet):
    serializer_class = DailyPriceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = DailyPrice.objects.all()
        group = self.request.query_params.get('group')
        if group:
            qs = qs.filter(vehicle_group=group)
        return qs

    @action(detail=False, methods=['post'])
    def bulk_set(self, request):
        from rest_framework.exceptions import ValidationError
        start = request.data.get('start_date')
        end = request.data.get('end_date')
        group = request.data.get('vehicle_group')
        price = request.data.get('price_per_day')
        if not all([start, end, group, price]):
            raise ValidationError('Tüm alanlar gerekli.')
        start_d = date.fromisoformat(start)
        end_d = date.fromisoformat(end)
        current = start_d
        while current <= end_d:
            DailyPrice.objects.update_or_create(
                date=current,
                vehicle_group=group,
                defaults={'price_per_day': price}
            )
            current += timedelta(days=1)
        return Response({'ok': True})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def deliver_reservation(request, pk):
    profile = getattr(request.user, 'profile', None)
    try:
        reservation = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:
        return Response({'error': 'Rezervasyon bulunamadı'}, status=404)
    if profile and profile.role == 'representative' and reservation.branch != profile.branch:
        return Response({'error': 'Yetkisiz'}, status=403)
    if reservation.status != 'assigned':
        return Response({'error': 'Rezervasyon onaylı değil'}, status=400)
    deliver_km = request.data.get('delivery_km')
    if deliver_km:
        assignment = AssignmentResult.objects.filter(reservation=reservation).order_by('-id').first()
        if assignment and assignment.vehicle and int(deliver_km) < assignment.vehicle.total_km:
            return Response({'error': f'Teslim KM ({deliver_km}), aracın mevcut KM\'sinden ({assignment.vehicle.total_km}) az olamaz'}, status=400)
    log, _ = DeliveryLog.objects.get_or_create(reservation=reservation, event_type='delivered')
    if 'document' in request.FILES:
        log.document = request.FILES['document']
    if deliver_km:
        log.delivery_km = deliver_km
    if request.data.get('fuel_level') is not None:
        log.fuel_level = request.data['fuel_level']
    if request.data.get('damage_items'):
        import json
        log.damage_items = json.loads(request.data['damage_items']) if isinstance(request.data['damage_items'], str) else request.data['damage_items']
    if request.data.get('notes'):
        log.notes = request.data['notes']
    log.save()
    return Response({'ok': True})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def return_reservation(request, pk):
    profile = getattr(request.user, 'profile', None)
    try:
        reservation = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:
        return Response({'error': 'Rezervasyon bulunamadı'}, status=404)
    if profile and profile.role == 'representative' and reservation.branch != profile.branch:
        return Response({'error': 'Yetkisiz'}, status=403)
    delivered_log = DeliveryLog.objects.filter(reservation=reservation, event_type='delivered').first()
    if not delivered_log:
        return Response({'error': 'Önce teslim işlemi yapılmalı'}, status=400)
    return_km = request.data.get('delivery_km')
    if return_km and delivered_log.delivery_km:
        if int(return_km) <= int(delivered_log.delivery_km):
            return Response({'error': f'İade KM ({return_km}), teslim KM\'sinden ({delivered_log.delivery_km}) büyük olmalı'}, status=400)
    log, _ = DeliveryLog.objects.get_or_create(reservation=reservation, event_type='returned')
    if 'document' in request.FILES:
        log.document = request.FILES['document']
    if request.data.get('delivery_km'):
        log.delivery_km = request.data['delivery_km']
    if request.data.get('fuel_level') is not None:
        log.fuel_level = request.data['fuel_level']
    if request.data.get('damage_items'):
        import json
        log.damage_items = json.loads(request.data['damage_items']) if isinstance(request.data['damage_items'], str) else request.data['damage_items']
    if request.data.get('notes'):
        log.notes = request.data['notes']
    log.save()
    if request.data.get('delivery_km'):
        assignment = AssignmentResult.objects.filter(reservation=reservation).order_by('-id').first()
        if assignment and assignment.vehicle:
            assignment.vehicle.total_km = int(request.data['delivery_km'])
            assignment.vehicle.damage_map = json.loads(request.data.get('damage_items', '{}'))
            assignment.vehicle.save(update_fields=['total_km', 'damage_map'])
    return Response({'ok': True})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def vehicle_history (request, vehicle_id):
    try:
        vehicle = Vehicle.objects.get(vehicle_id=vehicle_id)
    except Vehicle.DoesNotExist:
        return Response({'error': 'Araç bulunamadı'}, status=404)

    profile = getattr(request.user, 'profile', None)
    if profile and profile.role not in ('admin', 'representative'):
        return Response({'error': 'Yetkisiz'}, status=403)
    from django.db.models import OuterRef, Subquery
    latest_ar_id = AssignmentResult.objects.filter(
        reservation=OuterRef('reservation_id')
    ).order_by('-run__created_at').values('id')[:1]

    current_results = AssignmentResult.objects.filter(
        id=Subquery(latest_ar_id),
        vehicle=vehicle,
    ).select_related(
        'reservation', 'reservation__customer', 'reservation__customer__profile'
    ).prefetch_related('reservation__delivery_logs').order_by('-reservation__start_date')

    reservations = []
    for ar in current_results:
        r = ar.reservation
        logs = {log.event_type: log for log in r.delivery_logs.all()}
        delivered = logs.get('delivered')
        returned = logs.get('returned')
        reservations.append({
            'reservation_id': r.reservation_id,
            'start_date': r.start_date,
            'end_date': r.end_date,
            'status': r.status,
            'total_price': r.total_price,
            'customer_name': (
                r.customer.profile.full_name if r.customer and hasattr(r.customer, 'profile') else r.guest_name or '-'
            ),
            'delivered_km': delivered.delivery_km if delivered else None,
            'returned_km': returned.delivery_km if returned else None,
        })

    logs = vehicle.maintenance_logs.order_by('-start_date').values(
        'reason', 'start_date', 'end_date', 'current_km', 'notes'
    )

    return Response({
        'vehicle_id': vehicle.vehicle_id,
        'brand': vehicle.brand,
        'model': vehicle.model,
        'plate': vehicle.plate,
        'group': vehicle.group,
        'total_km': vehicle.total_km,
        'reservations': reservations,
        'maintenance_logs': list(logs),
    })


FUEL_LABELS = {0: 'E', 1: '1/8', 2: '1/4', 3: '3/8', 4: '1/2', 5: '5/8', 6: '3/4', 7: '7/8', 8: 'F'}

DAMAGE_STATES = {
    1: ('Sürtme',  '#fef9c3'),
    2: ('Göçük',   '#fed7aa'),
    3: ('Çizik',   '#fecaca'),
    4: ('Leke',    '#dbeafe'),
    5: ('Çatlak',  '#e9d5ff'),
    6: ('Eksik',   '#fda4af'),
}

CAR_PART_LABELS = {
    'on_tampon':         'Ön Tampon',
    'kaput':             'Kaput',
    'on_sol_camurluk':   'Ön Sol Çamurluk',
    'on_sag_camurluk':   'Ön Sağ Çamurluk',
    'on_sol_kapi':       'Ön Sol Kapı',
    'tavan':             'Tavan',
    'on_sag_kapi':       'Ön Sağ Kapı',
    'arka_sol_kapi':     'Arka Sol Kapı',
    'arka_sag_kapi':     'Arka Sağ Kapı',
    'arka_sol_camurluk': 'Arka Sol Çamurluk',
    'bagaj':             'Bagaj',
    'arka_sag_camurluk': 'Arka Sağ Çamurluk',
    'arka_tampon':       'Arka Tampon',
}


def build_damage_list(damage_items):
    if not damage_items:
        return []
    result = []
    for part_id, state in damage_items.items():
        if state and state > 0 and state in DAMAGE_STATES:
            label = CAR_PART_LABELS.get(part_id, part_id)
            state_label, color = DAMAGE_STATES[state]
            result.append({'label': label, 'state': state_label, 'color': color})
    return result


SVG_PATH = str(settings.BASE_DIR / 'static' / 'damage' /  'cardamage_frame.svg')
CARDAMAGE_PNG_PATH = str(settings.BASE_DIR / 'static' / 'damage' / 'cardamage.png')


def build_damage_svg(damage_items):
    import base64
    try:
        with open(SVG_PATH, 'r', encoding='utf-8') as f:
            svg = f.read()
    except FileNotFoundError:
        return ''
    svg = re.sub(r'width="387"', 'width="193"', svg)
    svg = re.sub(r'height="516"', 'height="258"', svg)
    # defs bloğunu (bozuk JPEG pattern) ve arka plan rect'ini kaldır
    svg = re.sub(r'<defs>.*?</defs>', '', svg, flags=re.DOTALL)
    svg = re.sub(r'<rect[^>]*fill="url\(#[^"]+\)"[^/]*/>', '', svg)
    # cardamage.png'yi SVG <image> olarak en alta ekle (paths üstte kalır)
    try:
        with open(CARDAMAGE_PNG_PATH, 'rb') as f:
            png_b64 = base64.b64encode(f.read()).decode()
        png_tag = f'<image href="data:image/png;base64,{png_b64}" x="0" y="0" width="387" height="516"/>'
        svg = re.sub(r'(<svg[^>]*>)', rf'\1{png_tag}', svg)
    except Exception:
        pass
    for part_id in CAR_PART_LABELS:
        state = (damage_items or {}).get(part_id, 0)
        color = DAMAGE_STATES.get(state, (None, '#f1f5f9'))[1]
        svg = re.sub(
            rf'(id="{part_id}")',
            rf'\1 fill="{color}" fill-opacity="0.6"',
            svg
        )
    b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f'<img src="data:image/svg+xml;base64,{b64}" width="193" height="258" />'


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def reservation_pdf(request, pk, pdf_type):
    try:
        reservation = Reservation.objects.select_related(
            'branch', 'customer', 'customer__profile'
        ).prefetch_related('delivery_logs').get(pk=pk)
    except Reservation.DoesNotExist:
        return HttpResponse(status=404)

    logs = {log.event_type: log for log in reservation.delivery_logs.all()}
    delivered = logs.get('delivered')
    returned = logs.get('returned')

    def make_photo(log):
        import base64
        if log and log.document:
            try:
                with open(log.document.path, 'rb') as f:
                    ext = log.document.name.split('.')[-1]
                    return f'data:image/{ext};base64,{base64.b64encode(f.read()).decode()}'
            except Exception:
                pass
        return None

    delivered_photo = make_photo(delivered)
    returned_photo = make_photo(returned)


    ar = AssignmentResult.objects.filter(reservation=reservation).order_by('-run__created_at').first()
    vehicle = ar.vehicle if ar else None

    customer_name = (
        reservation.customer.profile.full_name
        if reservation.customer and hasattr(reservation.customer, 'profile')
        else reservation.guest_name or '—'
    )

    def fuel_pct(val):
        return round((val / 8) * 100) if val is not None else 0

    if pdf_type == 'teslim':
        if not delivered:
            return HttpResponse('Teslim kaydı bulunamadı.', status=400)
        context = {
            'reservation_id': reservation.reservation_id,
            'branch_name': reservation.branch.name,
            'customer_name': customer_name,
            'brand': vehicle.brand if vehicle else '—',
            'model': vehicle.model if vehicle else '—',
            'plate': vehicle.plate if vehicle else '—',
            'start_date': reservation.start_date,
            'end_date': reservation.end_date,
            'delivered_at': delivered.logged_at.strftime('%d.%m.%Y %H:%M'),
            'delivered_km': delivered.delivery_km,
            'fuel_label': FUEL_LABELS.get(delivered.fuel_level, '—'),
            'fuel_pct': fuel_pct(delivered.fuel_level),
            'damage_list': build_damage_list(delivered.damage_items),
            'damage_svg': build_damage_svg(delivered.damage_items),
            'delivered_notes': delivered.notes,
            'photo': delivered_photo,
        }
        template = 'pdfs/teslim_belgesi.html'
        filename = f'teslim-{reservation.reservation_id}.pdf'

    elif pdf_type == 'iade':
        if not returned:
            return HttpResponse('İade kaydı bulunamadı.', status=400)
        km_diff = None
        if returned.delivery_km and delivered and delivered.delivery_km:
            km_diff = returned.delivery_km - delivered.delivery_km
        context = {
            'reservation_id': reservation.reservation_id,
            'branch_name': reservation.branch.name,
            'customer_name': customer_name,
            'brand': vehicle.brand if vehicle else '—',
            'model': vehicle.model if vehicle else '—',
            'plate': vehicle.plate if vehicle else '—',
            'start_date': reservation.start_date,
            'end_date': reservation.end_date,
            'returned_at': returned.logged_at.strftime('%d.%m.%Y %H:%M'),
            'delivered_km': delivered.delivery_km if delivered else None,
            'returned_km': returned.delivery_km,
            'km_diff': km_diff,
            'delivered_fuel_label': FUEL_LABELS.get(delivered.fuel_level if delivered else None, '—'),
            'delivered_fuel_pct': fuel_pct(delivered.fuel_level if delivered else None),
            'returned_fuel_label': FUEL_LABELS.get(returned.fuel_level, '—'),
            'returned_fuel_pct': fuel_pct(returned.fuel_level),
            'delivered_damage_list': build_damage_list(delivered.damage_items if delivered else {}),
            'delivered_damage_svg': build_damage_svg(delivered.damage_items if delivered else {}),
            'returned_damage_list': build_damage_list(returned.damage_items),
            'returned_damage_svg': build_damage_svg(returned.damage_items),
            'returned_notes': returned.notes,
            'delivered_photo': delivered_photo,
            'returned_photo': returned_photo,
        }
        template = 'pdfs/iade_belgesi.html'
        filename = f'iade-{reservation.reservation_id}.pdf'

    else:
        return HttpResponse('Geçersiz belge tipi.', status=400)

    html_string = render_to_string(template, context)
    buffer = BytesIO()
    pisa.CreatePDF(html_string, dest=buffer, encoding='utf-8')
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_stats(request):
    from django.db.models import Sum, Count

    today = date.today()

    try:
        group_start = date.fromisoformat(request.GET['start'])
        group_end = date.fromisoformat(request.GET['end'])
    except (KeyError, ValueError):
        group_start, group_end = today.replace(day=1), today

    if group_end < group_start:
        group_start, group_end = group_end, group_start

    this_month_revenue = Reservation.objects.filter(
        start_date__year=today.year, start_date__month=today.month
    ).exclude(status='cancelled').aggregate(total=Sum('total_price'))['total'] or 0

    # Son 12 ayın aylık ciro trendi
    from django.db.models.functions import TruncMonth

    trend_start = today.replace(day=1)
    for _ in range(11):
        trend_start = (trend_start - timedelta(days=1)).replace(day=1)

    monthly_totals = {
        r['month']: r['total']
        for r in Reservation.objects.exclude(status='cancelled')
        .filter(start_date__gte=trend_start)
        .annotate(month=TruncMonth('start_date'))
        .values('month')
        .annotate(total=Sum('total_price'))
    }

    monthly_revenue = []
    m = trend_start
    while m <= today:
        monthly_revenue.append({'month': m.isoformat()[:7], 'total': monthly_totals.get(m, 0)})
        m = date(m.year + (m.month == 12), m.month % 12 + 1, 1)

    # Son 30 günün günlük doluluk oranı — her rezervasyon için en güncel run'ın ataması geçerli
    window_start = today - timedelta(days=29)
    total_vehicle_count = Vehicle.objects.count()

    overlapping = (
        AssignmentResult.objects
        .filter(
            reservation__status='assigned',
            reservation__start_date__lte=today,
            reservation__end_date__gte=window_start,
        )
        .order_by('run_id')
        .values('reservation_id', 'vehicle_id', 'reservation__start_date', 'reservation__end_date')
    )
    latest_assignments = {r['reservation_id']: r for r in overlapping}

    daily_occupancy = []
    for i in range(30):
        d = window_start + timedelta(days=i)
        busy = {
            r['vehicle_id'] for r in latest_assignments.values()
            if r['reservation__start_date'] <= d <= r['reservation__end_date']
        }
        pct = round(len(busy) / total_vehicle_count * 100) if total_vehicle_count else 0
        daily_occupancy.append({'date': d.isoformat(), 'occupancy': pct})

    branches = Branch.objects.all()
    branch_stats = []
    for b in branches:
        total = Vehicle.objects.filter(branch=b).count()
        active = AssignmentResult.objects.filter(vehicle__branch=b, reservation__start_date__lte=today, reservation__end_date__gte=today, reservation__status="assigned").values('vehicle').distinct().count()
        branch_stats.append({'name': str(b), 'total': total, 'active': active})
    
    group_dist = list(
        Reservation.objects.exclude(status='cancelled')
        .filter(start_date__gte=group_start, start_date__lte=group_end)
        .values('vehicle_group')
        .annotate(count=Count('id'))
        .order_by('vehicle_group')
    )

    return Response({
        'group_start': group_start.isoformat(),
        'group_end': group_end.isoformat(),
        'this_month': this_month_revenue,
        'monthly_revenue': monthly_revenue,
        'daily_occupancy': daily_occupancy,
        'branches': branch_stats,
        'groups': group_dist,
    })
    
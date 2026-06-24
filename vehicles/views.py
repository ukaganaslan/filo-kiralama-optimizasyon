import uuid
from datetime import date, timedelta
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import Branch, Vehicle, Reservation, CustomerProfile, OptimizationRun, AssignmentResult, PenaltyConfig, TransferCost
from .serializers import BranchSerializer, VehicleSerializer, ReservationSerializer, TransferCostSerializer
from core.optimizer.solvers import greedy_solver_güncel
from core.optimizer.objective import calculate_score

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]


class TransferCostViewSet(viewsets.ModelViewSet):
    queryset = TransferCost.objects.select_related('from_branch', 'to_branch').all()
    serializer_class = TransferCostSerializer
    permission_classes = [permissions.IsAdminUser]


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if profile and profile.role == 'representative' and profile.branch:
            return Vehicle.objects.filter(branch=profile.branch)
        return Vehicle.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update']:
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
        serializer.save(vehicle_id=vehicle_id)


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
        save_kwargs = {'customer': customer, 'status': 'pending', 'reservation_id': reservation_id}
        if profile and profile.role == 'representative' and profile.branch:
            save_kwargs['branch'] = profile.branch
        serializer.save(**save_kwargs)
        _run_optimization()

def _run_optimization():
    reservations = list(Reservation.objects.exclude(status='cancelled'))
    vehicles = list(Vehicle.objects.all())

    assignments, unassigned = greedy_solver_güncel.solve(reservations, vehicles)
    score = calculate_score(assignments, unassigned, vehicles)

    Reservation.objects.exclude(status='cancelled').update(status='pending')
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
@permission_classes([permissions.IsAuthenticated])
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

    for i in range(90):
        gun = bugun + timedelta(days=i)
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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User

@api_view(['POST'])
def login_view(request):
    tr_number = request.data.get('trNumber')
    password = request.data.get('password')

    user = authenticate(request, tr_number=tr_number, password=password)
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=401)

    refresh = RefreshToken.for_user(user)
    return Response({'token': str(refresh.access_token)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    user = request.user
    return Response({
        'tr_number': user.tr_number,
        'role': user.role,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'its_number': user.its_number,
        'class_name': user.class_name,
        'hizb': user.hizb,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_users_view(request):
    users = User.objects.all().values('tr_number', 'first_name', 'last_name', 'role')
    return Response(list(users))

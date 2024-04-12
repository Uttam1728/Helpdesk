from django.contrib.auth import authenticate
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from common.constants import UserRole, CommonConstants
from user_accounts.models import Account
from user_accounts.serializer import AccountWriteSerializer, LoginSerializer, AccountReadSerializer
from rest_framework.decorators import action

class LoginView(APIView):
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: "Successful login. Response contains JWT tokens.",
            400: "Invalid credentials. Response contains error message."
        }
    )
    def post(self, request):

        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Authenticate user
            user = authenticate(request, username=email, password=password)

            if user:
                # Generate JWT token

                refresh = RefreshToken.for_user(user)
                # Retrieve user role
                role = user.role if hasattr(user, 'role') else None
                id = user.id if user else None
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'role': role , # Include user's role in the response,
                    'id' : id

                })
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: "Successfully logged out. Response contains success message.",
            400: "Invalid token. Response contains error message."
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'})
        except TokenError:
            return Response({'error': 'Invalid token'}, status=400)


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Protected view accessible only to authenticated users",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description=CommonConstants.JWT_TOKEN_SWAGGER_DESCRIPTION,
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    def get(self, request):
        user = request.user
        return Response({'message': f'Hello, {user.username}! You are authenticated.'})


class AccountViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Account.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return AccountReadSerializer
        return AccountWriteSerializer

        # Apply the decorator at the class level

    def get_permissions(self):
        if self.action in ['register', 'register_parent', 'register_staff']:
            return []
        return super().get_permissions()

    def get_allowed_methods(self):
        methods = super().get_allowed_methods()
        if self.action == 'register':
            return ['POST']
        return methods

    @swagger_auto_schema(
        request_body=AccountWriteSerializer,
        responses={status.HTTP_201_CREATED: AccountWriteSerializer}
    )
    @action(methods=["POST"], detail=False,url_path='register/parent')
    def register_parent(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(role=UserRole.PARENT.value)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=AccountWriteSerializer,
        responses={status.HTTP_201_CREATED: AccountWriteSerializer}
    )
    @action(methods=["POST"], detail=False, url_path='register/staff')
    def register_staff(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(role=UserRole.STAFF.value)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Get details of the users by role",
        responses={status.HTTP_201_CREATED: AccountReadSerializer},
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description=CommonConstants.JWT_TOKEN_SWAGGER_DESCRIPTION,
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter('role', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='User role'),
        ]
    )
    def list(self, request, *args, **kwargs):
        role = request.query_params.get('role', None)
        if role not in [role.value for role in UserRole]:
            return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)

        users = self.get_queryset().filter(role=role)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={status.HTTP_201_CREATED: AccountReadSerializer},
        operation_summary="Get details of the currently authenticated user",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description=CommonConstants.JWT_TOKEN_SWAGGER_DESCRIPTION,
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        user = request.user
        # Retrieve user details
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Partial update a YourModel instance",
        operation_description="Update a Account instance partially by providing only the fields to be updated",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT token",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        request_body= AccountWriteSerializer,
        responses={status.HTTP_200_OK: AccountReadSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.fields.pop('password')  # Exclude password field if not provided
        serializer.fields.pop('email')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
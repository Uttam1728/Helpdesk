from django.contrib.auth import authenticate
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from common.constants import UserRole, CommonConstants
from user_accounts.models import Account
from user_accounts.permissions import IsAdminUser
from user_accounts.serializer import UserRegistrationSerializer, LoginSerializer, UserReadSerializer


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

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'role': role  # Include user's role in the response
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


class UserRegistrationAPIView(APIView):
    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={status.HTTP_201_CREATED: UserRegistrationSerializer}
    )
    def post(self, request):
        print(request)
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(role=UserRole.PARENT.value)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUserAccountAPIView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        responses={200: openapi.Response("OK", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'role': openapi.Schema(type=openapi.TYPE_STRING),  # Modify according to your user model
                # Add other user details as needed
            }
        ))},
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
    def get(self, request):
        user = request.user
        # Retrieve user details
        serializer = UserReadSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
        # user_data = {
        #     'id': user.id,
        #     'username': user.username,
        #     'email': user.email,
        #     'role': user.role if hasattr(user, 'role') else None  # Assuming 'role' is a field in your user model
        #     # Add other user details as needed
        # }
        # return Response(user_data, status=status.HTTP_200_OK)

class UserByRoleAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get users by role",
        responses={200: UserRegistrationSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('role', openapi.IN_PATH, type=openapi.TYPE_STRING, description='User role'),
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING,
                              description=CommonConstants.JWT_TOKEN_SWAGGER_DESCRIPTION, required=True),

        ],
    )
    def get(self, request, role):
        if role not in [role.value for role in UserRole]:
            return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)

        users = Account.objects.filter(role=role)
        serializer = UserReadSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from .serializers import CustomTokenObtainPairSerializer, UserRegistrationSerializer
import json

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User created successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'role': getattr(user, 'role', 'TEACHER')  # Default role if not set
        })

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            # Generate a simple reset token (in real app, this would be more secure)
            reset_token = get_random_string(32)
            
            # Store the reset token in user's session or temporary storage
            # For simplicity, we'll store it in a JSON field or use a simple approach
            # In production, you might want to use Redis or database table for tokens
            
            # For now, we'll create a simple token that can be validated
            # Store token in user's last_name temporarily (not ideal but simple for demo)
            user.last_name = f"RESET_TOKEN:{reset_token}"
            user.save()
            
            return Response({
                'message': 'Password reset initiated',
                'reset_token': reset_token,
                'email': email,
                'user_info': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

class ResetPasswordView(APIView):
    def post(self, request):
        reset_token = request.data.get('reset_token')
        new_password = request.data.get('new_password')
        email = request.data.get('email')
        
        if not all([reset_token, new_password, email]):
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            # Check if the reset token matches
            if user.last_name == f"RESET_TOKEN:{reset_token}":
                # Update password
                user.password = make_password(new_password)
                user.last_name = ""  # Clear the reset token
                
                # Force save and refresh
                user.save(force_update=True)
                user.refresh_from_db()
                
                # Verify password was actually changed
                password_verified = user.check_password(new_password)
                
                # Return user info for debugging
                return Response({
                    'message': 'Password reset successfully',
                    'password_verified': password_verified,
                    'user_info': {
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid reset token'}, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
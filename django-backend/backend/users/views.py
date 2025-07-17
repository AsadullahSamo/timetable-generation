from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ProfileView(APIView):
    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'role': user.role
        })
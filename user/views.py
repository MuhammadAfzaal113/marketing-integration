from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from django.contrib.auth import get_user_model


User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"status": "error", "message": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "success": True,
                    "message": "Login successful",
                    "token": token.key,
                    "user": {
                        "id": str(user.id),
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                },status=status.HTTP_200_OK)

        return Response({"success": False, "message": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({"success": False, "message": "Something went wrong", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

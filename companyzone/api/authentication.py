from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_205_RESET_CONTENT
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import ensure_csrf_cookie
from .serializers import RegisterAppUserSerializer, AppUserSerializer, AppUserTokenObtainPairSerializer, AppUserTokenRefershSerializer
from django.contrib.auth import get_user_model
from .permissions import UserPermissionsChecker

# No need Authentication and Authorization
class RegisterAPIUserAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        u_obj = RegisterAppUserSerializer(data=request.data)
        if u_obj.is_valid():
            u_obj.save()
            # Returns the safe data (username, email) along with the success status
            return Response(u_obj.data, status=HTTP_201_CREATED)
        # Returns validation error details (e.g., "username already exists")
        return Response(u_obj.errors, status=HTTP_400_BAD_REQUEST)

# ################# Later - Production-SecurityGrade #################
# @ensure_csrf_cookie
# def init_csrf(request):
#     """
#     This endpoint sends data to the frontend AND forces Django 
#     to set the 'csrftoken' cookie, even for anonymous users.
#     """
#     return Response({'detail':'CSRF Cookie attached to cookies.'})
   
class ThrottledTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = AppUserTokenObtainPairSerializer
    # This matches the 'login_burst' key we defined in settings.py
    throttle_scope = 'login_burst'
    throttle_classes = [ScopedRateThrottle]

class ThrottledTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    serializer_class = AppUserTokenRefershSerializer
    throttle_scope = 'login_burst'
    throttle_classes = [ScopedRateThrottle]

User = get_user_model()
# Django's Authentication Middleware fills request.user automatically before your view code even runs 
# 1. If using SimpleJWT (Bearer Tokens)
# When the frontend sends a request, it includes an HTTP Header like this:Authorization: Bearer <your_access_token>
#   Django Rest Framework's JWTAuthentication class intercepts the request.
#   It decodes the access token and reads the user ID stored inside it.
#   It runs a database query behind the scenes: User.objects.get(id=user_id).
#   It attaches that fetched user object straight to request.user
class AppUserProfile(APIView):
    permission_classes = [IsAuthenticated, UserPermissionsChecker]
    permissions_required_actions_map = {
        'get': ['accounts.view_appuser'],
        'put': ['accounts.change_appuser'],
        'patch': ['accounts.change_appuser'],
    }

    def get(self, request):
        """Return the currently authenticated user's profile."""
        try:
            # request.user contains the AppUser instance automatically
            # Since DRF's JWTAuthentication has already fetched the user from the database 
            # and put it in request.user, you don't need a database query at all.
            ser_user = AppUserSerializer(request.user)
            return Response({'user':ser_user.data}, status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error':f'User does not exist.'}, status=HTTP_400_BAD_REQUEST)

    # Wrire Later - for editing
    def patch(self, request):
        """Allow the user to update their own profile fields (e.g., first_name, email)."""
        pass

# By default, standard rest_framework_simplejwt only generates and verifies tokens mathematically. 
# It doesn't store them in a database.
# If a user logs out, their tokens remain completely valid anywhere on the internet until they naturally expire.
# rest_framework_simplejwt.token_blacklist:
#   Hybrid. The server tracks stolen/invalidated/rotated tokens in a database.
#   Server-side enforcement. The server explicitly rejects the token.
#   High. Once blacklisted (or rotated), the stolen token becomes useless immediately.
class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist() # Destroys the refresh token
            return Response({'detail':'Successfully logged out.'}, status=HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'detail':'Token is invalid or expired.'}, status=HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# @ensure_csrf_token # This forces Django to drop the HttpOnly cookie in to the browser
# def csrf_token_handshake(request):
#     """
#     Public initialization gate. Returns the raw CSRF token text string 
#     inside a JSON payload so frontend can securely lock it away in memory.
#     """
#     return JsonResponse({'csrfToken':get_token(request)});
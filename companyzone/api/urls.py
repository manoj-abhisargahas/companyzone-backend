from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView
from .authentication import AppUserProfile, RegisterAPIUserAPIView, \
ThrottledTokenObtainPairView, ThrottledTokenRefreshView, LogoutAPIView


# namespace
app_name = 'api' # so internally we have to use like api:login-url

router = DefaultRouter()
# just for practice - but fully functional
router.register('EmployeeModelViewSet', views.EmployeeModelViewSet, basename='emp-model-viewset')


urlpatterns = [
    # No need Authentication for Register to API, this creates API user
    path('register/', RegisterAPIUserAPIView.as_view(), name='register-url'),

    # ===========================================================================
    # JWT Authentication Endpoints:
    # -------------------------------------------------------------------
    # 1. Send a POST request to 'login/' with json body
    # Login endpoint: (method:'POST', headers:{'Content-Type':"application/json"}), body:JSON.stringify({"username": "your_username", "password": "your_password"}))
    path('login/', ThrottledTokenObtainPairView.as_view(), name='login-url'),
    # Sends access, refresh tokens and user data directly in the JSON response body
    # Success (200 OK): {"access":"<token>", "refersh":"<token>", "user":{id:"",username:"",...}}
    # Failure (401 Unauthorized): {"detail": "No active account found with the given credentials"}
    # Failure (Missing Fields (400 Bad Request)): {"username": ["This field is required."], "password": ["This field is required."]}

    # 2. Send a GET request to any protected view like ViewEmployees.
    # (method:'<any>', headers:{'Content-Type':"application/json", 'Authorization':'Bearer <access_token>'}), body:JSON.stringify(<any-content>))
    
    # 3. When the access token expires (after 15 minutes based on our settings), send a POST request to 'token/refresh/'
    # Refresh endpoint: (method:'POST', headers:{'Content-Type':"application/json"}), body:JSON.stringify({"refresh": "<refersh_token>"}))
    path('token/refresh/', ThrottledTokenRefreshView.as_view(), name='token-refresh-url'),
    # returns a brand new access token without making the user re-type their password.
    # if ROTATE_REFRESH_TOKENS=True:
    #   Success (200 OK): {"access":"<token>", "refersh":"<token>"}
    # else:
    #   Success (200 OK): {"access":"<token>"} 
    # Failure (401 Unauthorized): {"detail": "Token is invalid or expired", "code": "token_not_valid"}

    # 4. Get user profile data
    # Me endpoint: (method:'GET', headers:{'Content-Type':"application/json", 'Authorization':'Bearer <access_token>'}))
    path('me/', AppUserProfile.as_view(), name='me-url'),
    # Success (200 OK): {}
    # Failure (401 Unauthorized): {"detail": "Token is invalid or expired", "code": "token_not_valid"}

    # 5. Optional endpoint to check if a token(access/refersh) is still valid
    # Verify endpoint: (method:'POST', headers:{'Content-Type':"application/json"), body:JSON.stringify({'token':'<access_token/refresh_token>'}))
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify-url'),
    # Success (200 OK): {}
    # Failure (401 Unauthorized): {"detail": "Token is invalid or expired", "code": "token_not_valid"}

    # 6. When a user logs out, your frontend application must:
    #   Send a POST request to /api/logout/ with the refresh token in the request body.
    #   Include the standard Access Token in the Authorization: Bearer <access_token> header.
    #   Delete both tokens from the frontend storage (e.g., localStorage, cookies) after receiving a successful response.
    # Verify endpoint: (method:'POST', headers:{'Content-Type':"application/json"), body:JSON.stringify({'refersh':'<refresh_token>'}))
    path('logout/', LogoutAPIView.as_view(), name='logout-url'),
    # Success (205 RESET CONTENT): {'detail':'Successfully logged out.'}
    # Failure (400 Bad Request): {'detail':'Token is invalid or expired.'}
    # ===========================================================================

    # Selected to serve for frontend
    path('CustomEmployee/', views.CustomEmployeeAPIView.as_view(), name='cust-emp-url'), # for GET_ALL which supports Pagination
    path('NewEmpFormData/', views.NewEmpFormDataAPIView.as_view(), name='emp-form-data-url'),
    path('Employee/', views.EmployeeAPIView.as_view(), name='emp-url'), # for POST
    path('Employee/<int:pk>/', views.EmployeeModifyAPIView.as_view(), name='emp-modify-url'), # for GET_ONE, PUT, DELETE

    # just for practice - partial methods written
    path('CustomEmployee/<int:pk>/', views.CustomEmployeeModifyAPIView.as_view(), name='cust-emp-modify-url'),

    path('', include(router.urls)),
]
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model # import the dynamic user

User = get_user_model()

# Create your tests here.
class CompanyZoneAPITests(APITestCase):
    def setUp(self):
        """Runs before every test to populate the MySQL Container with a user base."""
        self.username = "testdeveloper"
        self.password = "SecurePass123!"
        self.email = "dev@companyzone.com"

        # Create a test user in the temporary test database instance
        self.test_user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email
        )

    # ==============================================================
    # 🔓 AUTHENTICATION FREE ENDPOINT TESTS
    # ==============================================================
    """
    1. User Logs In  ──> [Send Password] ──> Django validates it
    2. Tokens Issued <── [Access & Refresh Tokens] <── Sent back to Frontend
    3. Read Data     ──> [Send Access Token] ──> Django returns Employee Table Data
    4. Token Expires ──> [Access Token Dead!] ──> Django returns 401 Unauthorized
    5. Silent Renew  ──> [Send Refresh Token] ──> Django returns New Access Token
    """

    def test_user_registration_endpoint(self):
        """1. Verifies that a new user successfully register via the API"""
        url = reverse('api:register-url')
        data = {
            "username": "newuserxyz",
            "email": "newuser@companyzone.com",
            "password": "NewSecurePassword567!"
        }
        response = self.client.post(url, data, format='json')
        #Expect 201 Created or 200 OK depending on your Register view logic
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_user_login_return_jwt_tokens(self):
        """2. Verifies that valid credentials return access and refresh JWT tokens"""
        url = reverse('api:login-url')
        data = {
            "username": self.username,
            "password": self.password
        }
        response = self.client.post(url, data, format='json')
        #401 UnAuthorized, when any other credentials passed other than self.username or self.password
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # SimpleJWT official output key checks
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_new_employee_form_data_is_accessible(self):
        """3. Verifies that the metadata form data endpoint can be fetched freely"""
        url = reverse('api:emp-form-data-url')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) #401 when UnAuthorized


    # ==============================================================
    # 🔓 LOGGED-IN / RESTRICTED ENDPOINT TESTS
    # ==============================================================

    def test_add_employee(self):
            """4. Verifies that adding an employee profile without a JWT token blocks access"""
            """4. Add Employee """
            # Hitting "Employee/
            url = reverse('api:emp-url')
            data = {
                "eno": 1,
                "ename": "Ravi Kiran",
                "esal": 20000
            }
            response = self.client.post(url, data, format='json')
            print('response1>>>>>', response.data);
            for key, value in response.items():
                print('response1>>>>', key, value);
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) #401 when UnAuthorized

    def test_modify_employee_denies_anonymous_user(self):
        """4. Verifies that updating an employee profile without a JWT token blocks access"""
        """4. Curretnly accepting without Authentication but previous posted data will not help here"""
        # Hitting "Employee/<int:pk>/" with a primary key (1)
        url = reverse('api:emp-modify-url', kwargs={'pk':1})
        data = {
            "eno": 1,
            "ename": "Ravi Kiran",
            "esal": 14000
        }
        response = self.client.put(url, data, format='json')
        print('response>>>>>', response.data);
        for key, value in response.items():
            print('response>>>>>', key, value);
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) #401 when UnAuthorized

    def test_router_viewswet_list_is_accessible(self):
        """5. Verifies that the router base listing is open"""
        # DefaultRouter appends '-list' to the basename for top-level collection requests
        url = reverse('api:emp-model-viewset-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_router_viewswet_destroy_denies_anonymous_user(self):
        """6. Verifies that deleting via ModelViewSet requires active authorization"""
        # DefaultRouter appends '-detail' for resourse-specific path like entry modification
        url = reverse('api:emp-model-viewset-detail', kwargs={'pk':1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) #401 when UnAuthorized
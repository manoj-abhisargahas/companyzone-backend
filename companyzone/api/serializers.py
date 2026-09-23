from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from companyzone.utils import sanitize_user_input
from empapp.models import Employee, Department, Location
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
import logging
from rest_framework_simplejwt.tokens import RefreshToken

class SanitizedModelSeralizer(serializers.ModelSerializer):
    """
    A base model serializer that automatically sanitizes all incoming 
    string fields before data validation or database saving.
    """

    # Clean a specific field using validate_<field_name>
    # --------------------------------------------------
    # def validate_ename(self, value):
    #     return sanitize_user_input(value)


    # Clean all text fields automatically using to_internal_value
    # -----------------------------------------------------------
    def to_internal_value(self, data):
        # Run standard DRF parsing first
        internal_value = super().to_internal_value(data)

        for field, value in internal_value.items():
            if isinstance(value, str):
                internal_value[field] = sanitize_user_input(value)

        return internal_value

    
class DepartmentSerializer(SanitizedModelSeralizer):
    class Meta:
        model = Department
        fields = '__all__'

class LocationSerializer(SanitizedModelSeralizer):
    class Meta:
        model = Location
        fields = '__all__'

class EmpSerializer(SanitizedModelSeralizer):
    # Overriding fields to use nested serializers
    # By adding read_only=True, you tell Django:
    #     For GET requests: Use the nested serializer to display the 
    #                       full department details (ID, name, etc.).
    #     For POST/PUT requests: Completely ignore this field during data validation.
    # edept = DepartmentSerializer(read_only=True)
    # eloc = LocationSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ['eno','ename','esal','edept','eloc','epfpic']

    # 1. DO NOT declare edept or eloc at the top anymore! 
    # Let Django treat them as standard writeable relational fields (expecting simple IDs).
    # It accepts "INBOUND" integer values because of how ModelSerializer works by default
    # Because it sees a ForeignKey, DRF automatically configures that field internally as a PrimaryKeyRelatedField.
    # Database Verification: It automatically runs a safe query under the hood, similar to: Department.objects.get(pk=2)

    # 2. Override to_representation to change the "OUTBOUND" data format
    def to_representation(self, instance):
        # Get the standard flat primitive dictionary data (with IDs)
        representation = super().to_representation(instance)

        # Dynamically inject the full nested department data if it exists
        if instance.edept:
            representation['edept'] = DepartmentSerializer(instance.edept).data
            # or = {'dept_id':instance.edept.dept_id, 'dept_name':instance.edept.dept_name}
        if instance.eloc:
            representation['eloc'] = LocationSerializer(instance.eloc).data
            # or = {'loc_id':instance.eloc.loc_id, 'loc_name':instance.eloc.loc_name}

        return representation

class CustomEmpSerializer(SanitizedModelSeralizer):
    empno = serializers.IntegerField()
    firstname = serializers.CharField(max_length=20)
    lastname = serializers.CharField(max_length=20)
    salary = serializers.IntegerField()
    bonus = serializers.IntegerField()

    # for POST
    def create(self, validated_data):
        empno = validated_data['empno']
        fname = validated_data['firstname']
        lname = validated_data['lastname']
        sal = validated_data['salary']
        bonus = validated_data['bonus']

        emp_obj = Employee.objects.create(
            eno = empno,
            ename = fname+' '+lname,
            esal = sal + bonus
        )

        return emp_obj

    # for PUT
    def update(self, instance, validated_data):
        fname = validated_data['firstname']
        lname = validated_data['lastname']
        sal = validated_data['salary']
        bonus = validated_data['bonus']

        instance.ename = fname+' '+lname
        instance.esal = sal + bonus

        return instance

    # for POST, PUT, PATCH
    def validate(self, data_to_validate):
        errors = []

        if data_to_validate['empno'] < 0:
            errors.append({'empno':'Negative values cannot be accepted for Employee No.'})
        if data_to_validate['salary'] < 0:
            errors.append({'salary':'Negative values cannot be accepted for Salary.'})
        if data_to_validate['bonus'] < 0:
            errors.append({'bonus':'Negative values cannot be accepted for Bonus.'})
        
        if errors:
            raise ValidationError(errors)
        
        return data_to_validate #validated_data

User = get_user_model()
class RegisterAppUserSerializer(SanitizedModelSeralizer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {
            # Makes password write-only so it never leaks in responses
            'password': {'write_only':True}
        }

    def create(self, validated_data):
        # Appropriately hashes the password using Django's PBKDF2/Argon2 algorithms instead of saving it in plain text

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            # Automated Production Lockdowns
            is_api_user=True,
            is_staff=False,
            is_superuser=False
        )

        # Automatically fetch and assign the 'Api User' group
        try:
            api_group = Group.objects.get(name='Api User')
            user.groups.add(api_group) # Links the user to the group permissions
        except Group.DoesNotExist:
            # Safe fallback if you haven't created the group in the admin panel yet
            logging.warning("The group 'Api User' does not exist. Permissions not assigned.")

        return user

class AppUserSerializer(SanitizedModelSeralizer):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_superuser', 'is_staff']

# TokenObtainPairView has user data in "self.user"
# where TokenRefreshView, TokenVerifyView don't have
# use from django.forms.models import model_to_dict to get the fields of objects
#   model_to_dict(User.objects.get(id=1))
class AppUserTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # 1. Get the standard response (contains 'access' and 'refresh')
        data = super().validate(attrs)

        # 2. Add your custom user data fields directly into the response payload
        data['user'] = AppUserSerializer(self.user).data
        return data

class AppUserTokenRefershSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        # 1. Gets the new access token (and refresh token if rotation is on)
        data = super().validate(attrs)

        # 2. Extract user_id from the incoming refresh token payload
        refresh_token_string = attrs['refresh']
        decoded_token = RefreshToken(refresh_token_string)
        user_id = decoded_token.payload.get('user_id')

        # 3. Add your custom user data fields directly into the response payload
        try:
            user = User.objects.get(id=user_id)
            data['user'] = AppUserSerializer(user).data
        except User.DoesNotExist:
            pass
        return data
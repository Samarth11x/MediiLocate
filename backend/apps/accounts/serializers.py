"""
Serializers for authentication, user profiles, and administrative auditing.
Ensures zero credential leakage and enforces strict role validation.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import UserProfile, UserRole, AuditLog
from apps.pharmacies.models import Pharmacy, VerificationStatus


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role', 'phone_number', 'created_at']
        read_only_fields = ['created_at']


class CurrentUserSerializer(serializers.ModelSerializer):
    """
    Public-safe representation of the authenticated user.
    Excludes password, password hash, and internal secret tokens.
    """
    role = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    is_pharmacist = serializers.SerializerMethodField()
    pharmacy = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'phone_number',
            'is_staff',
            'is_admin',
            'is_pharmacist',
            'pharmacy',
            'date_joined',
        ]
        read_only_fields = fields

    def get_role(self, obj):
        profile = getattr(obj, 'profile', None)
        if obj.is_superuser or obj.is_staff:
            return UserRole.ADMIN
        return profile.role if profile else UserRole.USER

    def get_phone_number(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.phone_number if profile else None

    def get_is_admin(self, obj):
        if obj.is_superuser or obj.is_staff:
            return True
        profile = getattr(obj, 'profile', None)
        return bool(profile and profile.role == UserRole.ADMIN)

    def get_is_pharmacist(self, obj):
        profile = getattr(obj, 'profile', None)
        return bool(profile and profile.role == UserRole.PHARMACIST)

    def get_pharmacy(self, obj):
        profile = getattr(obj, 'profile', None)
        if profile and profile.role == UserRole.PHARMACIST:
            pharmacy = obj.pharmacies.first()
            if pharmacy:
                return {
                    'id': pharmacy.id,
                    'name': pharmacy.name,
                    'address': pharmacy.address,
                    'area': pharmacy.area,
                    'city': pharmacy.city,
                    'pin_code': pharmacy.pin_code,
                    'contact_number': pharmacy.contact_number,
                    'license_number': pharmacy.license_number,
                    'verification_status': pharmacy.verification_status,
                    'rejection_reason': pharmacy.rejection_reason,
                }
        return None


class RegisterSerializer(serializers.Serializer):
    """
    User registration serializer.
    Strictly forbids role escalation to ADMIN.
    """
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=[UserRole.USER, UserRole.PHARMACIST],
        default=UserRole.USER,
        help_text="Registration role (USER or PHARMACIST only)"
    )
    phone_number = serializers.CharField(max_length=25, required=False, allow_blank=True)

    # Optional pharmacy fields for Pharmacist onboarding
    pharmacy_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    license_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    area = serializers.CharField(max_length=150, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    pin_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    contact_number = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_role(self, value):
        if value == UserRole.ADMIN:
            raise serializers.ValidationError("Public registration for the ADMIN role is strictly forbidden.")
        return value

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data.get('email', '')
        password = validated_data['password']
        role = validated_data.get('role', UserRole.USER)
        phone_number = validated_data.get('phone_number', '')

        # Create Django User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create Profile
        UserProfile.objects.create(
            user=user,
            role=role,
            phone_number=phone_number
        )

        # If Pharmacist, create Pharmacy in PENDING verification status
        if role == UserRole.PHARMACIST:
            pharmacy_name = validated_data.get('pharmacy_name') or f"{username}'s Pharmacy"
            address = validated_data.get('address') or "Pending address submission"
            area = validated_data.get('area') or "Central"
            city = validated_data.get('city') or "Demo City"
            pin_code = validated_data.get('pin_code') or "560001"
            contact_number = validated_data.get('contact_number') or phone_number
            license_number = validated_data.get('license_number') or "PENDING-LIC"

            Pharmacy.objects.create(
                name=pharmacy_name,
                owner=user,
                address=address,
                area=area,
                city=city,
                pin_code=pin_code,
                contact_number=contact_number,
                license_number=license_number,
                verification_status=VerificationStatus.PENDING,
                is_demo=True
            )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials provided.")
        if not user.is_active:
            raise serializers.ValidationError("This user account has been disabled.")

        attrs['user'] = user
        return attrs


class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'actor',
            'actor_username',
            'action',
            'target_type',
            'target_id',
            'metadata',
            'ip_address',
            'timestamp',
        ]
        read_only_fields = fields

    def get_actor_username(self, obj):
        return obj.actor.username if obj.actor else "System"

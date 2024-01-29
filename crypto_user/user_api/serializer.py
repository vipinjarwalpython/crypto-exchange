from rest_framework import serializers
from crypto_user.models import *
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
        ]

    def validate_email(self, value):
        # Add additional email validation logic if needed
        return value

    def validate_password(self, value):
        # Add additional password validation logic if needed
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = "__all__"


class UserKYCSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer()

    class Meta:
        model = KYCInformation
        fields = "__all__"


class CoinSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    symbol = serializers.CharField()
    slug = serializers.CharField()
    quote = serializers.DictField(child=serializers.DictField())


class UserDashboardSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    status = serializers.IntegerField()
    coin_info = CoinSerializer(many=True)


class UserWalletSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer()

    class Meta:
        model = UserWallet
        fields = "__all__"


class UserDashboardSerializer(serializers.ModelSerializer):
    # userwallet = UserWalletSerializer()

    class Meta:
        model = UserCryptoWallet
        fields = "__all__"


class UserCoinsSerializer(serializers.ModelSerializer):
    user_crypto_wallet = UserDashboardSerializer()

    class Meta:
        model = UpdateCoinDetails
        fields = "__all__"

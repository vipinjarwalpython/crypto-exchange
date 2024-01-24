from django.db import models
from django.contrib.auth.models import User
import datetime


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_kyc = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class KYCInformation(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50)
    document_number = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    document_image = models.ImageField(upload_to="kyc_documents/")
    verification_status = models.BooleanField(default=False)  # True if KYC is verified

    def __str__(self):
        return f"{self.user_profile}"


class BankAccount(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=50)
    account_holder_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    swift_code = models.CharField(max_length=20)


class UserWallet(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    balance = models.FloatField(default=00.00)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_profile} Wallet"


class UserCryptoWallet(models.Model):
    userwallet = models.ForeignKey(UserWallet, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    coin_name = models.CharField(max_length=100)
    coin_quantity = models.FloatField(default=00.00)
    coin_price = models.FloatField(default=00.00)
    coin_status = models.CharField(max_length=100)
    total_amount = models.FloatField(default=00.00)
    profitandloss = models.FloatField(default=00.00)

    def __str__(self):
        return f"{self.userwallet} = {self.coin_name} * {self.coin_quantity}"


class CoinTransaction(models.Model):
    userwallet = models.ForeignKey(UserWallet, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    coin_name = models.CharField(max_length=100)
    coin_quantity = models.FloatField(default=00.00)
    coin_price = models.FloatField(default=00.00)
    coin_status = models.CharField(max_length=100)
    total_amount = models.FloatField(default=00.00)
    profitandloss = models.FloatField(default=00.00)

    def __str__(self):
        return f"{self.userwallet} = {self.coin_name} * {self.coin_quantity}"


class FundTransactions(models.Model):
    userwallet = models.ForeignKey(UserWallet, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField(default=0.0)
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.userwallet} = {self.amount} - {self.status}"

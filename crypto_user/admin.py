from django.contrib import admin
from .models import (
    UserProfile,
    KYCInformation,
    UserWallet,
    UserCryptoWallet,
    CoinTransaction,
    FundTransactions,
)

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(KYCInformation)
admin.site.register(UserWallet)
admin.site.register(UserCryptoWallet)
admin.site.register(CoinTransaction)
admin.site.register(FundTransactions)

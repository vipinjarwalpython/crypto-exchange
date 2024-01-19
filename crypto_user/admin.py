from django.contrib import admin
from .models import UserProfile, KYCInformation, UserWallet, UserCryptoWallet

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(KYCInformation)
admin.site.register(UserWallet)
admin.site.register(UserCryptoWallet)

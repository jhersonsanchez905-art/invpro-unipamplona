from django_otp.plugins.otp_totp.models import TOTPDevice


def user_2fa_status(request):
    if request.user.is_authenticated:
        tiene_2fa = TOTPDevice.objects.filter(
            user=request.user, confirmed=True
        ).exists()
    else:
        tiene_2fa = False
    return {'tiene_2fa': tiene_2fa}
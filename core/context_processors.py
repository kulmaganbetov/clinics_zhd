from .models import ClinicInfo


def clinic_info(request):
    """Context processor для информации о клинике"""
    return {
        'clinic_info': ClinicInfo.objects.first()
    }

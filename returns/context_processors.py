from bors_project import VERSION
from .models import OperatorAccess


def operator_access(request):
    access_id = request.session.get('operator_access_id')
    if not access_id:
        return {'operator_access': None, 'app_version': VERSION}
    try:
        return {'operator_access': OperatorAccess.objects.get(pk=access_id, is_active=True), 'app_version': VERSION}
    except OperatorAccess.DoesNotExist:
        return {'operator_access': None, 'app_version': VERSION}

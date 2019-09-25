from off.elements.models import Permissions, PermissionsShift

def get_permissions_rwx(permissions, scope=None):
    if scope:
        scope = [scope]
    else:
        scope = [PermissionsShift.u, PermissionsShift.g, PermissionsShift.a]
    result = ''
    for shift in scope:
        perms = (permissions & (0b111 << shift)) >> shift
        for perm in [Permissions.r, Permissions.w, Permissions.x]:
            result += perm.name if perms & perm else '-'
    return result
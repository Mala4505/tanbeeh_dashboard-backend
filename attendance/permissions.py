from rest_framework.permissions import BasePermission


# --- Individual Role Permissions ---

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "admin"


class IsPrefect(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "prefect"


class IsDeputyPrefect(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "deputy_prefect"


class IsMasool(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "masool"


class IsMuaddib(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "muaddib"


class IsLajnatMember(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "lajnat_member"


# --- Combined Role Permissions ---

class IsFlaggingRole(BasePermission):
    """
    Allows access to users who can flag students:
    Prefect, Deputy Prefect, Masool, Muaddib
    """
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role in [
            "prefect", "deputy_prefect", "masool", "muaddib"
        ]


class IsDashboardRole(BasePermission):
    """
    Allows access to dashboards for all roles except Admin.
    Admin has global dashboard separately.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role in [
            "prefect", "deputy_prefect", "masool", "muaddib", "lajnat_member"
        ]


class IsAssignmentRole(BasePermission):
    """
    Allows access to assignment management.
    Only Admin can assign/reassign students.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "admin"


class IsAuditViewer(BasePermission):
    """
    Allows access to audit logs.
    Only Admin can view audit logs.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "admin"

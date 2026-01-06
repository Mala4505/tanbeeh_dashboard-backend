
def get_role_scope(user):
    """
    Determine the role and scope for the logged-in user.
    Replace with your actual role logic.
    """
    role = getattr(user, "role", None)

    # Example scope mapping
    if role == "prefect":
        return role, {"hizb_id": user.hizb_id}
    elif role == "masool":
        return role, {"group_id": user.group_id}
    elif role == "muaddib":
        return role, {"group_id": user.group_id}
    elif role == "lajnat":
        return role, {"student_ids": user.assigned_students.values_list("id", flat=True)}
    else:
        return None, {}

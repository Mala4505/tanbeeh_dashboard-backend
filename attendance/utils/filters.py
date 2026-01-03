def filter_by_role(user, records):
    """
    Role-based filtering of attendance records.

    - Admins: see all records.
    - Prefects/Deputy Prefects: see only their hizb.
    - Faculty: see only their room.
    - Masool: see only assigned students.
    - Muaddib: see only students in their groups.
    - Lajnat Members: see only flagged students assigned to them.
    """

    role = getattr(user, "role", None)

    if role == "admin":
        return records

    elif role in ["prefect", "deputy_prefect"]:
        return [r for r in records if r.get("hizb") == getattr(user, "hizb", None)]

    elif role == "faculty":
        return [r for r in records if r.get("room") == getattr(user, "room", None)]

    elif role == "masool":
        # Assuming user has masool_students relation
        masool_students = getattr(user, "masool_students", [])
        masool_ids = {s.trno for s in masool_students}
        return [r for r in records if r.get("id") in masool_ids]

    elif role == "muaddib":
        # Assuming user has muaddib_students relation
        muaddib_students = getattr(user, "muaddib_students", [])
        muaddib_ids = {s.trno for s in muaddib_students}
        return [r for r in records if r.get("id") in muaddib_ids]

    elif role == "lajnat_member":
        # Lajnat members only see flagged students assigned to them
        flagged_ids = getattr(user, "assigned_flagged_ids", [])
        return [r for r in records if r.get("id") in flagged_ids]

    # Default: no records
    return []

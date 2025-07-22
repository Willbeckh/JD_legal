from typing import Optional, Literal
from users.models import User
from core.models import SiteSetting

# Define allowed roles
AllowedRole = Literal["transcriber", "proofreader"]


def get_next_user(role: AllowedRole) -> Optional[User]:
    # Only fetch user IDs - (less memory)
    user_ids = list(
        User.objects.filter(role=role, is_active=True)
        .order_by("id")
        .values_list("id", flat=True)
    )

    if not user_ids:
        return None

    setting_key = f"last_{role}_id"
    setting = SiteSetting.objects.filter(key=setting_key).first()

    try:
        last_id = int(setting.value) if setting and setting.value is not None else 0
    except (ValueError, TypeError):
        last_id = 0

    # Find next ID greater than last used
    next_user_id = next((uid for uid in user_ids if uid > last_id), None)

    if next_user_id is None:
        # Wrap around
        next_user_id = user_ids[0]

    # Save this ID as the last assigned
    SiteSetting.objects.update_or_create(
        key=setting_key, defaults={"value": str(next_user_id)}
    )

    return User.objects.get(id=next_user_id)

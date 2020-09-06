from typing import Any

from billing.models.user import User


def validate_funds(funds: Any) -> bool:
    if not funds:
        return False
    try:
        funds = float(funds)
    except ValueError:
        return False
    if funds < 0:
        return False
    return True


def validate_user(transfer_to: User, current_user: User) -> bool:
    if not transfer_to:
        return False
    if transfer_to == current_user:
        return False
    return True

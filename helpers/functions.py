import math

from helpers.enums import DeliveryState, SizeType, WeightType


def is_state_change_valid(old_state, new_state):
    if (
            (old_state == DeliveryState.READY and new_state == DeliveryState.ASSIGNED)
            or (old_state == DeliveryState.ASSIGNED and new_state == DeliveryState.DELIVERING)
            or (old_state == DeliveryState.DELIVERING and (new_state == DeliveryState.UNDELIVERABLE
                                                           or new_state == DeliveryState.DELIVERED))
    ):
        return True
    else:
        return False


def calculate_price(distance, size, weight):
    price = distance / 1000  # 1 euro per km

    if size == SizeType.LARGE:
        price = price*1.15
    elif size == SizeType.MEDIUM:
        price = price * 1.1

    if weight == WeightType.HEAVY:
        price = price*1.15
    elif weight == WeightType.MEDIUM:
        price = price * 1.1

    return math.floor(price * 100) / 100


import math

from helpers.enums import DeliveryState, SizeType, WeightType


def is_state_change_valid(old_state, new_state):
    """
    Check if state change follows the logical sequence of item delivery

    :param old_state: Current state of delivery
    :param new_state: Proposed new state of delivery
    :return: True if change valid, false if change invalid
    """
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
    """
    Calculate price of the delivery based on distance, size and weight.

    :param distance: Route distance from pickup place to delivery place
    :param size: Size type of delivery
    :param weight: Weight type of delivery
    :return: Calculated price in euros
    """
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


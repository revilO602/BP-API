from helpers.enums import DeliveryState


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

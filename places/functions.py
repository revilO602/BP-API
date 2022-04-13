from couriers.models import Courier


def is_courier(user):
    return Courier.objects.filter(user=user).exists()


def is_state_change_valid(old_state, new_state):
    if (
            (old_state == 'ready' and new_state == 'assigned')
            or (old_state == 'assigned' and new_state == 'delivering')
            or (old_state == 'delivering' and (new_state == 'undeliverable' or new_state == 'delivered'))
    ):
        return True
    else:
        return False

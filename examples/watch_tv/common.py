IS_THIRSTY_KEY = "is_thirsty"
DRINKS_COUNT_KEY = "drinks_count"
FRIDGE_OPEN_KEY = "is_fridge_open"
COUCH_OCCUPANCY_KEY = "couch_occupancy"
COUCH_SEATS_KEY = "couch_seats"
HELD_OBJECT_KEY = "held_object"

AGENT_NAMESPACE = "agent"


class Drink:
    def __init__(self):
        self.sips_remaining = 4

    def take_sip(self):
        if self.sips_remaining == 0:
            raise ValueError("drink is empty")
        self.sips_remaining -= 1

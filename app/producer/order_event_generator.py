import json
import random
import time
from datetime import datetime
from uuid import uuid4


CUSTOMERS = [
    "CUST-1001",
    "CUST-1002",
    "CUST-1003",
    "CUST-1004",
    "CUST-1005",
]

PRODUCTS = [
    "Laptop",
    "Headphones",
    "Keyboard",
    "Monitor",
    "Mouse",
]

ORDER_STATUSES = [
    "created",
    "paid",
    "shipped",
    "delivered",
]


def generate_order_event() -> dict:

    quantity = random.randint(
        1,
        4,
    )

    unit_price = round(
        random.uniform(
            20,
            1200,
        ),
        2,
    )

    event = {
        "event_id": str(
            uuid4()
        ),
        "order_id": (
            f"ORD-{random.randint(10000, 99999)}"
        ),
        "customer_id": random.choice(
            CUSTOMERS
        ),
        "product": random.choice(
            PRODUCTS
        ),
        "quantity": quantity,
        "unit_price": unit_price,
        "order_value": round(
            quantity * unit_price,
            2,
        ),
        "status": random.choice(
            ORDER_STATUSES
        ),
        "event_timestamp": (
            datetime.utcnow().isoformat()
        ),
    }

    return event


def main():

    while True:

        event = generate_order_event()

        print(
            json.dumps(
                event,
                indent=2,
            )
        )

        time.sleep(
            2
        )


if __name__ == "__main__":
    main()
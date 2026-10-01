import json
from collections import deque

from kafka import KafkaConsumer

from app.services.database import insert_anomaly_alert


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "order-events"

HIGH_VALUE_THRESHOLD = 2500.0
ROLLING_WINDOW_SIZE = 20
SPIKE_MULTIPLIER = 2.5


def create_consumer() -> KafkaConsumer:

    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="streamsight-anomaly-detector",
        value_deserializer=lambda value: json.loads(
            value.decode("utf-8")
        ),
    )


def detect_anomalies(
    event: dict,
    recent_values: deque,
) -> list[tuple[str, str]]:

    alerts = []

    order_value = float(
        event["order_value"]
    )

    if order_value >= HIGH_VALUE_THRESHOLD:

        alert_message = (
            f"High-value order detected: "
            f"${order_value:,.2f}"
        )

        alerts.append(
            (
                "HIGH_VALUE_ORDER",
                alert_message,
            )
        )

    if len(recent_values) >= 5:

        rolling_average = (
            sum(recent_values)
            / len(recent_values)
        )

        if (
            rolling_average > 0
            and order_value
            >= rolling_average
            * SPIKE_MULTIPLIER
        ):

            alert_message = (
                f"Order value ${order_value:,.2f} "
                f"is much higher than rolling average "
                f"${rolling_average:,.2f}"
            )

            alerts.append(
                (
                    "ORDER_VALUE_SPIKE",
                    alert_message,
                )
            )

    return alerts


def main():

    consumer = create_consumer()

    recent_values = deque(
        maxlen=ROLLING_WINDOW_SIZE
    )

    print(
        f"Watching topic for anomalies: "
        f"{KAFKA_TOPIC}"
    )

    print(
        "Saving anomaly alerts to PostgreSQL..."
    )

    try:

        for message in consumer:

            event = message.value

            alerts = detect_anomalies(
                event,
                recent_values,
            )

            order_value = float(
                event["order_value"]
            )

            if alerts:

                print(
                    "\n=============================="
                )

                print(
                    "STREAMSIGHT ALERT"
                )

                print(
                    "=============================="
                )

                print(
                    f"Order ID: "
                    f"{event['order_id']}"
                )

                print(
                    f"Customer ID: "
                    f"{event['customer_id']}"
                )

                print(
                    f"Product: "
                    f"{event['product']}"
                )

                print(
                    f"Order value: "
                    f"${order_value:,.2f}"
                )

                for (
                    alert_type,
                    alert_message,
                ) in alerts:

                    insert_anomaly_alert(
                        event,
                        alert_type,
                        alert_message,
                    )

                    print(
                        f"Alert: {alert_type}"
                    )

                    print(
                        f"Message: {alert_message}"
                    )

                    print(
                        "Saved alert to PostgreSQL."
                    )

            recent_values.append(
                order_value
            )

    except KeyboardInterrupt:

        print(
            "\nStopping anomaly detector..."
        )

    finally:

        consumer.close()


if __name__ == "__main__":
    main()
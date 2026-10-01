import json
from collections import defaultdict
from datetime import datetime

from kafka import KafkaConsumer


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "order-events"


def create_consumer() -> KafkaConsumer:

    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="streamsight-metrics-processor",
        value_deserializer=lambda value: json.loads(
            value.decode("utf-8")
        ),
    )


def main():

    consumer = create_consumer()

    total_orders = 0
    total_revenue = 0.0

    status_counts = defaultdict(
        int
    )

    product_revenue = defaultdict(
        float
    )

    print(
        f"Listening for real-time events on: {KAFKA_TOPIC}"
    )

    try:

        for message in consumer:

            event = message.value

            total_orders += 1

            order_value = float(
                event["order_value"]
            )

            total_revenue += order_value

            status = event["status"]
            product = event["product"]

            status_counts[
                status
            ] += 1

            product_revenue[
                product
            ] += order_value

            print(
                "\n=============================="
            )

            print(
                "STREAMSIGHT REAL-TIME METRICS"
            )

            print(
                "=============================="
            )

            print(
                f"Updated at: {datetime.now().isoformat()}"
            )

            print(
                f"Total orders: {total_orders}"
            )

            print(
                f"Total revenue: ${total_revenue:,.2f}"
            )

            print(
                f"Status counts: {dict(status_counts)}"
            )

            print(
                "Product revenue:"
            )

            for (
                product_name,
                revenue,
            ) in product_revenue.items():

                print(
                    f"  {product_name}: "
                    f"${revenue:,.2f}"
                )

    except KeyboardInterrupt:

        print(
            "\nStopping metrics processor..."
        )

    finally:

        consumer.close()


if __name__ == "__main__":
    main()
import json

from kafka import KafkaConsumer

from app.services.database import insert_order_event


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "order-events"


def create_consumer() -> KafkaConsumer:

    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="streamsight-order-db-consumer",
        value_deserializer=lambda value: json.loads(
            value.decode("utf-8")
        ),
    )


def main():

    consumer = create_consumer()

    print(
        f"Listening to Kafka topic: {KAFKA_TOPIC}"
    )

    print(
        "Saving order events to PostgreSQL..."
    )

    try:

        for message in consumer:

            event = message.value

            insert_order_event(
                event
            )

            print(
                f"Saved order event: "
                f"{event['order_id']} "
                f"| ${event['order_value']:,.2f}"
            )

    except KeyboardInterrupt:

        print(
            "\nStopping database consumer..."
        )

    finally:

        consumer.close()


if __name__ == "__main__":
    main()
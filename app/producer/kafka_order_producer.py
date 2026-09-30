import json
import time

from kafka import KafkaProducer

from app.producer.order_event_generator import (
    generate_order_event,
)


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "order-events"


def create_producer() -> KafkaProducer:

    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda value: json.dumps(
            value
        ).encode(
            "utf-8"
        ),
    )


def main():

    producer = create_producer()

    print(
        "Kafka producer connected."
    )

    print(
        f"Publishing to topic: {KAFKA_TOPIC}"
    )

    try:

        while True:

            event = generate_order_event()

            producer.send(
                KAFKA_TOPIC,
                value=event,
            )

            producer.flush()

            print(
                json.dumps(
                    event,
                    indent=2,
                )
            )

            time.sleep(
                2
            )

    except KeyboardInterrupt:

        print(
            "\nStopping producer..."
        )

    finally:

        producer.close()


if __name__ == "__main__":
    main()
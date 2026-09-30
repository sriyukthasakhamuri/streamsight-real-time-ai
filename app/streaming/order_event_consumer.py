import json

from kafka import KafkaConsumer


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "order-events"


def create_consumer() -> KafkaConsumer:

    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="streamsight-order-consumer",
        value_deserializer=lambda value: json.loads(
            value.decode("utf-8")
        ),
    )


def main():

    consumer = create_consumer()

    print(
        f"Listening to Kafka topic: {KAFKA_TOPIC}"
    )

    try:

        for message in consumer:

            event = message.value

            print(
                "\nReceived order event:"
            )

            print(
                json.dumps(
                    event,
                    indent=2,
                )
            )

    except KeyboardInterrupt:

        print(
            "\nStopping consumer..."
        )

    finally:

        consumer.close()


if __name__ == "__main__":
    main()
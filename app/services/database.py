import psycopg2


DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5433,
    "database": "streamsight",
    "user": "streamsight",
    "password": "streamsight_dev",
}


def get_connection():
    return psycopg2.connect(
        **DB_CONFIG
    )


def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS order_events (
            id SERIAL PRIMARY KEY,
            event_id TEXT UNIQUE NOT NULL,
            order_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price NUMERIC(12, 2) NOT NULL,
            order_value NUMERIC(12, 2) NOT NULL,
            status TEXT NOT NULL,
            event_timestamp TIMESTAMP NOT NULL
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS anomaly_alerts (
            id SERIAL PRIMARY KEY,
            event_id TEXT NOT NULL,
            order_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            product TEXT NOT NULL,
            order_value NUMERIC(12, 2) NOT NULL,
            alert_type TEXT NOT NULL,
            alert_message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    connection.commit()

    cursor.close()
    connection.close()

    print(
        "StreamSight database initialized successfully."
    )


def insert_order_event(event: dict):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO order_events (
            event_id,
            order_id,
            customer_id,
            product,
            quantity,
            unit_price,
            order_value,
            status,
            event_timestamp
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON CONFLICT (event_id)
        DO NOTHING;
        """,
        (
            event["event_id"],
            event["order_id"],
            event["customer_id"],
            event["product"],
            event["quantity"],
            event["unit_price"],
            event["order_value"],
            event["status"],
            event["event_timestamp"],
        ),
    )

    connection.commit()

    cursor.close()
    connection.close()


def insert_anomaly_alert(
    event: dict,
    alert_type: str,
    alert_message: str,
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO anomaly_alerts (
            event_id,
            order_id,
            customer_id,
            product,
            order_value,
            alert_type,
            alert_message
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        );
        """,
        (
            event["event_id"],
            event["order_id"],
            event["customer_id"],
            event["product"],
            event["order_value"],
            alert_type,
            alert_message,
        ),
    )

    connection.commit()

    cursor.close()
    connection.close()


if __name__ == "__main__":
    initialize_database()
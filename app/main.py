from fastapi import FastAPI

from app.services.database import get_connection


app = FastAPI(
    title="StreamSight API",
    description=(
        "Real-time analytics API for orders, "
        "metrics, and anomaly alerts."
    ),
    version="1.0.0",
)


@app.get("/")
def root():

    return {
        "message": "StreamSight Real-Time AI API"
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.get("/orders/recent")
def get_recent_orders(
    limit: int = 10,
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            order_id,
            customer_id,
            product,
            quantity,
            order_value,
            status,
            event_timestamp
        FROM order_events
        ORDER BY id DESC
        LIMIT %s;
        """,
        (
            limit,
        ),
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return [
        {
            "order_id": row[0],
            "customer_id": row[1],
            "product": row[2],
            "quantity": row[3],
            "order_value": float(
                row[4]
            ),
            "status": row[5],
            "event_timestamp": row[6],
        }
        for row in rows
    ]


@app.get("/alerts/recent")
def get_recent_alerts(
    limit: int = 10,
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            order_id,
            customer_id,
            product,
            order_value,
            alert_type,
            alert_message,
            created_at
        FROM anomaly_alerts
        ORDER BY id DESC
        LIMIT %s;
        """,
        (
            limit,
        ),
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return [
        {
            "order_id": row[0],
            "customer_id": row[1],
            "product": row[2],
            "order_value": float(
                row[3]
            ),
            "alert_type": row[4],
            "alert_message": row[5],
            "created_at": row[6],
        }
        for row in rows
    ]


@app.get("/metrics/summary")
def get_metrics_summary():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(
                SUM(order_value),
                0
            ),
            COALESCE(
                AVG(order_value),
                0
            )
        FROM order_events;
        """
    )

    metrics = cursor.fetchone()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM anomaly_alerts;
        """
    )

    alert_count = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return {
        "total_orders": metrics[0],
        "total_revenue": float(
            metrics[1]
        ),
        "average_order_value": round(
            float(
                metrics[2]
            ),
            2,
        ),
        "total_alerts": alert_count,
    }
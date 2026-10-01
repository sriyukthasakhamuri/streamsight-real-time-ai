from langchain_ollama import ChatOllama

from app.services.database import get_connection


MODEL_NAME = "llama3.2:3b"


def get_operational_context() -> dict:

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(order_value), 0),
            COALESCE(AVG(order_value), 0)
        FROM order_events;
        """
    )

    metrics = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            product,
            COUNT(*) AS order_count,
            COALESCE(SUM(order_value), 0) AS revenue
        FROM order_events
        GROUP BY product
        ORDER BY revenue DESC;
        """
    )

    product_rows = cursor.fetchall()

    cursor.execute(
        """
        SELECT
            alert_type,
            COUNT(*)
        FROM anomaly_alerts
        GROUP BY alert_type
        ORDER BY COUNT(*) DESC;
        """
    )

    alert_rows = cursor.fetchall()

    cursor.execute(
        """
        SELECT
            order_id,
            customer_id,
            product,
            order_value,
            alert_type,
            alert_message
        FROM anomaly_alerts
        ORDER BY id DESC
        LIMIT 5;
        """
    )

    recent_alert_rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return {
        "total_orders": metrics[0],
        "total_revenue": float(metrics[1]),
        "average_order_value": round(
            float(metrics[2]),
            2,
        ),
        "products": [
            {
                "product": row[0],
                "order_count": row[1],
                "revenue": float(row[2]),
            }
            for row in product_rows
        ],
        "alert_counts": [
            {
                "alert_type": row[0],
                "count": row[1],
            }
            for row in alert_rows
        ],
        "recent_alerts": [
            {
                "order_id": row[0],
                "customer_id": row[1],
                "product": row[2],
                "order_value": float(row[3]),
                "alert_type": row[4],
                "alert_message": row[5],
            }
            for row in recent_alert_rows
        ],
    }


def generate_ai_insight() -> str:

    context = get_operational_context()

    model = ChatOllama(
        model=MODEL_NAME,
        temperature=0,
    )

    prompt = f"""
You are StreamSight, an AI operations analyst.

Use ONLY the operational data below.

Do not invent causes, customers, trends, or business facts.
Do not claim that a factor caused an anomaly unless the data proves it.
Describe observed patterns, concentrations, and operational signals.

Operational data:

Total orders:
{context["total_orders"]}

Total revenue:
${context["total_revenue"]:,.2f}

Average order value:
${context["average_order_value"]:,.2f}

Product metrics:
{context["products"]}

Alert counts:
{context["alert_counts"]}

Most recent anomaly alerts:
{context["recent_alerts"]}

Create a concise operational summary with exactly these sections:

1. Current Snapshot
2. Key Revenue Signal
3. Anomaly Activity
4. Recommended Attention

Keep the response business-friendly and concise.
"""

    response = model.invoke(
        prompt
    )

    return response.content


if __name__ == "__main__":

    insight = generate_ai_insight()

    print(
        "\nSTREAMSIGHT AI INSIGHT\n"
    )

    print(
        insight
    )
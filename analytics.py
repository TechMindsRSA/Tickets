from database import get_connection


def get_dashboard_stats():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tickets")
    total_tickets = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE status='Open'"
    )
    open_tickets = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE status='Resolved'"
    )
    resolved_tickets = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE priority='Critical'"
    )
    critical_tickets = cursor.fetchone()[0]

    conn.close()

    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "resolved_tickets": resolved_tickets,
        "critical_tickets": critical_tickets
    }

def get_ticket_trend():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT created_at, COUNT(*)
        FROM tickets
        GROUP BY created_at
        ORDER BY created_at
    """)

    data = cursor.fetchall()
    conn.close()

    dates = [row[0] for row in data]
    counts = [row[1] for row in data]

    return dates, counts

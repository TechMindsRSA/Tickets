import datetime

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import pickle
import json
import os
import matplotlib
matplotlib.use('Agg')

import sqlite3
from textblob import TextBlob
from responses import generate_response
from notifications import ( send_admin_email, send_employee_resolution_email )

app = Flask(__name__)
app.secret_key = "ticket_dashboard_secret_2026"

# Load model and vectorizer
with open("model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

with open("vectorizer.pkl", "rb") as vec_file:
    vectorizer = pickle.load(vec_file)

# Home route
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234567890":

            session["admin"] = True

            return redirect("/dashboard")

        return "Invalid Credentials"

    return render_template("login.html")

# Admin dashboard route
@app.route("/dashboard")
def dashboard():

    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, employee_name, employee_id, department, employee_email, ticket_text, category, priority, status,created_at
    FROM tickets
    ORDER BY id DESC
    """)
    tickets = cursor.fetchall()

    cursor.execute("""
    SELECT created_at, COUNT(*)
    FROM tickets
    GROUP BY created_at
    ORDER BY created_at
    """)

    date_data = cursor.fetchall()

    dates = [row[0] for row in date_data]
    counts = [row[1] for row in date_data]
    

    print(tickets)
    alert_tickets = [
    ticket for ticket in tickets
    if ticket[7] in ["High", "Critical"]
    ]

    # Analytics

    total_tickets = len(tickets)

    high_count = sum(1 for t in tickets if t[7] == "High")
    medium_count = sum(1 for t in tickets if t[7] == "Medium")
    low_count = sum(1 for t in tickets if t[7] == "Low")
    critical_count = sum(1 for t in tickets if t[7] == "Critical")


    open_count = sum(1 for t in tickets if t[8] == "Open")
    resolved_count = sum(1 for t in tickets if t[8] == "Resolved")
    conn.close()

    from collections import Counter

    # get all ticket categories (column index 6)
    categories = [ticket[6] for ticket in tickets]

    # count each type
    category_counts = Counter(categories)
    
    top_category = None
    if category_counts:
        top_category = category_counts.most_common(1)[0][0]
    
    # ✅ Automated summary
    summary_text = ""

    if total_tickets == 0:
        summary_text = "No tickets have been recorded."
    else:
        summary_text = f"There are {total_tickets} tickets in total. "

        if open_count > resolved_count:
            summary_text += "More tickets are open than resolved. Immediate attention is required. "
        else:
            summary_text += "Tickets are being handled efficiently. "

        if critical_count > 0:
            summary_text += f"There are {critical_count} critical issues that need urgent resolution. "

        if top_category:
            summary_text += f"The most active department is {top_category}."
    conn.close()

    return render_template(
    "dashboard.html",
    tickets=tickets,
    category_counts=category_counts,
    top_category=top_category,
    summary_text=summary_text,

    total_tickets=total_tickets,
    high_count=high_count,
    medium_count=medium_count,
    low_count=low_count,
    critical_count=critical_count,
    dates=dates,
    counts=counts,

    open_count=open_count,
    resolved_count=resolved_count,

    notification_count=total_tickets,
    alert_tickets=alert_tickets
    )
@app.route("/update_status/<int:ticket_id>/<status>")
def update_status(ticket_id, status):

    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()

    #update status
    cursor.execute("""
    UPDATE tickets
    SET status=?
    WHERE id=?
    """, (status, ticket_id))

    conn.commit()

    #if ticket is resolved notify employee
    if status == "Resolved":

        cursor.execute("""
        SELECT employee_name, employee_email, ticket_text
        FROM tickets
        WHERE id=?
        """, (ticket_id,))

        employee = cursor.fetchone()
        try:
            send_employee_resolution_email(
                employee[1],  # employee_email
                employee[0],  # employee_name
                employee[2]   # ticket_text
            )
        except Exception as e:
            print("EMPLOYEE EMAIL FAILED:", e)

    
    conn.close()

    return redirect("/dashboard")

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file
from flask import request
import sqlite3
import io
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

@app.route('/download_summary')
def download_summary():

    department = request.args.get('department')

    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, employee_name, employee_id, department, employee_email, ticket_text, category, priority, status
    FROM tickets
    """)

    tickets = cursor.fetchall()
    # ✅ Filter by department if selected
    if department:
        tickets = [t for t in tickets if t[6] == department]


    # ✅ Analytics (same as dashboard)
    total_tickets = len(tickets)

    high_count = sum(1 for t in tickets if t[7] == "High")
    medium_count = sum(1 for t in tickets if t[7] == "Medium")
    low_count = sum(1 for t in tickets if t[7] == "Low")
    critical_count = sum(1 for t in tickets if t[7] == "Critical")

    open_count = sum(1 for t in tickets if t[8] == "Open")
    resolved_count = sum(1 for t in tickets if t[8] == "Resolved")

    from collections import Counter
    categories = [t[6] for t in tickets]
    category_counts = Counter(categories)

    top_category = None
    if category_counts:
        top_category = category_counts.most_common(1)[0][0]

    # ✅ recreate summary_text here

    summary_text = ""

    if total_tickets == 0:
        summary_text = "No tickets have been recorded."
    else:
        summary_text = f"There are {total_tickets} tickets in total. "

    if open_count > resolved_count:
        summary_text += "More tickets are open than resolved. Immediate attention is required. "
    else:
        summary_text += "Tickets are being handled efficiently. "

    if critical_count > 0:
        summary_text += f"There are {critical_count} critical issues that need urgent resolution. "

    if top_category:
        summary_text += f"The most active department is {top_category}."

    conn.close()

    # ✅ Create PDF
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    pdf.setFont("Helvetica-Bold", 16)
    title = "Enterprise Service Desk Report"

    if department:
        title = f"{department} Department Report"

    pdf.drawString(50, 750, title)

    y = 720

    # ✅ OVERVIEW TABLE
    overview_data = [
        ["Metric", "Value"],
        ["Total Tickets", total_tickets],
        ["Open Tickets", open_count],
        ["Resolved Tickets", resolved_count],
        ["Critical Tickets", critical_count],
    ]

    overview_table = Table(overview_data)
    overview_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))

    overview_table.wrapOn(pdf, 400, 200)
    overview_table.drawOn(pdf, 50, y-120)

    y -= 160


    # ✅ PRIORITY TABLE
    priority_data = [
        ["Priority", "Count"],
        ["High", high_count],
        ["Medium", medium_count],
        ["Low", low_count],
    ]

    priority_table = Table(priority_data)
    priority_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))

    priority_table.wrapOn(pdf, 400, 200)
    priority_table.drawOn(pdf, 50, y-120)

    y -= 160


    # ✅ DEPARTMENT BLOCK
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Department Insight")
    y -= 20

    pdf.setFont("Helvetica", 12)
    pdf.drawString(70, y, f"Top Department: {top_category}")

    y -= 40


    # ✅ SUMMARY BLOCK
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Summary")
    y -= 20

    pdf.setFont("Helvetica", 12)

    lines = summary_text.split(". ")

    for line in lines:
        if line.strip():
            pdf.drawString(70, y, line.strip())
            y -= 20


    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="weekly_summary.pdf",
        mimetype='application/pdf'
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# Classify ticket route
@app.route("/classify", methods=["POST"])
def classify_ticket():

    try:
        data = request.json
        name = data["name"]
        employeeId = data["employeeId"]
        department = data["department"]
        employeeEmail = data["employeeEmail"]
        original_text = data["text"]

        # Auto-correct spelling
        corrected_text = str(TextBlob(original_text).correct())

        # Vectorize input
        text_vector = vectorizer.transform([corrected_text])

        # Predict category
        prediction = model.predict(text_vector)[0]

        # Priority detection

        critical_keywords = [
        "production has stopped",
        "server is down",
        "system outage",
        "network outage",
        "cannot work",
        "business is down"
        ]

        high_priority_keywords = [
        "not working",
        "computer is not working",
        "laptop is not working",
        "internet down",
        "vpn issue",
        "printer is not working",
        "harassment",
        "harassed",
        "urgent",
        "harassment",
        "emergency",
        "violence",
        "abuse",
        "harssed"
        ]

        medium_priority_keywords = [
        "slow",
        "password reset",
        "salary",
        "delay",
        "complaint",
        "issue"
        ]

        ticket_lower = original_text.lower()

        priority = "Low"

        # Critical priority
        for word in critical_keywords:
            if word in ticket_lower:
                priority = "Critical"

        # High priority
        for word in high_priority_keywords:
            if word in ticket_lower and priority != "Critical":
                priority = "High"

        # Medium priority
        for word in medium_priority_keywords:
            if word in ticket_lower and priority not in ["Critical", "High"]:
                priority = "Medium"

        ai_response = generate_response(
            prediction, priority)

        # Final result
        result = {
            "ticket": original_text,
            "predicted_category": prediction,
            "priority": priority,
            "response": ai_response
        }

        

        # Save to SQLite database
        conn = sqlite3.connect("tickets.db")
        cursor = conn.cursor()

        created_at = datetime.date.today()
        
        cursor.execute("""
        INSERT INTO tickets (
        employee_name,
        employee_id,
        department, 
        employee_email, 
        ticket_text, 
        category, 
        priority,
        status,
        created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, 
        (name, employeeId, department, employeeEmail, original_text, prediction, priority, "Open", created_at))

        conn.commit()
        conn.close()
        if priority in ["High", "Critical"]:

            print("HIGH PRIORITY DETECTED")
            try:
                send_admin_email(
                    name,
                    employeeId,
                    department,
                    original_text,
                    prediction,
                    priority
                )
            except Exception as e:
                print("ADMIN EMAIL FAILED:", e)
        
        return jsonify(result)
    
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500





@app.route("/test")
def test():
    return "Test route works"

print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import pickle
import json
import os
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
    SELECT id, employee_name, employee_id, department, employee_email, ticket_text, category, priority, status
    FROM tickets
    ORDER BY id DESC
    """)

    tickets = cursor.fetchall()
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

    conn.close()

    return render_template(
        "dashboard.html",
        tickets=tickets,
        total_tickets=total_tickets,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
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

        cursor.execute("""
        INSERT INTO tickets (
        employee_name,
        employee_id,
        department, 
        employee_email, 
        ticket_text, 
        category, 
        priority,
        status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, 
        (name, employeeId, department, employeeEmail, original_text, prediction, priority, "Open"))

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
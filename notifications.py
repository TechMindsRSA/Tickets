from http import server
import smtplib
from email.mime.text import MIMEText

def send_admin_email(name, employeeId, department, ticket, category, priority):

    sender_email = "ticketdashboard2026@gmail.com"

    sender_password = "kipetkbifijzalfr"

    admin_email = "217046843@edu.vut.ac.za"

    subject = f"New {priority} Ticket"

    body = f"""
Enterprise Service Desk Alert

Employee Name: {name}
Employee ID: {employeeId}
Department: {department}

Category: {category}
Priority: {priority}

Ticket Description:
{ticket}

Please review this ticket immediately.
"""

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = "Enterprise Service Desk <ticketdashboard2026@gmail.com>"
    msg["To"] = admin_email

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587
    )

    server.starttls()

    server.login(
        sender_email,
        sender_password
    )

    print("Sending email...")

    server.send_message(msg)

    print("Email sent successfully!")

    server.quit()

def send_employee_resolution_email(
    employee_email,
    employee_name,
    ticket_text
):

    sender_email = "ticketdashboard2026@gmail.com"

    sender_password = "kipetkbifijzalfr"

    subject = "Enterprise Service Desk - Ticket Resolution Notice"

    body = f"""
Hello {employee_name},

We are pleased to inform you that your support request has been resolved.

Ticket:
{ticket_text}

If you are still experiencing issues, please submit a new support request.

Kind Regards,

Enterprise Service Desk Team
ticketdashboard2026@gmail.com
"""

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = employee_email

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587
    )

    server.starttls()

    server.login(
        sender_email,
        sender_password
    )

    print("Sending employee email...")

    server.send_message(msg)

    print("Employee notified successfully!")

    server.quit()
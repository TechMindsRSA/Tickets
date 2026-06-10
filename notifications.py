import os
import resend

# Load Resend API Key
resend.api_key = os.getenv("RESEND_API_KEY")

print("RESEND_API_KEY =", os.getenv("RESEND_API_KEY"))


def send_admin_email(
    name,
    employeeId,
    department,
    ticket,
    category,
    priority
):

    print("Sending admin email...")

    response = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": ["phadedumiie@gmail.com"],
        "subject": f"New {priority} Ticket",
        "html": f"""
        <h2>Enterprise Service Desk Alert</h2>

        <p><strong>Employee Name:</strong> {name}</p>
        <p><strong>Employee ID:</strong> {employeeId}</p>
        <p><strong>Department:</strong> {department}</p>

        <p><strong>Category:</strong> {category}</p>
        <p><strong>Priority:</strong> {priority}</p>

        <p><strong>Ticket Description:</strong></p>

        <p>{ticket}</p>
        """
    })

    print("RESEND RESPONSE:", response)
    print("Admin email sent!")


def send_employee_resolution_email(
    employee_email,
    employee_name,
    ticket_text
):

    print("Sending employee resolution email...")

    response = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": [employee_email],
        "subject": "Enterprise Service Desk - Ticket Resolution Notice",
        "html": f"""
        <h2>Enterprise Service Desk</h2>

        <p>Hello {employee_name},</p>

        <p>Your support ticket has been resolved.</p>

        <p><strong>Ticket:</strong></p>

        <p>{ticket_text}</p>

        <p>
        If the issue persists, please submit a new support request.
        </p>

        <p>
        Kind Regards,<br>
        Enterprise Service Desk Team
        </p>
        """
    })

    print("RESEND RESPONSE:", response)
    print("Employee email sent!")
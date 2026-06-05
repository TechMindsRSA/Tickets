def generate_response(category, priority):

    if priority == "Critical":

        return f"""
🚨 CRITICAL INCIDENT

Your {category} request has been classified as CRITICAL.

The relevant support team has been alerted immediately and is actively investigating the issue.

We understand the impact this may have on business operations and will provide updates as soon as possible.
"""

    elif priority == "High":

        return f"""
⚠️ HIGH PRIORITY REQUEST

Your {category} request has been received and marked as HIGH priority.

The support team has been alerted and your issue is receiving immediate attention.

A technician or specialist will contact you shortly if additional information is required.
"""

    elif priority == "Medium":

        return f"""
📌 MEDIUM PRIORITY REQUEST

Your {category} request has been logged successfully.

The relevant team has been alerted and your request has been placed in the service queue for review.

We appreciate your patience while the team investigates the matter.
"""

    else:

        return f"""
✅ REQUEST RECEIVED

Your {category} request has been submitted successfully.

The request has been recorded and assigned to the appropriate team.

You will be contacted if further information is required.
"""
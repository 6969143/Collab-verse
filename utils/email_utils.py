from flask_mail import Message, Mail
from flask import current_app

def send_email(to_email, subject, body, html_body=None):
    """Send email using Flask-Mail"""
    try:
        # Get the mail instance from the current app
        if 'mail' in current_app.extensions:
            mail = current_app.extensions['mail']
        else:
            # Fallback: create mail instance if not available
            mail = Mail(current_app)
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body
        )
        
        if html_body:
            msg.html = html_body
        
        # Send email
        mail.send(msg)
        
        print(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_project_invitation(inviter_name, project_name, project_id, recipient_email):
    """Send project invitation email"""
    subject = f"Project Invitation: {project_name}"
    
    # Plain text version
    body = f"""
Hello!

You have been invited to join the project "{project_name}" by {inviter_name}.

To accept this invitation, please visit:
http://127.0.0.1:5000/projects/{project_id}

Best regards,
Your Project Management Team
    """.strip()
    
    # HTML version
    html_body = f"""
    <html>
    <body>
        <h2>Project Invitation</h2>
        <p>Hello!</p>
        <p>You have been invited to join the project <strong>{project_name}</strong> by {inviter_name}.</p>
        <p>To accept this invitation, please click the link below:</p>
        <p><a href="http://127.0.0.1:5000/projects/{project_id}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Join Project</a></p>
        <p>Best regards,<br>Your Project Management Team</p>
    </body>
    </html>
    """
    
    return send_email(recipient_email, subject, body, html_body)

def send_password_recovery(user_email, reset_token):
    """Send password recovery email with reset link"""
    reset_url = f"http://127.0.0.1:5000/auth/reset_password/{reset_token}"
    subject = "Password Recovery - Reset Your Password"
    
    # Plain text version
    body = f"""
Hello!

You have requested to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in 1 hour for security reasons.

If you didn't request this password reset, please ignore this email.

Best regards,
Your Project Management Team
    """.strip()
    
    # HTML version
    html_body = f"""
    <html>
    <body>
        <h2>Password Recovery</h2>
        <p>Hello!</p>
        <p>You have requested to reset your password. Click the button below to set a new password:</p>
        <p><a href="{reset_url}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
        <p><strong>This link will expire in 1 hour for security reasons.</strong></p>
        <p>If you didn't request this password reset, please ignore this email.</p>
        <p>Best regards,<br>Your Project Management Team</p>
    </body>
    </html>
    """
    
    return send_email(user_email, subject, body, html_body)

def send_project_application(applicant_name, applicant_email, project_name, project_id, message, owner_email):
    """Send project application email to project owner"""
    subject = f"Project Application: {project_name}"
    
    # Plain text version
    body = f"""
Hello Project Owner!

{applicant_name} ({applicant_email}) has applied to join your project "{project_name}".

Application Details:
- Applicant: {applicant_name}
- Email: {applicant_email}
- Project: {project_name}

Message from applicant:
{message if message else "No message provided"}

To review and manage this application, please visit:
http://127.0.0.1:5000/projects/{project_id}

You can accept or reject this application through the project management interface.

Best regards,
Your Project Management Team
    """.strip()
    
    # HTML version
    html_body = f"""
    <html>
    <body>
        <h2>Project Application</h2>
        <p>Hello Project Owner!</p>
        <p><strong>{applicant_name}</strong> ({applicant_email}) has applied to join your project <strong>{project_name}</strong>.</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h4>Application Details:</h4>
            <ul>
                <li><strong>Applicant:</strong> {applicant_name}</li>
                <li><strong>Email:</strong> {applicant_email}</li>
                <li><strong>Project:</strong> {project_name}</li>
            </ul>
        </div>
        
        <div style="background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h4>Message from applicant:</h4>
            <p>{message if message else "No message provided"}</p>
        </div>
        
        <p>To review and manage this application, please click the button below:</p>
        <p><a href="http://127.0.0.1:5000/projects/{project_id}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Review Application</a></p>
        
        <p>You can accept or reject this application through the project management interface.</p>
        <p>Best regards,<br>Your Project Management Team</p>
    </body>
    </html>
    """
    
    return send_email(owner_email, subject, body, html_body)

def send_role_application_notification(application):
    """Send notification to admin about new role application"""
    subject = f"New Role Application: {application.applicant.full_name}"
    
    # Plain text version
    body = f"""
Hello Admin!

A new role application has been submitted.

Application Details:
- Applicant: {application.applicant.full_name} ({application.applicant.email})
- Requested Role: {application.requested_role}
- Reason: {application.reason}
- Experience: {application.experience}
- Skills: {application.skills}

To review this application, please visit the admin dashboard.

Best regards,
Your Project Management Team
    """.strip()
    
    # HTML version
    html_body = f"""
    <html>
    <body>
        <h2>New Role Application</h2>
        <p>Hello Admin!</p>
        <p>A new role application has been submitted.</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h4>Application Details:</h4>
            <ul>
                <li><strong>Applicant:</strong> {application.applicant.full_name} ({application.applicant.email})</li>
                <li><strong>Requested Role:</strong> {application.requested_role}</li>
                <li><strong>Reason:</strong> {application.reason}</li>
                <li><strong>Experience:</strong> {application.experience}</li>
                <li><strong>Skills:</strong> {application.skills}</li>
            </ul>
        </div>
        
        <p>To review this application, please visit the admin dashboard.</p>
        <p>Best regards,<br>Your Project Management Team</p>
    </body>
    </html>
    """
    
    # Send to admin (you might want to get admin email from config or database)
    admin_email = "admin@projecttracker.com"
    return send_email(admin_email, subject, body, html_body)

def send_role_application_response(application):
    """Send response to applicant about their role application"""
    status_text = "approved" if application.status == "approved" else "rejected"
    subject = f"Role Application {status_text.title()}: {application.requested_role}"
    
    # Plain text version
    body = f"""
Hello {application.applicant.full_name}!

Your application for the role of {application.requested_role} has been {status_text}.

Application Details:
- Requested Role: {application.requested_role}
- Status: {application.status.title()}

{f"Admin Notes: {application.admin_notes}" if application.admin_notes else ""}

Best regards,
Your Project Management Team
    """.strip()
    
    # HTML version
    html_body = f"""
    <html>
    <body>
        <h2>Role Application {status_text.title()}</h2>
        <p>Hello {application.applicant.full_name}!</p>
        <p>Your application for the role of <strong>{application.requested_role}</strong> has been <strong>{status_text}</strong>.</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h4>Application Details:</h4>
            <ul>
                <li><strong>Requested Role:</strong> {application.requested_role}</li>
                <li><strong>Status:</strong> {application.status.title()}</li>
            </ul>
        </div>
        
        {f'<div style="background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 15px 0;"><h4>Admin Notes:</h4><p>{application.admin_notes}</p></div>' if application.admin_notes else ''}
        
        <p>Best regards,<br>Your Project Management Team</p>
    </body>
    </html>
    """
    
    return send_email(application.applicant.email, subject, body, html_body) 
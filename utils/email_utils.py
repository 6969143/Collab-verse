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
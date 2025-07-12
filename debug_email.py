from flask import Flask
from flask_mail import Mail, Message
from config import Config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_direct_smtp():
    """Test direct SMTP connection to Gmail"""
    print("=== Testing Direct SMTP Connection ===")
    try:
        # Get config values
        username = Config.MAIL_USERNAME
        password = Config.MAIL_PASSWORD
        server = Config.MAIL_SERVER
        port = Config.MAIL_PORT
        
        print(f"Server: {server}:{port}")
        print(f"Username: {username}")
        print(f"Password: {'*' * len(password)} (length: {len(password)})")
        
        # Test SMTP connection
        smtp = smtplib.SMTP(server, port)
        smtp.starttls()
        smtp.login(username, password)
        
        # Create and send test email
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = username  # Send to yourself
        msg['Subject'] = 'Direct SMTP Test Email'
        
        body = 'This is a test email sent via direct SMTP connection.'
        msg.attach(MIMEText(body, 'plain'))
        
        text = msg.as_string()
        smtp.sendmail(username, username, text)
        smtp.quit()
        
        print("✅ Direct SMTP test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Direct SMTP test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_flask_mail():
    """Test Flask-Mail functionality"""
    print("\n=== Testing Flask-Mail ===")
    try:
        app = Flask(__name__)
        app.config.from_object(Config)
        
        mail = Mail(app)
        
        with app.app_context():
            msg = Message(
                subject='Flask-Mail Test Email',
                recipients=[Config.MAIL_USERNAME],
                body='This is a test email sent via Flask-Mail.'
            )
            
            mail.send(msg)
            print("✅ Flask-Mail test successful!")
            return True
            
    except Exception as e:
        print(f"❌ Flask-Mail test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def check_config():
    """Check configuration values"""
    print("\n=== Configuration Check ===")
    print(f"MAIL_SERVER: {Config.MAIL_SERVER}")
    print(f"MAIL_PORT: {Config.MAIL_PORT}")
    print(f"MAIL_USE_TLS: {Config.MAIL_USE_TLS}")
    print(f"MAIL_USERNAME: {Config.MAIL_USERNAME}")
    print(f"MAIL_PASSWORD: {'*' * len(Config.MAIL_PASSWORD)} (length: {len(Config.MAIL_PASSWORD)})")
    print(f"MAIL_DEFAULT_SENDER: {Config.MAIL_DEFAULT_SENDER}")
    
    # Check if password looks like an app password
    if len(Config.MAIL_PASSWORD) != 16:
        print("⚠️  Warning: App password should be 16 characters long")
    if ' ' in Config.MAIL_PASSWORD:
        print("⚠️  Warning: App password should not contain spaces")

def main():
    print("🔍 Email Debug Test")
    print("=" * 50)
    
    check_config()
    
    # Test both methods
    smtp_success = test_direct_smtp()
    flask_success = test_flask_mail()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print(f"Direct SMTP: {'✅ Success' if smtp_success else '❌ Failed'}")
    print(f"Flask-Mail: {'✅ Success' if flask_success else '❌ Failed'}")
    
    if smtp_success or flask_success:
        print("\n✅ Email was sent successfully!")
        print("📧 Check your inbox and spam folder")
        print("📧 If not received, check Gmail settings:")
        print("   - 2-Step Verification enabled")
        print("   - App password generated correctly")
        print("   - Less secure app access (if using regular password)")
    else:
        print("\n❌ Both email methods failed")
        print("🔧 Troubleshooting steps:")
        print("   1. Verify Gmail App Password is correct")
        print("   2. Ensure 2-Step Verification is enabled")
        print("   3. Check if App Password was generated for 'Mail'")
        print("   4. Try generating a new App Password")

if __name__ == "__main__":
    main() 
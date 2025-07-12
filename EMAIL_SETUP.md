# Email Setup Guide

## Configure Gmail for Sending Emails with Flask-Mail

To send emails from `pavanchandu9391@gmail.com` using Flask-Mail, follow these steps:

### 1. Enable 2-Step Verification
1. Go to your Google Account settings: https://myaccount.google.com/
2. Navigate to Security
3. Enable 2-Step Verification if not already enabled

### 2. Generate App Password
1. Go to Security > App passwords
2. Select "Mail" as the app
3. Click "Generate"
4. Copy the 16-character password (without spaces)

### 3. Set Environment Variables
Create a `.env` file in your project root with the following content:

```
# Flask Configuration
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///tracker.db

# Email Configuration (Gmail) - Flask-Mail
MAIL_USERNAME=pavanchandu9391@gmail.com
MAIL_PASSWORD=your-16-character-app-password
MAIL_DEFAULT_SENDER=pavanchandu9391@gmail.com
```

### 4. Verify Dependencies
Flask-Mail is already included in requirements.txt. If you need to install it manually:

```bash
pip install Flask-Mail
```

### 5. How It Works
The system now uses Flask-Mail which:
- Integrates seamlessly with Flask applications
- Handles SMTP connections automatically
- Provides clean, simple API for sending emails
- Supports both plain text and HTML emails
- Uses the configuration from config.py

### 6. Test Email Functionality
Once configured, the system will:
- Send password reset emails when users request them
- Send project invitation emails
- Use proper HTML formatting for better email appearance
- Handle email sending errors gracefully

### Security Notes:
- Never commit your `.env` file to version control
- The app password is different from your regular Gmail password
- App passwords are more secure for application use
- You can revoke app passwords anytime from Google Account settings

### Troubleshooting:
- If emails don't send, check the console for error messages
- Ensure 2-Step Verification is enabled
- Verify the app password is correct
- Check that the `.env` file is in the project root directory
- Flask-Mail will automatically use the configuration from config.py

### Code Structure:
- `run.py`: Initializes Flask-Mail and stores it in app.extensions
- `utils/email_utils.py`: Uses Flask-Mail to send emails
- `config.py`: Contains email configuration settings
- Environment variables override config defaults for security 
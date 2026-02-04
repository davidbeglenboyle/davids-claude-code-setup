# Sendemail Skill Setup (Gmail SMTP)

How to set up Gmail SMTP for sending email notifications.

## Overview

This skill sends emails via Gmail's SMTP server. You'll need:
1. A Gmail account
2. An App Password (not your regular password)
3. The sendemail script configured with your credentials

## Setup Steps

### 1. Enable 2-Step Verification

App Passwords require 2-Step Verification:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click **2-Step Verification**
3. Follow the setup process if not already enabled

### 2. Create an App Password

1. Go to [Google Account App Passwords](https://myaccount.google.com/apppasswords)
2. Click **Select app** → Choose "Mail"
3. Click **Select device** → Choose "Other (Custom name)"
4. Enter a name like "Claude Code"
5. Click **Generate**
6. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)
7. **Save it securely** — you can't view it again

### 3. Store Credentials

```bash
# Create secrets directory
mkdir -p ~/.config/secrets

# Save app password (remove spaces)
echo "xxxxyyyyzzzzwwww" > ~/.config/secrets/gmail-app-password
chmod 600 ~/.config/secrets/gmail-app-password

# Save your email address
echo "your.email@gmail.com" > ~/.config/secrets/gmail-sender-email
chmod 600 ~/.config/secrets/gmail-sender-email
```

### 4. Create the Sendemail Script

Create `~/.claude/bin/sendemail`:

```bash
#!/bin/bash
# Send email via Gmail SMTP

# Read credentials
APP_PASSWORD=$(cat ~/.config/secrets/gmail-app-password)
SENDER_EMAIL=$(cat ~/.config/secrets/gmail-sender-email)
DEFAULT_TO="$SENDER_EMAIL"  # Default: send to yourself

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--subject) SUBJECT="$2"; shift 2 ;;
        -b|--body) BODY="$2"; shift 2 ;;
        -f|--body-file) BODY=$(cat "$2"); shift 2 ;;
        -t|--to) TO="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Read from stdin if no body provided
if [ -z "$BODY" ]; then
    BODY=$(cat)
fi

TO="${TO:-$DEFAULT_TO}"

# Validate
if [ -z "$SUBJECT" ]; then
    echo "Error: Subject required (-s or --subject)"
    exit 1
fi

# Send via Python (more reliable than curl for SMTP)
python3 << EOF
import smtplib
from email.mime.text import MIMEText

msg = MIMEText('''$BODY''')
msg['Subject'] = '''$SUBJECT'''
msg['From'] = '$SENDER_EMAIL'
msg['To'] = '$TO'

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login('$SENDER_EMAIL', '$APP_PASSWORD')
    server.send_message(msg)

print(f"✅ Email sent to $TO")
EOF
```

Make it executable:

```bash
chmod +x ~/.claude/bin/sendemail
```

### 5. Test the Setup

```bash
~/.claude/bin/sendemail -s "Test from Claude Code" -b "If you see this, email is working!"
```

Check your inbox.

## Multi-Machine Setup

App passwords are not machine-specific — sync them:

```bash
# Store in synced secrets directory
mv ~/.config/secrets/gmail-app-password ~/Dropbox/.secrets/
mv ~/.config/secrets/gmail-sender-email ~/Dropbox/.secrets/

# Symlink to standard location (if not already done)
ln -s ~/Dropbox/.secrets ~/.config/secrets
```

Both machines can then send email.

## Security Notes

1. **App Passwords are per-app** — revoke this one if compromised without affecting your main password
2. **Don't commit credentials** — keep them in `~/.config/secrets/`, not in scripts
3. **Rotate periodically** — create a new App Password yearly and delete the old one

## Troubleshooting

### "Authentication failed"
1. Verify App Password is correct (no spaces)
2. Ensure 2-Step Verification is still enabled
3. Check that "Less secure apps" isn't blocking (shouldn't affect App Passwords)

### "Connection refused"
1. Check internet connection
2. Verify port 465 isn't blocked by firewall
3. Try port 587 with TLS instead of SSL if needed

### "Script not found"
1. Verify script exists: `ls -la ~/.claude/bin/sendemail`
2. Check it's executable: `chmod +x ~/.claude/bin/sendemail`
3. Add to PATH or use full path

## AI Agent Instructions

When setting this up via Claude Code:

1. Cannot create App Password — user must do this in Google Account
2. Can help create the sendemail script once credentials are stored
3. Can test by sending a test email

Tell the user: "Please create a Gmail App Password in your Google Account settings and save it to `~/.config/secrets/gmail-app-password`. Then I can set up the email script."

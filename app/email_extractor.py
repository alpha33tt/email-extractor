import os
import random
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from email.utils import formatdate

app = Flask(__name__)

# Configure email settings for Gmail SMTP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'hewlettpackardenterprise01@gmail.com')  # Your Gmail email address
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'aoarlmobvjtablgm')  # Gmail app password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'hewlettpackardenterprise01@gmail.com')

# Initialize Flask-Mail
mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

def get_ip_address():
    # This function can retrieve the client's IP address from the request object.
    return request.remote_addr  # Example for Flask app

def strip_html_tags(html):
    """Remove HTML tags and return plain text."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html)

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        from_name = "PAUL MOTIL"  # Set the sender name to PAUL MOTIL
        from_email = "paulmotil235@gmail.com"  # The email address to be used in the "Reply-To"
        recipients = request.form['bcc'].split(',')  # Use 'bcc' as recipients, now they won't see each other
        subject = request.form['subject']
        body = request.form['email-body']
        reply_to = request.form.get('reply-to', from_email)  # Use the 'reply-to' provided or fall back to default

        # Get the plain text version of the email body
        plain_text_body = strip_html_tags(body)

        if not plain_text_body.strip():
            return 'Email body cannot be empty.', 400

        # Prepare the response
        responses = []

        # Loop through the recipients and send them one by one
        for email in recipients:
            msg = Message(
                subject=subject,
                recipients=[email],  # Send to individual recipients
                body=plain_text_body,  # Plain text content
                html=body,  # HTML content
                sender=f"{from_name} <{from_email}>",  # From name and email address
                reply_to=reply_to,  # Set the 'Reply-to' email
                date=formatdate(localtime=True)  # Date header for the email
            )

            # Set headers properly using the Message object attributes
            msg.extra_headers = {
                'X-Mailer': 'CustomMailer/1.0',
                'X-Originating-IP': get_ip_address(),  # Retrieve the client's IP address (optional)
                'Precedence': 'bulk',  # Important to avoid being flagged as spam
                'X-Priority': '3 (Normal)',  # Normal priority
                'X-MSMail-Priority': 'Normal',  # Ensure it's not flagged as high priority
                'X-Content-Type-Options': 'nosniff',
                'X-Entity-Ref-ID': str(random.randint(100000, 999999)),
                'List-Unsubscribe': f'<mailto:unsubscribe@yourdomain.com>',  # Optional: Add unsubscribe link if required
                'Feedback-ID': f"{from_name}:example.com",
                'X-Campaign-ID': str(random.randint(1000, 9999))
            }

            # Handle file attachments (if any)
            if 'attachment' in request.files:
                attachment = request.files['attachment']
                if attachment:
                    msg.attach(attachment.filename, attachment.content_type, attachment.read())

            # Send the email
            mail.send(msg)

            # Wait a bit before sending the next email to simulate sequential sending
            time.sleep(2.5)

            responses.append(f"Email to {email} sent successfully!")

        return jsonify({"status": "success", "responses": responses})

    except Exception as e:
        app.logger.error(f"Error while sending email: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)

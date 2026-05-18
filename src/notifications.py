import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from textwrap import dedent


def build_body(successful_tickers, failed_tickers):
    successful_html = "".join(f"<li>{ticker}</li>" for ticker in successful_tickers)

    failed_html = "".join(f"<li>{ticker}</li>" for ticker in failed_tickers)

    html_body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                color: #333;
            }}

            .container {{
                max-width: 600px;
                margin: auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
            }}

            .success {{
                color: green;
            }}

            .failure {{
                color: red;
            }}

            ul {{
                margin-top: 5px;
            }}
        </style>
    </head>

    <body>
        <div class="container">
            <h2>ETL Process Status Report</h2>

            <p>
                The ETL process for options data has completed.
            </p>

            <h3 class="success">
                Successful tickers ({len(successful_tickers)})
            </h3>

            <ul>
                {successful_html}
            </ul>

            <h3 class="failure">
                Failed tickers ({len(failed_tickers)})
            </h3>

            <ul>
                {failed_html}
            </ul>

            <hr>

            <p>
                Automated ETL Notification System
            </p>
        </div>
    </body>
    </html>
    """

    return html_body


def send_confirmation_email(
    smtp_server,
    smtp_port,
    smtp_username,
    smtp_password,
    sender_email,
    recipient_email,
    subject,
    successful_tickers,
    failed_tickers,
):
    try:
        # Create the email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        body = build_body(successful_tickers, failed_tickers)

        # Add body text
        message.attach(MIMEText(body, "html"))

        # Connect to SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_username, smtp_password)

            # Send email
            server.sendmail(sender_email, recipient_email, message.as_string())

        print("Confirmation email sent successfully.")

    except Exception as e:
        print(f"Failed to send email: {e}")

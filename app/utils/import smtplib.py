from azure.communication.email import EmailClient
from azure.communication.email.models import (
    EmailContect,
    Emailrecipients,
    EmailAddress,
    EmailMessage
)

# Replace this with your connection string
connection_string = "endpoint=https://tcc123.unitedstates.communication.azure.com/;accesskey=FjpoDng3WSztnrk89qcyxjKbh3TKkWpE6gsTrybzmkv5BQa5wWSwJQQJ99AIACULyCp685a1AAAAAZCSxfULg"

email_client = EmailClient.from_connection_string(connection_string)

# Set up email details
email_content = EmailContent(
    subject="Test Email from Azure Communication Services",
    plain_text="This is a test email sent using Azure Communication Services.",
    html="<!DOCTYPE html><html><body><h1>Test Email</h1><p>This is a test email sent using Azure Communication Services.</p></body></html>"
)

email_recipients = EmailRecipients(
    to=[EmailAddress(email="pascal@machloc.com", display_name="Recipient Name")]
)

message_id = email_client.send(
    from_="patricepascal1@gmail.com",
    content=email_content,

    recipients=email_recipients
)

print(f"Email sent! Message ID: {message_id}")


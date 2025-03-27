from email.message import EmailMessage
import os
import smtplib


class EmailManager:
    
    def __init__(self, smtp: str, port: int, user: str, password: str):
        self.smtp = smtp
        self.port = port
        self.user = user
        self.password = password
        
    
    def send_mail(self, send_to: str, subject: str, text: str, file_paths: list[str]) -> None:
        email = EmailMessage()
        email["From"] = self.user
        email["To"] = send_to
        email["Subject"] = subject
        email.set_content(text)

        # attach files
        for file_path in file_paths:
            with open(file_path, "rb") as file:
                file_data = file.read()
                email.add_attachment(
                    file_data,
                    maintype="application",
                    subtype="octet-stream",
                    filename=os.path.basename(file_path),
                )
        
        server = smtplib.SMTP(self.smtp, port=self.port)
        server.starttls()
        server.login(self.user, self.password)
        server.sendmail(self.user, send_to, email.as_string())
        server.quit()


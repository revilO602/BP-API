import threading

from django.core.mail import send_mail
from django.utils.html import strip_tags


class EmailThread(threading.Thread):
    def __init__(self, subject, html_message, to_address, from_address):
        self.subject = subject
        self.html_message = html_message
        self.plain_message = strip_tags(self.html_message)
        self.to_address = to_address
        self.from_address = from_address
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject, self.plain_message,  self.from_address, [self.to_address],
                  html_message=self.html_message)

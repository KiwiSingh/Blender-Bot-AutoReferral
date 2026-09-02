import random
from time import sleep
import config
import errors
from whatsapp import WhatsAppClient


class ReferralMessenger:
    def __init__(self, client: WhatsAppClient):
        self.whatsapp_bot = client
        self.greeting_template = config.GREETING_TEMPLATE

    def contact_person(self, phone_number: str):
        self.whatsapp_bot.open_chat(phone_number)

    def send_greeting(self, phone_number: str):
        self.contact_person(phone_number)
        self.whatsapp_bot.send_message(self.greeting_template)

    def send_resume(self, resume_path: str = config.RESUME_FILE_PATH):
        self.whatsapp_bot.send_attachment(resume_path)

    def process_all(self, phone_numbers: list[str]):
        for phone_number in phone_numbers:
            try:
                self.send_greeting(phone_number)
                self.send_resume()
                delay = random.uniform(*config.DELAY_BETWEEN_CONTACTS)
                sleep(delay)
            except errors.WhatsAppError as e:
                print(f"Error while contacting {phone_number}: {str(e)}")
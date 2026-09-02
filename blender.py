from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import config
import errors
from whatsapp import WhatsAppClient


class BlenderBot:
    def __init__(self):
        self.whatsapp = WhatsAppClient()

    def query_company(self, company_name: str):
        self.whatsapp.open_whatsapp()
        self.whatsapp.open_chat(config.BLENDER_BOT_NUMBER)
        self.whatsapp.send_message(f"/company {company_name}")

    def get_response(self, delay: int = 5) -> str:
        driver = self.whatsapp.driver
        wait = WebDriverWait(driver, config.MESSAGE_TIMEOUT)

        # Give Blender bot a few seconds to process and post the message
        print(f"Waiting {delay}s for Blender bot to reply...")
        sleep(delay)

        try:
            # WhatsApp rows always have role="row" inside #main
            def find_last_message_text(d):
                # Target copyable text spans or rows inside the active chat
                rows = d.find_elements(By.XPATH, '//*[@id="main"]//div[@role="row"]')
                if not rows:
                    # Fallback to any copyable text element inside the conversation
                    rows = d.find_elements(By.XPATH, '//*[@id="main"]//span[contains(@class, "copyable-text")]')

                if not rows:
                    return False

                # Take the last row rendered at the bottom of the chat
                last_elem = rows[-1]
                text = last_elem.text.strip()
                return text if text else False

            latest_text = wait.until(find_last_message_text)
            return latest_text

        except Exception as e:
            raise errors.BlenderResponseTimeoutError(
                f"Failed to retrieve latest response from Blender bot: {str(e)}"
            )
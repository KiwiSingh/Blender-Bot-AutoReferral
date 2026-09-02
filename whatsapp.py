import os
import sys
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth
import config
import errors


# JS snippet that neuters HTMLInputElement.click() for file inputs only.
# WhatsApp's own UI code calls input.click() on the hidden <input type="file">
# when you pick "Document" from the attach menu, and THAT is what spawns the
# native OS file picker. Selenium has no way to see or dismiss a native OS
# window (it only operates inside the browser DOM), so the only reliable fix
# is to stop that click from ever reaching the OS in the first place. We still
# populate the input afterwards with Selenium's own send_keys(), which sets
# the file directly via the browser driver and never touches the OS dialog.
_SUPPRESS_FILE_DIALOG_JS = """
if (!window.__fileClickPatched) {
    window.__fileClickPatched = true;
    const originalClick = HTMLInputElement.prototype.click;
    HTMLInputElement.prototype.click = function (...args) {
        if (this.type === 'file') {
            // swallow the click; do NOT call the native picker
            return;
        }
        return originalClick.apply(this, args);
    };
}
"""

_RESTORE_FILE_DIALOG_JS = """
if (window.__fileClickPatched && window.__origInputClick) {
    HTMLInputElement.prototype.click = window.__origInputClick;
    window.__fileClickPatched = false;
}
"""


class WhatsAppClient:
    def __init__(self):
        chrome_options = Options()

        chrome_options.binary_location = (
            "/Volumes/Zweidrive/Applications/Google Chrome.app/"
            "Contents/MacOS/Google Chrome"
        )

        profile_dir = os.path.expanduser("~/selenium-chrome-profile")
        chrome_options.add_argument(f"--user-data-dir={profile_dir}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, config.PAGE_TIMEOUT)

        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="MacIntel",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True
        )

    def open_whatsapp(self):
        self.driver.get("https://web.whatsapp.com/")
        print("Waiting for WhatsApp Web to load...")
        try:
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="side"]'))
            )
            print("WhatsApp Web is ready.")
        except Exception:
            print("Main screen not detected automatically; ensure QR is scanned if prompted.")

    def open_chat(self, phone_number: str):
        formatted_number = "".join(filter(str.isdigit, phone_number))
        url = f"https://web.whatsapp.com/send?phone={formatted_number}"
        self.driver.get(url)
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//footer//div[@contenteditable="true"]')
                )
            )
        except Exception as e:
            raise errors.ChatOpenError(f"Failed to open chat with {phone_number}: {str(e)}")

    def send_message(self, message: str):
        try:
            message_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//footer//div[@contenteditable="true"]')
                )
            )
            message_box.click()

            modifier_key = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL
            message_box.send_keys(modifier_key, "a")
            message_box.send_keys(Keys.BACKSPACE)

            lines = message.split("\n")
            for index, line in enumerate(lines):
                message_box.send_keys(line)
                if index < len(lines) - 1:
                    ActionChains(self.driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()

            send_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div/div/div[5]/div/span/div/button/div/div/div[1]/span')
                )
            )
            send_button.click()
        except Exception as e:
            raise errors.MessageSendError(f"Failed to send message: {str(e)}")

    def send_attachment(self, file_path: str):
        if not os.path.isabs(file_path) or not os.path.exists(file_path):
            raise errors.ResumeUploadError(f"File not found at path: {file_path}")

        try:
            # 0. Patch file-input clicks BEFORE we touch anything in WhatsApp's
            #    UI, so that whatever WhatsApp does internally to mount/trigger
            #    the input can never spawn the native OS picker.
            self.driver.execute_script(_SUPPRESS_FILE_DIALOG_JS)

            # 1. Click the '+' attach button to open the drawer
            attach_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//footer//button[@aria-label="Attach"] | //footer//span[@data-icon="plus"]/ancestor::button | //footer//div[@title="Attach"]')
                )
            )
            attach_btn.click()

            # 2. Wait for the Document button to be present
            doc_btn = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//button[@aria-label="Document"] | //li[.//span[contains(text(), "Document")]]')
                )
            )

            # 3. Trigger Document click via JS (sidesteps animation intercept).
            #    Even if this internally calls input.click(), the patch from
            #    step 0 turns that into a no-op for file inputs.
            self.driver.execute_script("arguments[0].click();", doc_btn)
            sleep(0.5)

            # 4. Grab the newly mounted document file input (the one that
            #    accepts '*' or is NOT image-only)
            file_input = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//input[@type="file" and not(@accept="image/*")] | //input[@type="file" and @accept="*"]')
                )
            )

            # 5. Populate it directly through the driver. This sets the file
            #    at the protocol level and never opens (or needs) any dialog.
            file_input.send_keys(file_path)

            # 6. Wait for the preview dialog send button and click it
            send_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[@role="button"]//span[@data-icon="send"] | //span[@data-icon="send"]/ancestor::div[@role="button"] | //*[@id="app"]/div/div/div[3]/div/div[2]/div[2]/div/span/div/div/div/div[2]/div/div[2]/div[2]/span/div/div/span')
                )
            )
            send_btn.click()

            # 7. Wait for preview modal to disappear
            self.wait.until(
                EC.invisibility_of_element_located(
                    (By.XPATH, '//div[@role="button"]//span[@data-icon="send"] | //*[@id="app"]/div/div/div[3]/div/div[2]/div[2]/div/span/div/div/div/div[2]/div/div[2]/div[2]/span/div/div/span')
                )
            )
            sleep(1)

        except Exception as e:
            # Fallback safety net: if a native dialog ever does slip through
            # (e.g. a Chrome build that opens it on mousedown rather than
            # click), Selenium still can't see or close it — it lives outside
            # the browser process entirely. On macOS the only way to dismiss
            # it programmatically is OS-level automation (System Events),
            # not WebDriver. See _dismiss_native_dialog_macos() below.
            if sys.platform == "darwin":
                self._dismiss_native_dialog_macos()
            raise errors.ResumeUploadError(f"Failed to send attachment: {str(e)}")

        finally:
            # Restore normal click behavior so it doesn't leak into unrelated
            # file inputs elsewhere on the page (e.g. profile photo upload).
            self.driver.execute_script(_RESTORE_FILE_DIALOG_JS)

    @staticmethod
    def _dismiss_native_dialog_macos():
        """
        Best-effort fallback: send Escape via macOS System Events to close a
        stray native file picker. Selenium/WebDriver cannot interact with
        native OS windows at all, so this uses AppleScript instead. Requires
        the terminal/process running this script to have Accessibility
        permissions granted in System Settings > Privacy & Security.
        """
        import subprocess
        try:
            subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to key code 53'],
                timeout=3,
                check=False,
            )
        except Exception:
            pass
import inspect
import os

COMPANY = os.getenv("MY_DREAM_COMPANY") # This will vary depending on where you want to apply. Set it using the export command
                                        # in your terminal before running the script. For example, export MY_DREAM_COMPANY="Flipkart"
BLENDER_BOT_NUMBER = os.getenv("BLENDER_BOT_NUMBER") # This is purposefully gatekept, making the script useless unless 
                                                    # you have access to the Blender bot's number. You can set it using 
                                                    # the export command in your terminal before running the script. 
                                                    # For example, export BLENDER_BOT_NUMBER="1234567890"
RESUME_FILE_PATH = os.getenv("RFPATH") # This will be the path to your resume. Ideally, tailor it according to the company 
                                        # you are applying to. Set it using the export command in your terminal before 
                                        # running the script.

GREETING_TEMPLATE = inspect.cleandoc(f"""
    Hello,
    I hope you are doing well. I got your number from the Blender bot. I am looking for jobs in {COMPANY}. Could you please refer me to any suitable openings? I have attached my resume for your reference. Thank you for your time and consideration.

    Thanks and regards,
    Parthasarathi Singh
""")

# I've set my name as my actual name on here, but you can change it to your name as per your requirement.

PAGE_TIMEOUT = 20
MESSAGE_TIMEOUT = 15

DELAY_BETWEEN_CONTACTS = (30, 90) # Don't change these rate limits; they exist to protect your WhatsApp account 
                                # from being flagged for spam. The script will wait for a random duration between
                                # 30 and 90 seconds before contacting the next person.
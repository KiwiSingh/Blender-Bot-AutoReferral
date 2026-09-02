import config
from blender import BlenderBot
import messaging
import parser

if __name__ == "__main__":
    bot = BlenderBot()
    bot.query_company(config.COMPANY)
    raw_response = bot.get_response()
    contacts = parser.parse_phone_numbers_as_list(raw_response)

    messaging_bot = messaging.ReferralMessenger(client=bot.whatsapp)
    messaging_bot.process_all(contacts)
from dotenv import load_dotenv
from os import getenv

load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")
GROUP_ID = getenv("GROUP_ID")

LOCATIONS = [
    "Поклонная 13",
    "Чехова 6",
    "Первомайская 5",
    "Дубовая 18",
    "Центральная 11"
]

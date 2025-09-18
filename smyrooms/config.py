import os

from dotenv import load_dotenv

from shared.config import AppConfig

load_dotenv()


class SmyroomsConfig(AppConfig):
    DISTRIBUTOR_APIKEY: str
    DB_CCENTER: str

    @property
    def database_config(self):
        return {
            "ccenter": {
                "connection": Config.DB_CCENTER,
                "tables": [
                    "reports_bookingsfinancialdata",
                    "reports_bookingsinitialvalues",
                    "reports_specificstopsalesrules",
                    "reports_hotelsfinancials",
                    "reports_clientsrules",
                    "clients_credential",
                    "hotel_hotel",
                    "hotel_chain",
                    "hotel_provider",
                ],
            },
        }


Config = SmyroomsConfig(os.environ)

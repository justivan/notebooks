import os

from dotenv import load_dotenv

from shared.config import AppConfig
from shared.database import DatabaseConfig

load_dotenv()


class SmyroomsConfig(AppConfig):
    DISTRIBUTOR_APIKEY: str
    DB_CCENTER: str

    MICROSOFT_CLIENT_ID: str
    MICROSOFT_TENANT_ID: str
    MICROSOFT_CLIENT_SECRET: str

    @property
    def database_config(self):
        return DatabaseConfig(
            databases={
                "ccenter": {
                    "connection": Config.DB_CCENTER,
                    "tables": [
                        "reports_bookingsfinancialdata",
                        "reports_bookingsinitialvalues",
                        "reports_specificstopsalesrules",
                        "reports_hotelsfinancials",
                        "reports_clientsrules",
                        "clients_client",
                        "clients_credential",
                        "hotel_hotel",
                        "hotel_chain",
                        "hotel_provider",
                        "reports_calendar",
                    ],
                },
            },
            default_timezone="Europe/Madrid",
        )


Config = SmyroomsConfig(os.environ)

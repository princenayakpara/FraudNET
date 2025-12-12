from pydantic import BaseModel

class Transaction(BaseModel):
    amount: float
    device_trust: str
    country: str
    home_country: str
    hour: int

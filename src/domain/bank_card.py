from pydantic import BaseModel, Field, ConfigDict


class BankCard(BaseModel):
    """Domain Entity - Core business object."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    issuer_name: str = Field(..., description="Name of the bank")
    payment_network: str = Field(..., description="Payment network (e.g., Visa, Mastercard, JCB, Napas)")
    card_number: str = Field(..., description="Full card number")
    cardholder_name: str = Field(..., description="Cardholder's name")
    expiry_date: str = Field(..., description="MM/YY or MM/YYYY")
    card_type: str | None = Field(None, description="Card function type (e.g., credit, debit, prepaid, atm)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0.0 - 1.0")

    def is_valid(self) -> bool:
        """Validate card number using Luhn algorithm."""
        digits = [int(d) for d in "".join(filter(str.isdigit, self.card_number))]
        if len(digits) < 13 or len(digits) > 19:
            return False
        for i in range(len(digits) - 2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        return sum(digits) % 10 == 0
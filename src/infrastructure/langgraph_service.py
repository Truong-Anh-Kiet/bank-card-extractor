import os
from application import LLMServiceProtocol
from domain import BankCard
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from typing import TypedDict


class AgentState(TypedDict):
    image_base64: str
    card: BankCard | None
    confidence: float
    retry_count: int


class LangGraphLLMService(LLMServiceProtocol):
    """Infrastructure Adapter - Implements LLM + LangGraph using OpenAI GPT-4o."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

    async def extract_from_image(self, image_base64: str) -> BankCard:
        def vision_node(state: AgentState) -> dict:
            image_url = f"data:image/jpeg;base64,{state['image_base64']}"
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": """You are an expert in extracting structured information from bank card images.
Extract the following fields accurately from the provided image:
- bank_name: Full name of the issuing bank (e.g., "JPMorgan Chase" or "HSBC").
- payment_network: Payment network or logo type (e.g., "Visa", "Mastercard", "JCB", "American Express", "Napas").
- card_number: Full card number (16-19 digits, without spaces).
- cardholder_name: Name of the cardholder (e.g., "JOHN DOE").
- expiry_date: Expiration date in MM/YY or MM/YYYY format.
- card_type: Card function type if visible (e.g., "credit", "debit", "prepaid", "atm"); set to null if unclear.
- confidence: Your confidence score as a float between 0.0 and 1.0 (1.0 for perfect match).

If a field is unclear or missing, set it to null and lower the confidence accordingly.
Return only the structured JSON object matching the BankCard schema. Do not include any additional text or explanations."""
                    },
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]
            )
            result = self.llm.with_structured_output(BankCard).invoke([message])
            if hasattr(result, 'parsed'):
                parsed_result = result.parsed
            else:
                parsed_result = result

            return {"card": parsed_result, "confidence": parsed_result.confidence}

        def validate_node(state: AgentState) -> dict:
            card = state["card"]
            new_confidence = card.confidence * (0.95 if card.is_valid() else 0.6)
            return {"confidence": new_confidence}

        graph = StateGraph(AgentState)
        graph.add_node("vision", vision_node)
        graph.add_node("validate", validate_node)
        graph.set_entry_point("vision")
        graph.add_edge("vision", "validate")
        graph.add_edge("validate", END)

        app = graph.compile()
        result = app.invoke({
            "image_base64": image_base64,
            "retry_count": 0,
            "confidence": 0.0,
        })
        return result["card"]
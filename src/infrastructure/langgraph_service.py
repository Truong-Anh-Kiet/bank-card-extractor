import os
from application import LLMServiceProtocol
from domain import BankCard
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from typing import TypedDict


class AgentState(TypedDict):
    """State for the LangGraph agent."""
    image_base64: str
    card: BankCard | None
    confidence: float

class LangGraphLLMService(LLMServiceProtocol):
    """Infrastructure Adapter - Implements LLM + LangGraph using OpenAI GPT-4o."""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in .env")
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            openai_api_key=api_key,
        )

    async def extract_from_image(self, image_base64: str) -> BankCard:
        def vision_node(state: AgentState) -> dict:
            image_url = f"data:image/jpeg;base64,{state['image_base64']}"

            text_prompt = """You are a world-class bank card OCR specialist with deep expertise in physical cards.

                Your task is to extract information from the provided card image with maximum accuracy.

                Return ONLY a valid JSON object that strictly matches the BankCard schema. No explanations, no markdown, no extra text.

                ### Fields to extract:

                - issuer_name: Exact full issuer name (not co-brand name) exactly as printed on the card, preserving original language and characters. Never shorten, translate, or normalize. If the card has no issuer name, set to null.
                - payment_network: Exact network/brand: Visa, Mastercard, JCB, American Express, UnionPay, Napas, Discover, etc. Only if explicitly stated on the card; otherwise null.
                - card_number: Full card number (13-19 digits only). Remove ALL spaces, dashes, or separators. If the card number is partially obscured, return only the visible digits and set confidence lower.
                - cardholder_name: Exact name as printed on the card, preserving original language and characters. If the card has no name, set to null.
                - expiry_date: Expiration date in "MM/YY" format. If the card has no expiry, set to null.
                - card_type: "credit", "debit", "prepaid", "ATM", etc. Only if explicitly stated on the card; otherwise null.
                - confidence: Float between 0.0 and 1.0. Start with 1.0 for a perfect, clear card. Reduce confidence for any issues:
                    - Blurry, low-quality, or damaged images → reduce confidence.
                    - Partially obscured or unreadable fields → reduce confidence proportionally.
                    - Unusual layouts or non-standard cards → reduce confidence.

                ### Strict Rules:
                - Never guess or hallucinate values.
                - If a field is truly unreadable or missing → set to null and reduce confidence.
                - Support every international bank equally well.
                - Handle rotated, reflected, or low-quality images intelligently.

                Output only the clean JSON object.
            """

            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": text_prompt
                    },
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]
            )

            try:
                result = self.llm.with_structured_output(BankCard).invoke([message])
                parsed_result = result
            except Exception:
                parsed_result = BankCard(
                    issuer_name='Unknown',
                    payment_network='Unknown',
                    card_number='Unknown',
                    cardholder_name='Unknown',
                    expiry_date='Unknown',
                    card_type='Unknown',
                    confidence=0.0
                )
            return {"card": parsed_result, "confidence": parsed_result.confidence}

        def validate_node(state: AgentState) -> dict:
            card = state["card"]
            multiplier = 0.95 if card.is_valid() else 0.6
            card.confidence *= multiplier
            return {"card": card, "confidence": card.confidence}

        graph = StateGraph(AgentState)
        graph.add_node("vision", vision_node)
        graph.add_node("validate", validate_node)
        graph.set_entry_point("vision")
        graph.add_edge("vision", "validate")
        graph.add_edge("validate", END)

        app = graph.compile()
        result = app.invoke({
            "image_base64": image_base64,
            "confidence": 0.0,
        })
        return result["card"]
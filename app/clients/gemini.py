from ..utils import GEMINI_API_KEY, GEMINI_SYSTEM_INSTRUCTIONS_PATH
import logging
import json
from app.exceptions import GeminiAPIError
from google import genai
from google.genai import types


class GeminiClient:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash-lite"
        self.system_instructions = open(
            GEMINI_SYSTEM_INSTRUCTIONS_PATH, "r"
        ).read()

    def generate_content_config(self, products):
        return types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=genai.types.Schema(
                type=genai.types.Type.OBJECT,
                properties={
                    "products": genai.types.Schema(
                        type=genai.types.Type.ARRAY,
                        items=genai.types.Schema(
                            type=genai.types.Type.OBJECT,
                            required=["name", "quantity"],
                            properties={
                                "name": genai.types.Schema(
                                    type=genai.types.Type.STRING,
                                ),
                                "quantity": genai.types.Schema(
                                    type=genai.types.Type.INTEGER,
                                ),
                            },
                        ),
                    ),
                },
            ),
            system_instruction=[
                types.Part.from_text(
                    text=self.__insert_products(products)),
            ],
        )

    def __insert_products(self, products):
        text = ", ".join(products)
        return self.system_instructions.replace("{{product_names}}", text)

    def extract_products(self, ad_title, ad_description, products):
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=f"Title: {ad_title}\nDescription: {ad_description}"),
                ],
            ),
        ]

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=self.generate_content_config(products),
            )
        except Exception as e:
            logging.error(f"Error fetching from Gemini: {e}")
            raise GeminiAPIError(f"Failed to fetch data from Gemini API. {e}")

        text = response.text
        obj = json.loads(text)
        products = obj.get("products", [])
        return products


if __name__ == "__main__":
    client = GeminiClient()
    products = ['1750', 'universal', '520', '530', '510',
                        '3000', '4040', '4020', '546', '6660', 'dvb', '310', '450']

    text = ", ".join(products)

    system_instructions = open(
        GEMINI_SYSTEM_INSTRUCTIONS_PATH, "r"
    ).read()
    system_instructions = system_instructions.replace(
        "{{product_names}}", text)
    print(system_instructions)

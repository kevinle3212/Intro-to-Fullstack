# _____________________________________ Module 5 _____________________________________ #

from openai import OpenAI, AuthenticationError
import os
from pathlib import Path
from dotenv import load_dotenv

from pprint import pprint 

class AI:

    def __init__(self, model="gpt-4o-mini") -> None:
        # Load key securely
        self.key = self.__set_key()
        self.client = self.__set_client()
        self.model = model

    def __set_key(self):
        """
        Retrieves API key from environment variables or your secrets manager.
        """
        key = ...
        if not key:
            raise ValueError("OPEN_AI key not found.")
        return key

    def __set_client(self):
        """
        Initializes an authenticated OpenAI client.
        """
        try:
            client = OpenAI(api_key=self.key)
            return client
        except Exception as error:
            raise RuntimeError(f"Error initializing OpenAI client: {error}")

    def request_query(self, prompt: str):
        """
        Sends a text request to the OpenAI Responses API.
        """
        if not self.client:
            return {"message": "Client not initialized", "response": None}

        if not prompt or not isinstance(prompt, str):
            return {"message": "Invalid prompt", "response": None}

        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt
            )

            # Extract assistant message
            content = response.output_text
            return {"message": "success", "response": content}

        except AuthenticationError:
            return {"message": "Invalid API key", "response": None}

        except Exception as e:
            return {"message": "Error sending prompt", "response": str(e)}


if __name__ == "__main__":
    model = AI()
    ticker = input("Enter Ticker: ")

    payload = model.request_query(
                        prompt = f"""
                You are an experienced equity analyst.

                Write a concise, retail-investor-friendly overview of the stock with ticker "{ticker}".

                Your response must:
                - First, briefly explain what the company does and its main business lines.
                - Then, summarize any notable recent events or themes that may affect the stock (such as earnings trends, product launches, regulatory news, or macro conditions). 
                - Give me links to articles if you find any
                - Then using data give a technical overview, like lows, highs, or any other major numbers 
                - Finally, describe the current overall market sentiment toward this stock (for example: bullish, bearish, mixed, or uncertain) and explain why in qualitative terms.
                

                Constraints:
                - Respond as a single paragraph of 6 to 7 sentences.
                - Do NOT use bullet points, headings, titles, or markdown formatting.
                - Use clear, neutral, professional language and avoid hype.
                - If you are not confident about specific recent events or sentiment, say so explicitly instead of guessing.
                - Do not make up exact prices, dates, or analyst targets.
                -Seperate response in formated text ie headers and indents
            
                """
                    )

    pprint(payload)

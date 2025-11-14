
# _____________________________________ Module 5 _____________________________________ #

# Here we will connect with an OpenAI through its SDK. This will allow us to directly access a 
# functionality that ChatGPT would directly do.

from openai import OpenAI, AuthenticationError # pip install openai
#from backend.utils.support import get_secret
import os

class AI:
    
    def __init__(self, model="gpt-4o") -> None:
    
        self.key = os.getenv("OPENAI_API_KEY")
        self.client = self.__set_client()
        self.model = model

    def __set_client(self):
        client = OpenAI()
        try:
           client = OpenAI()
           return client
        except Exception as error:
            print(f"Error ocurred when intializing the client. Error: {error}")
    
    def __is_valid_response(self, response):
        if not response:
            print("No response to check")
            return
        
        status = response["message"]
        if status == "success":
            return True
        return False
    
    def request_query(self, prompt:str):
        
        if not self.client:
            return {"message": "There was an error getting OpenAI client started", "response": {}}
        if not prompt:
            return {"message": "Prompt set is invalid", "response":{}}
        try:
            reponse = self.client.responses.create(
                model = self.model,
                input = prompt
            )
            content = reponse.output_text
            return {"message": "success", "response" : content}
        
        except AuthenticationError:
            return {"message":"API key is incorrect. Authentication is invalid", "response":{}}
        except Exception as e:
            return {"message":"There was an error initializing the prompt.", "response":{e}}

        
        
    
            
        
if __name__ == "__main__":
    model = AI()
    ticker = input("Enter Ticker: ")
    payload = model.request_query(f"Give me a short summary on {ticker}, maybe include recent news, lastly what is market sentemin? respond in paragraph form, no bullet points or headers or fancy titles")
    print(payload["response"])
import requests
from typing import List,Any
from core.models.quote_request import QuoteRequest

class QuoteAPI:
    """
    A client to interact with the Hackathon Assurance API.
    """
    BASE_URL = "https://apidevis.onrender.com/api/auto/packs"

    def get_quote(self, request_data: QuoteRequest) -> List[Any]:
        """
        Calls the API to get an insurance quote.

        Args:
            request_data: A Pydantic model containing the request parameters.

        Returns:
            A list of Pydantic models representing the insurance packs.
        """
        try:
            response = requests.get(self.BASE_URL, params=request_data.model_dump())
            response.raise_for_status() 


            try: 
                response_data = response.json()
                results = response_data.get("body", {}).get("result", [])
                return results
            except requests.exceptions.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        
        return []
    
if __name__ == "__main__":
    # 1. Create a request object with the required details
    # This example uses the data from the documentation
    quote_request_data = QuoteRequest(
        n_cin="08478931",
        valeur_venale=60000,
        nature_contrat="n",  # 'n' for Tous Risques (comprehensive)
        nombre_place=5,
        valeur_a_neuf=60000,
        date_premiere_mise_en_circulation="2022-02-28",
        capital_bris_de_glace=900,
        capital_dommage_collision=60000,
        puissance=6,
        classe=3
    )

    # 2. Instantiate the API client
    api_client = QuoteAPI()

    # 3. Call the API to get the quote
    quotes = api_client.get_quote(quote_request_data)
    print(quotes)

    
   
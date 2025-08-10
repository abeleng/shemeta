import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

API_KEY = 'AIzaSyAE6WwQBM7I3sTwb2JY1Iw777OSaONV7bQ'

class FarmerProfile(BaseModel):
    name: str
    location: str
    soil_type: str
    rainfall: str
    preferred_crops: Optional[str] = None
    farm_size: Optional[str] = None

class CropRecommendation:
    def __init__(self, farmer_json):
        self.farmer = farmer_json

        load_dotenv()
        self.api_key = API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name='gemini-2.0-flash-exp')

    def generate_crop_message(self):
        prompt = f"""
You are an agricultural expert helping Ethiopian farmers choose the best crops for their land.
Below is the farmer's profile in JSON:
{self.farmer}

Based on the farmer's location, soil type, rainfall, preferred crops, and farm size, write a personalized crop recommendation message for the farmer.
The message should:
- Be written in natural, friendly Amharic.
- Start with the farmer's name.
- Clearly recommend the best crops for their situation.
- Explain why these crops are suitable.
- Offer practical advice for success.
- Only reply in Amharic.
"""
        try:
            print("Generating crop recommendation message in Amharic...")
            parts = [{"text": prompt}]
            response = self.model.generate_content(parts)
            if response.candidates and response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]
                if hasattr(part, 'text'):
                    print("\n--- የእርሻ ምክር መልእክት ---")
                    print(part.text)
                    return part.text
            print("Sorry, I couldn't generate a crop recommendation message.")
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    farmer_json = {
        "name": "አቶ ተስፋዬ ወልደማሪያም",
        "location": "አዲስ አበባ አካባቢ",
        "soil_type": "ተስማሚ የገለባ መሬት",
        "rainfall": "መካከለኛ",
        "preferred_crops": "በስንዴ፣ በተኸላ",
        "farm_size": "3 ሄክታር"
    }

    rec = CropRecommendation(farmer_json)
    rec.generate_crop_message()
import os
import json
import pandas as pd
from datetime import datetime
from google import genai
from google.genai import types

# 1. GitHub Secret se safe tarike se API key nikalna
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 2. Strict Sawaal
sawaal = """
PC Hotel Karachi ka current per night room rent kya chal raha hai? 
Live internet par search karo aur mujhe sirf ek single line json output do, bilkul aese:
{"hotel": "PC Hotel Karachi", "price": 125, "source": "Expedia"}
"""

# 3. Live Google Search Run
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=sawaal,
    config=types.GenerateContentConfig(
        tools=[{"google_search": {}}],
        temperature=0.1
    )
)

try:
    clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
    data_dict = json.loads(clean_text)
    
    hotel_name = data_dict.get("hotel", "PC Hotel Karachi")
    data_safae = {
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Hotel Name": hotel_name,
        "Price_USD": data_dict.get("price", 0),
        "Source": data_dict.get("source", "Internet Search")
    }
    
    df_naya = pd.DataFrame([data_safae])
    
    # GitHub par pehle se mojood file check karna
    file_name = "hotel_prices_tracker.csv"
    if os.path.exists(file_name):
        df_purana = pd.read_csv(file_name)
        df_final = pd.concat([df_purana, df_naya], ignore_index=True)
    else:
        df_final = df_naya
        
    df_final.to_csv(file_name, index=False)
    print("🎉 Data successfully saved in GitHub environment!")

except Exception as e:
    print("Error parsing data:", e)
  

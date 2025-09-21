from langchain_groq import ChatGroq
import os 

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GROQ_API_KEY')

llm=ChatGroq(groq_api_key=api_key, model="Gemma2-9b-It", streaming=True)
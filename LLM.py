from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
from langchain_community.llms import HuggingFaceEndpoint

load_dotenv()

api_key = os.getenv('HUGGINGFACE_API_KEY')
os.environ['HUGGINGFACEHUB_API_TOKEN'] = api_key

MISTRAL_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

mistral_params = {
                  #"wait_for_model": True, # waits if model is not available in Hugginface serve
                  "do_sample": False, # greedy decoding - temperature = 0
                  "return_full_text": False, # don't return input prompt
                  "max_new_tokens": 1000, # max tokens answer can go upto
                }

llm = HuggingFaceEndpoint(
    endpoint_url=MISTRAL_API_URL,
    task = "text-generation",
    **mistral_params)

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# PDF Path
pdf_path = "D:/GIT/feed_tracker_rss/test_data/Hindalco Industries Limited.pdf"  # Replace with your PDF file path
pdf_text = extract_text_from_pdf(pdf_path)

def chunk_text(text, max_length=2000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

chunks = chunk_text(pdf_text, max_length=2000)

for i,chunk in enumerate(chunks):
    #print(f"Processing Chunk {i+1}")
    print(llm.invoke(f"will the following news have a VERY STRONG impact on stock price? (Answer only 'Yes' or 'No') {chunk}")) #(Answer only 'Yes' or 'No')
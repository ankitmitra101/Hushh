from dotenv import load_dotenv
import os

# Load from .env file explicitly if needed, but load_dotenv() searches in current dir
load_dotenv()

key = os.getenv("GROQ_API_KEY")
print(f"Checking for GROQ_API_KEY...")

if key:
    if key.startswith("gsk_"):
        print(f"SUCCESS: GROQ_API_KEY loaded and starts with 'gsk_' (Length: {len(key)})")
    else:
        print(f"WARNING: GROQ_API_KEY loaded but does not start with 'gsk_' (Value: {key})")
else:
    print("FAILURE: GROQ_API_KEY not found in environment.")

# Also check OPENAI_API_KEY as fallback just in case
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
     print(f"INFO: OPENAI_API_KEY also present: {openai_key[:5]}...")

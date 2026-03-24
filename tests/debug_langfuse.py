# import os
# from dotenv import load_dotenv
# from langfuse import Langfuse

# load_dotenv()

# # Manually grab them to see if they exist
# pk = os.getenv("LANGFUSE_PUBLIC_KEY")
# sk = os.getenv("LANGFUSE_SECRET_KEY")
# host = os.getenv("LANGFUSE_HOST")

# print(f"--- Configuration Check ---")
# print(f"Host: {host}")
# print(f"Public Key starts with: {pk[:7] if pk else 'MISSING'}")
# print(f"Secret Key starts with: {sk[:7] if sk else 'MISSING'}")

# # Initialize
# langfuse = Langfuse(public_key=pk, secret_key=sk, host=host)

# try:
#     if langfuse.auth_check():
#         print("\n✅ CONNECTION SUCCESSFUL!")
#     else:
#         print("\n❌ CONNECTION FAILED: Credentials rejected by server.")
# except Exception as e:
#     print(f"\n❌ ERROR: {e}")

from langfuse import Langfuse

# PASTE YOUR ACTUAL STRINGS HERE DIRECTLY
langfuse = Langfuse(
    public_key="pk-lf-46b071f7-0acc-4c68-9959-f4ed85733e4e",      # Starts with "pk"
    secret_key="sk-lf-7ad935f2-be5e-4f0b-9674-f26a4023e40f",      # Starts with "sk"
    host="https://cloud.langfuse.com"  # Try without the "us." first
)

# LANGFUSE_SECRET_KEY="sk-lf-..."
# LANGFUSE_PUBLIC_KEY="pk-lf-..."
# LANGFUSE_BASE_URL="https://cloud.langfuse.com"

try:
    if langfuse.auth_check():
        print("✅ SUCCESS! The keys are valid.")
    else:
        print("❌ FAILED! Keys rejected.")
except Exception as e:
    print(f"❌ ERROR: {e}")

    
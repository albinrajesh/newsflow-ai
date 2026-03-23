from openai import OpenAI
from app.config import settings

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=settings.openrouter_api_key)

try:
    res = client.chat.completions.create(
        model="stepfun/step-3.5-flash:free",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("SUCCESS:", res.choices[0].message.content)
except Exception as e:
    print("STILL FAILING:", e)
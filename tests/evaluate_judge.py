import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# We use Gemini 2.0 via OpenRouter as our "Elite Judge"
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def evaluate_agent_run(question, context_list, answer):
    # Convert list of contexts to a single string for the prompt
    formatted_context = "\n---\n".join(context_list)
    
    prompt = f"""
    ### ROLE
    You are a Senior AI Quality Engineer. Evaluate the following RAG Agent output.

    ### INPUTS
    - **Question**: {question}
    - **Retrieved Context**: {formatted_context}
    - **Agent's Final Report**: {answer}

    ### METRICS (Score 0.0 to 1.0)
    1. **Faithfulness**: Is every claim in the report supported ONLY by the provided context? (Hallucination check)
    2. **Answer Relevance**: Does the report actually answer the specific question asked?
    3. **Context Precision**: Out of the provided context chunks, how many were useful for the final answer?

    ### OUTPUT FORMAT
    Return ONLY a JSON object with this structure:
    {{
        "scores": {{
            "faithfulness": float,
            "relevance": float,
            "precision": float
        }},
        "reasoning": "A brief explanation of why these scores were given."
    }}
    """
    
    response = client.chat.completions.create(
        model="openrouter/free", # Change this line
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

if __name__ == "__main__":
    # Example data from your 2026 AI Trends run
    sample_q = "What are the key AI trends in 2026?"
    sample_c = [
        "Healthcare AI is maturing into clinical deployment.",
        "Agentic AI is entering the 'trough of disillusionment' in 2026."
    ]
    sample_a = "The AI landscape in 2026 features clinical healthcare AI and the evolution of agentic systems."

    print("\n[EVAL] Starting LLM-as-a-Judge...")
    results = evaluate_agent_run(sample_q, sample_c, sample_a)
    
    print("\n" + "="*50)
    print("FINAL QUALITY SCORES")
    print("="*50)
    print(json.dumps(results, indent=4))
    print("="*50)
import os
import asyncio
from dotenv import load_dotenv
from ragas import EvaluationDataset, SingleTurnSample, evaluate
from ragas.metrics import Faithfulness, ResponseRelevancy, ContextPrecision
from ragas.llms import llm_factory
from openai import OpenAI

load_dotenv()

# 1. Setup your 'Judge' model (using your existing OpenRouter/Gemini setup)
# This ensures Ragas doesn't look for a default OpenAI key
client = OpenAI(
    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("OPENROUTER_API_KEY")
)
# We wrap it so Ragas can use it
evaluator_llm = llm_factory("google/gemini-2.0-flash-001", provider="openai", client=client)

async def run_eval():
    # 2. Prepare the data from your last run
    # Note: 'contexts' must be a list of strings
    sample = SingleTurnSample(
        user_input="What are the key AI trends in 2026?",
        response="The 2026 landscape focuses on agentic workflows and healthcare AI...",
        retrieved_contexts=[
            "Agentic AI is moving into enterprise workflows in 2026.",
            "Healthcare moves to patient-facing clinical deployment."
        ],
        reference="AI trends for 2026 include agentic systems and healthcare scaling."
    )
    
    dataset = EvaluationDataset(samples=[sample])

    # 3. Run the evaluation
    print("[INFO] Starting Ragas Evaluation...")
    result = evaluate(
        dataset=dataset,
        metrics=[Faithfulness(llm=evaluator_llm), 
                 ResponseRelevancy(llm=evaluator_llm), 
                 ContextPrecision(llm=evaluator_llm)]
    )

    # 4. Show the results
    print("\n==================================================")
    print("RAGAS EVALUATION SCORES")
    print("==================================================")
    print(result)
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_eval())
"""Test LLM models connectivity and response."""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Models to test (tier order)
MODELS_TO_TEST = [
    ("gemini-2.5-flash-lite", "LITE - Simple tasks"),
    ("gemini-2.5-flash", "FAST - Volume tasks"),
    ("gemini-2.5-pro", "PRO - Complex reasoning"),
    # ("gemini-3.1-pro-preview", "PREMIUM - Critical analysis"),  # May not be available
]

TEST_PROMPT = "What is 2+2? Reply with just the number."


async def test_vertex_ai_model(model_name: str, description: str) -> dict:
    """Test a specific model via Vertex AI."""
    import time
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    
    result = {
        "model": model_name,
        "description": description,
        "status": "unknown",
        "response": "",
        "latency_ms": 0,
        "error": None
    }
    
    try:
        start = time.perf_counter()
        
        model = GenerativeModel(model_name)
        config = GenerationConfig(
            temperature=0.0,
            max_output_tokens=100,
        )
        
        # Run sync call in executor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(
                TEST_PROMPT,
                generation_config=config
            )
        )
        
        latency_ms = int((time.perf_counter() - start) * 1000)
        
        result["status"] = "OK"
        result["response"] = response.text.strip() if hasattr(response, "text") else str(response)
        result["latency_ms"] = latency_ms
        
    except Exception as e:
        result["status"] = "FAILED"
        result["error"] = str(e)
    
    return result


async def test_all_models():
    """Test all configured models."""
    import vertexai
    
    project = os.getenv("GCP_PROJECT")
    location = os.getenv("GCP_LOCATION", "us-central1")
    
    if not project:
        print("ERROR: GCP_PROJECT not set in .env")
        sys.exit(1)
    
    print(f"Initializing Vertex AI (project={project}, location={location})")
    vertexai.init(project=project, location=location)
    
    print("\n" + "=" * 60)
    print("LLM MODEL CONNECTIVITY TEST")
    print("=" * 60 + "\n")
    
    results = []
    for model_name, description in MODELS_TO_TEST:
        print(f"Testing {model_name} ({description})...")
        result = await test_vertex_ai_model(model_name, description)
        results.append(result)
        
        if result["status"] == "OK":
            print(f"  ✓ OK - Response: '{result['response']}' ({result['latency_ms']}ms)")
        else:
            print(f"  ✗ FAILED - {result['error']}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    ok_count = sum(1 for r in results if r["status"] == "OK")
    print(f"\nModels tested: {len(results)}")
    print(f"Successful: {ok_count}")
    print(f"Failed: {len(results) - ok_count}")
    
    if ok_count < len(results):
        print("\nFailed models:")
        for r in results:
            if r["status"] != "OK":
                print(f"  - {r['model']}: {r['error']}")
    
    return results


if __name__ == "__main__":
    results = asyncio.run(test_all_models())
    sys.exit(0 if all(r["status"] == "OK" for r in results) else 1)

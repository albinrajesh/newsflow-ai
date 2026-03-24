import httpx
import json
import sys
import time

# Color codes for a prettier terminal
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

def run_test():
    url = "http://localhost:8000/research/stream"
    
    # Payload for the request
    payload = {"query": "What are the latest breakthroughs in Agentic AI and RAG as of 2026?"}
    
    print(f"{CYAN}Connecting to {url}...{RESET}")
    
    try:
        # 120.0s timeout to allow for model inference and rate-limit recovery
        with httpx.stream("POST", url, json=payload, timeout=120.0) as response:
            if response.status_code != 200:
                print(f"Error: Server returned {response.status_code}")
                return

            print(f"{GREEN}Stream Started:{RESET}\n" + "-"*40)
            
            for line in response.iter_lines():
                if not line or not line.startswith("data: "):
                    continue
                
                # Extract the JSON data portion
                data_str = line[6:].strip()
                
                # Handle the completion signal
                if data_str == "[DONE]":
                    print(f"\n" + "-"*40 + f"\n{GREEN}Stream Finished Successfully.{RESET}")
                    break
                
                try:
                    data_json = json.loads(data_str)
                    
                    # 1. Handle Status Updates (Planning, Grading, etc.)
                    if "status" in data_json:
                        # Use Magenta for background processing status
                        print(f"\n{MAGENTA}>> {data_json['status']}{RESET}", flush=True)
                    
                    # 2. Handle Token Content (The actual LLM response)
                    elif "content" in data_json:
                        content = data_json.get("content", "")
                        
                        # Typewriter Effect: 
                        # We print char by char or word by word to make it feel natural.
                        # Setting flush=True ensures it shows up instantly.
                        print(content, end="", flush=True)
                        
                        # Very slight sleep to smooth out the flow (optional)
                        # time.sleep(0.01) 
                        
                    # 3. Handle Errors sent by the server
                    elif "error" in data_json:
                        print(f"\n{YELLOW}[Server Error]:{RESET} {data_json['error']}")

                except json.JSONDecodeError:
                    if data_str:
                        print(f"\n[Raw Info]: {data_str}")

    except httpx.ConnectError:
        print(f"\n{YELLOW}FAILED:{RESET} Could not connect to the server. Is uvicorn running?")
    except httpx.ReadTimeout:
        print(f"\n{YELLOW}TIMEOUT:{RESET} The agent is working hard but the test script timed out.")
    except Exception as e:
        print(f"\n{YELLOW}An unexpected error occurred:{RESET} {e}")

if __name__ == "__main__":
    # Windows ANSI support enablement
    if sys.platform == "win32":
        import os
        os.system('color')
        
    run_test()
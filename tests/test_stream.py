import httpx
import json
import sys

# Color codes for a prettier terminal (optional but helpful)
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def run_test():
    url = "http://localhost:8000/research/stream"
    
    # You can change the query here for different tests
    payload = {"query": "Tell me a short joke about AI."}
    
    print(f"{CYAN}Connecting to {url}...{RESET}")
    
    try:
        # 120.0 timeout to allow for Gemini/Mistral thinking time and rate limits
        with httpx.stream("POST", url, json=payload, timeout=120.0) as response:
            if response.status_code != 200:
                print(f"Error: Server returned {response.status_code}")
                return

            print(f"{GREEN}Stream Started:{RESET}\n" + "-"*30)
            
            for line in response.iter_lines():
                if not line or not line.startswith("data: "):
                    continue
                
                # Extract the data portion of the SSE
                data_str = line[6:].strip()
                
                # Check for the [DONE] signal
                if data_str == "[DONE]":
                    print(f"\n" + "-"*30 + f"\n{GREEN}Stream Finished Successfully.{RESET}")
                    break
                
                try:
                    data_json = json.loads(data_str)
                    
                    # 1. Handle Status Updates (from Planner/Grader etc.)
                    if "status" in data_json:
                        # Print status on a new line to keep it separate from the content
                        print(f"\n{YELLOW}[Status]{RESET} {data_json['status']}", flush=True)
                    
                    # 2. Handle Token Content (from Synthesiser)
                    elif "content" in data_json:
                        content = data_json.get("content", "")
                        print(content, end="", flush=True)
                        
                    # 3. Handle Errors
                    elif "error" in data_json:
                        print(f"\n{YELLOW}[Server Error]:{RESET} {data_json['error']}")

                except json.JSONDecodeError:
                    # In case of raw strings that aren't JSON
                    if data_str:
                        print(f"\n[Raw]: {data_str}", end="", flush=True)

    except httpx.ConnectError:
        print(f"\n{YELLOW}FAILED:{RESET} Could not connect to the server. Is uvicorn running?")
    except httpx.ReadTimeout:
        print(f"\n{YELLOW}TIMEOUT:{RESET} The agent took too long to respond.")
    except Exception as e:
        print(f"\n{YELLOW}An unexpected error occurred:{RESET} {e}")

if __name__ == "__main__":
    # Ensure terminal handles colors correctly on Windows
    if sys.platform == "win32":
        import os
        os.system('color')
        
    run_test()
import os
import time
import requests
from google import genai
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from collections import deque, defaultdict

# --- SETTINGS ---
WINDOW_SIZE = 10        # Seconds to look back
SPIKE_THRESHOLD = 5     # Alert threshold
COOLDOWN_PERIOD = 60    # Min seconds between AI calls
LOG_FILE_PATH = "test.log"

# Secrets (Make sure these are exported in your terminal)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
DISCORD_URL = os.environ.get("DISCORD_WEBHOOK_URL")

client = genai.Client(api_key=GEMINI_KEY)

def send_to_discord(template, explanation, count):
    """Sends a formatted alert to Discord."""
    if not DISCORD_URL:
        return
    data = {
        "embeds": [{
            "title": "AIOps Incident Detected",
            "color": 15548997, # Red
            "fields": [
                {"name": "Log Template", "value": f"`{template}`", "inline": False},
                {"name": "Spike Intensity", "value": f"{count} hits in {WINDOW_SIZE}s", "inline": True},
                {"name": "AI Analysis", "value": explanation[:1024], "inline": False}
            ],
            "footer": {"text": "Gemini Sentinel Analysis"}
        }]
    }
    try:
        requests.post(DISCORD_URL, json=data)
    except Exception as e:
        print(f"Failed to send Discord alert: {e}")

def get_ai_explanation(template, sample_logs):
    """Calls Gemini API for RCA."""
    prompt = f"""
    You are an expert SRE. A log spike was detected.
    Template: {template}
    Recent Examples: {sample_logs}
    
    1. What is the likely root cause?
    2. Suggest 2 immediate steps to fix this.
    Keep it concise.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        # Check for Rate Limit specifically
        if "429" in str(e):
            return "RATE_LIMIT_HIT"
        return f"AI Analysis failed: {e}"

def main():
    config = TemplateMinerConfig()
    template_miner = TemplateMiner(config=config)
    history = defaultdict(lambda: deque())
    last_ai_call_time = 0

    # Ensure file exists
    if not os.path.exists(LOG_FILE_PATH):
        open(LOG_FILE_PATH, 'a').close()

    print(f"--- Monitoring {LOG_FILE_PATH} (Threshold: {SPIKE_THRESHOLD}) ---")
    
    with open(LOG_FILE_PATH, "r") as f:
        f.seek(0, os.SEEK_END)
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            
            result = template_miner.add_log_message(line)
            template_id = result["cluster_id"]
            current_time = time.time()
            
            history[template_id].append(current_time)
            
            # Slide the window
            while history[template_id] and history[template_id][0] < current_time - WINDOW_SIZE:
                history[template_id].popleft()
            
            # Check for Spike
            count = len(history[template_id])
            if count >= SPIKE_THRESHOLD:
                print(f"\n [SPIKE DETECTED] Template #{template_id} appeared {count} times!")
                
                # Check if we are in cooldown
                if (current_time - last_ai_call_time) > COOLDOWN_PERIOD:
                    print(f" Analyzing with AI...")
                    explanation = get_ai_explanation(result['template_mined'], line.strip())

                    if explanation == "RATE_LIMIT_HIT":
                        print(" AI is busy (Rate Limit). Skipping this RCA to avoid spam.")
                    else:
                        print("-" * 30)
                        print(f"AI ROOT CAUSE ANALYSIS:\n{explanation}")
                        print("-" * 30)
                        send_to_discord(result['template_mined'], explanation, count)
                        last_ai_call_time = current_time # Update cooldown
                else:
                    print(f" Spike detected, but AI is on cooldown ({int(COOLDOWN_PERIOD - (current_time - last_ai_call_time))}s remaining).")
                
                history[template_id].clear()

if __name__ == "__main__":
    main()
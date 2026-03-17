import time
import os
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig

def main():
    config = TemplateMinerConfig()
    template_miner = TemplateMiner(config=config)
    
    log_file_path = "/var/log/syslog"
    
    print(f"--- Monitoring {log_file_path} ---")
    
    # Open the file and move to the end so we only see NEW logs
    with open(log_file_path, "r") as f:
        f.seek(0, os.SEEK_END)
        
        try:
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)  # Wait for new logs
                    continue
                
                # Process the real log line
                result = template_miner.add_log_message(line)
                
                # If a new template is found, print it!
                if result["change_type"] != "none":
                    print(f"\n[NEW PATTERN DETECTED]")
                    print(f"Log: {line.strip()}")
                    print(f"Template: {result['template_mined']}")
                    
        except KeyboardInterrupt:
            print("\nStopping monitor...")

if __name__ == "__main__":
    main()
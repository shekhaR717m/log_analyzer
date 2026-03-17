Log Sentinel: Pattern-Based Anomaly Detection

Project Overview
This project provides a real-time monitoring solution for system logs. Traditional log analysis often fails due to the sheer volume of data and the dynamic nature of log messages (such as fluctuating timestamps or unique user IDs). This system addresses that by using the Drain3 mining algorithm to learn log templates on the fly, allowing it to distinguish between normal system noise and genuine operational spikes.

Technical Architecture
The system operates as a streaming pipeline:

Log Ingestion: The script monitors a target file (syslog or a custom test file) using a non-blocking stream.

Template Mining: Raw log lines are processed by a Drain3 engine. This transforms unstructured text like User 104 failed to login into a structured template: User <*> failed to login.

Frequency Analysis: A sliding window algorithm tracks the occurrence rate of each template. If a template appears more than five times within a ten-second window, it is flagged as an anomaly.

Contextual Analysis: Once a spike is detected, the system passes the template and sample logs to the Gemini 2.0 Flash model to generate a technical root cause analysis.

Alerting: Detailed incident reports are pushed to a Discord webhook for immediate visibility.

Implementation Details
The project includes a built-in cooldown mechanism to prevent API exhaustion and alert fatigue. If an incident is active, the system will continue to monitor spikes but will throttle AI calls to once per minute. This ensures that the system remains cost-effective and stable during high-volume log bursts.

Setup Instructions
Prerequisites
Python 3.9 or higher

WSL2 (if running on Windows)

Access to a Google AI Studio API Key

Installation
Clone the repository and install the required dependencies:

Bash
git clone https://github.com/shekhaR717m/log_analyzer.git
cd log_analyzer
pip install -r requirements.txt
Environment Configuration
The system requires two environment variables to be set in your shell:

Bash
export GEMINI_API_KEY='your_api_key_here'
export DISCORD_WEBHOOK_URL='your_webhook_url_here'
Running the System
Start the analyzer:

Bash
python3 app.py
To test the detection logic, you can use the following bash command in a separate terminal to simulate a database connection spike:

Bash
for i in {1..10}; do echo "ERROR: Database connection timeout on port 5432" >> test.log; done
Repository Structure
app.py: Main logic for streaming, parsing, and alerting.

requirements.txt: List of Python dependencies (google-genai, drain3, requests).

test.log: Local file used for simulating log traffic.

How to push this to GitHub now:
Save the file in VS Code.

In your WSL terminal, run:

Bash
git add README.md
git commit -m "docs: rewrite readme for professional tone"
git push origin main
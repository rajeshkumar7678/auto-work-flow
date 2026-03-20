import schedule
import time
import subprocess
import os
import pytz
from datetime import datetime

# Configure US/Eastern Timezone
US_TZ = pytz.timezone("US/Eastern")

def run_agent():
    """
    Trigger the autonomous agent script.
    Using subprocess to ensure it runs in its own environment.
    """
    now_us = datetime.now(US_TZ).strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{now_us} ET] 🚀 Triggering Automated US Upload...")
    
    try:
        # Run autonomous_agent.py
        result = subprocess.run(["python", "autonomous_agent.py"], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️  Warnings/Errors:\n{result.stderr}")
    except Exception as e:
        print(f"❌ Scheduler failed to launch agent: {e}")

def check_and_run():
    """
    Checks if current US/Eastern time matches one of the target hours.
    9 AM, 12 PM, 3 PM, 6 PM, 9 PM ET.
    """
    now_et = datetime.now(US_TZ)
    target_hours = [9, 12, 15, 18, 21]
    
    # We use a simple check loop that maps to the target ET hours
    if now_et.hour in target_hours and now_et.minute == 0:
        run_agent()
        # Sleep for a bit to avoid double trigger in the same minute
        print("Waiting for next slot...")
        time.sleep(61)

print("=" * 40)
print("   📅 US-DOMINANCE Scheduler Active")
print("   Targeting: 09:00, 12:00, 15:00, 18:00, 21:00 US Eastern Time")
print("=" * 40)
print("\nPress Ctrl+C to stop the scheduler.")

# Run once immediately on startup for verification (optional)
# run_agent()

while True:
    check_and_run()
    time.sleep(30) # check every 30 seconds

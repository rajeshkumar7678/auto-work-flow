import sys
import time
import subprocess
import os
import pytz
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Configure US/Eastern Timezone
US_TZ = pytz.timezone("US/Eastern")

# --- Daily Upload Schedule ---
# 5 slots per day. Each slot has a content mode assigned:
#   football  → Uses real-time FIFA/World Cup trends (FootballTrendScout + ContentResearcher)
#   general   → Uses psychology/tech/AI niche trends (original flow)
#
# Slot assignment (US Eastern Time):
#   09:00 ET → football  (Slot 1/5)
#   12:00 ET → football  (Slot 2/5)
#   15:00 ET → football  (Slot 3/5)
#   18:00 ET → general   (Slot 4/5)
#   21:00 ET → general   (Slot 5/5)

UPLOAD_SCHEDULE = {
    9:  "football",
    12: "football",
    15: "football",
    18: "general",
    21: "general",
}

def run_agent(content_mode):
    """
    Trigger the autonomous agent with the specified content mode.
    Injects CONTENT_MODE env variable before launching subprocess.
    Uses sys.executable to ensure the active virtual environment Python is used.
    """
    now_us = datetime.now(US_TZ).strftime('%Y-%m-%d %H:%M:%S')
    mode_label = "⚽ Football" if content_mode == "football" else "💼 General"
    print(f"\n[{now_us} ET] {mode_label} — Triggering Automated Upload...")

    try:
        # Inject the content mode into the subprocess environment
        env = os.environ.copy()
        env["CONTENT_MODE"] = content_mode

        result = subprocess.run(
            [sys.executable, "autonomous_agent.py"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env
        )
        print(result.stdout)
        if result.stderr:
            print(f"⚠️  Warnings/Errors:\n{result.stderr}")
    except Exception as e:
        print(f"❌ Scheduler failed to launch agent: {e}")

def check_and_run():
    """
    Checks if current US/Eastern time matches one of the target hours.
    Automatically selects the correct content mode for that slot.
    """
    now_et = datetime.now(US_TZ)

    if now_et.hour in UPLOAD_SCHEDULE and now_et.minute == 0:
        content_mode = UPLOAD_SCHEDULE[now_et.hour]
        run_agent(content_mode)
        # Sleep 61 seconds to avoid double-triggering within the same minute
        print("Waiting for next slot...")
        time.sleep(61)

print("=" * 50)
print("   📅 US-DOMINANCE Scheduler Active")
print("=" * 50)
print("   Daily Upload Plan (US Eastern Time):")
for hour, mode in UPLOAD_SCHEDULE.items():
    label = "⚽ Football/World Cup" if mode == "football" else "💼 General Niche"
    print(f"   {hour:02d}:00 ET  →  {label}")
print("=" * 50)
print("\nPress Ctrl+C to stop the scheduler.\n")

while True:
    check_and_run()
    time.sleep(30)  # Check every 30 seconds


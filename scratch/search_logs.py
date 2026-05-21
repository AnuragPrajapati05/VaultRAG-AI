import json

log_file = r"C:\Users\anurag_prajapati\.gemini\antigravity\brain\bd38b1cd-73ea-4059-82e6-f58d614ec4d6\.system_generated\logs\overview.txt"

with open(log_file, encoding="utf-8") as f:
    for line_num, line in enumerate(f, 1):
        if "gemini" in line.lower() or "api_key" in line.lower() or "ai_key" in line.lower():
            print(f"Line {line_num} contains keywords.")
            # find first occurrences
            idx = line.lower().find("gemini")
            if idx != -1:
                print("gemini match:", line[max(0, idx-50):min(len(line), idx+100)])
            idx2 = line.lower().find("api_key")
            if idx2 != -1:
                print("api_key match:", line[max(0, idx2-50):min(len(line), idx2+100)])

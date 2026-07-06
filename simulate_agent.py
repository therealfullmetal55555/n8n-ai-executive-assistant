#!/usr/bin/env python3
"""
Interactive CLI simulator for the AI Executive Assistant.
Demonstrates multi-turn tool calling, safety confirmation loops, and window buffer memory offline.
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

class SimulatedAgent:
    def __init__(self):
        self.memory = []
        self.pending_confirmation = None
        self.notion_tasks = []
        self.calendar_events = [
            {"title": "Internal Team Standup", "start": "10:00", "end": "10:30"},
            {"title": "Client Architecture Review", "start": "14:00", "end": "15:00"}
        ]

    def tool_check_calendar_availability(self, date_str: str) -> dict:
        return {
            "date": date_str,
            "busy_events": self.calendar_events,
            "free_slots": ["09:00 - 10:00", "11:00 - 14:00", "15:00 - 18:00"],
            "status": "success"
        }

    def tool_create_calendar_event(self, title: str, time_str: str) -> dict:
        evt = {"title": title, "start": time_str, "status": "confirmed"}
        self.calendar_events.append(evt)
        return evt

    def tool_create_notion_task(self, title: str, priority: str, due_date: str) -> dict:
        task = {"id": f"notion_{len(self.notion_tasks)+1}", "title": title, "priority": priority, "due_date": due_date}
        self.notion_tasks.append(task)
        return task

    def tool_tavily_search(self, query: str) -> dict:
        return {
            "query": query,
            "snippet": f"Summary for '{query}': Multi-turn agent architectures enforce safety by requesting user confirmation before writing changes to external APIs."
        }

    def process_message(self, user_text: str) -> str:
        text_lower = user_text.lower()
        
        # Check if pending confirmation
        if self.pending_confirmation and any(w in text_lower for w in ["yes", "confirm", "book it", "sure", "proceed"]):
            conf = self.pending_confirmation
            self.tool_create_calendar_event(conf["title"], conf["time"])
            self.pending_confirmation = None
            return f"Meeting Confirmed & Booked in Google Calendar:\n• Title: {conf['title']}\n• Schedule: {conf['time']}\n• Status: Synced."

        # Scenario 1: Book calendar event request
        if "book" in text_lower or "schedule" in text_lower:
            time_match = re.search(r'(\d{1,2}:\d{2})', user_text)
            if not time_match:
                return "What specific time would you prefer for the meeting, and how long should it be (e.g. 30 mins)?"
            
            target_time = time_match.group(1)
            avail = self.tool_check_calendar_availability("Tomorrow")
            self.pending_confirmation = {"title": "Meeting with Partner", "time": f"Tomorrow at {target_time}"}
            return (
                f"[Tool Call: check_calendar_availability] -> Slot {target_time} is FREE.\n\n"
                f"Proposed Meeting Details:\n"
                f"• Title: Meeting with Partner\n"
                f"• Time: Tomorrow, {target_time} (30 mins)\n\n"
                f"Confirmation Check: Shall I go ahead and confirm this booking on your Google Calendar?"
            )

        # Scenario 2: Create task
        if "task" in text_lower:
            task_res = self.tool_create_notion_task("Review contract & deliverables", "High", "Friday 5 PM")
            return (
                f"[Tool Call: create_notion_task] -> Payload: {json.dumps(task_res)}\n\n"
                f"Task Logged in Notion:\n"
                f"• Title: {task_res['title']}\n"
                f"• Priority: {task_res['priority']}\n"
                f"• Due Date: {task_res['due_date']}\n"
                f"• Status: To Do"
            )

        # Scenario 3: Web search
        if any(w in text_lower for w in ["search", "research", "what is", "what are", "latest"]):
            search_res = self.tool_tavily_search(user_text)
            return (
                f"[Tool Call: tavily_web_search] -> Query: '{user_text}'\n\n"
                f"Web Search Summary:\n"
                f"{search_res['snippet']}"
            )

        return "I am your AI Executive Assistant. I can check/book calendar slots (with your confirmation), create Notion tasks, or perform web research. How can I assist you?"

def main():
    print("=" * 80)
    print("AI EXECUTIVE ASSISTANT (TOOL-CALLING LOCAL SIMULATOR)")
    print("=" * 80)
    
    agent = SimulatedAgent()
    demo_prompts = [
        "Can you book a 30-min call with Alex tomorrow at 15:00?",
        "Yes, confirm and book it.",
        "Create a high priority task to review the supplier contract by Friday 5 PM.",
        "What are the latest best practices for n8n AI agent safety?"
    ]
    
    for i, prompt in enumerate(demo_prompts, 1):
        print(f"\nUser [Turn {i}]: \"{prompt}\"")
        reply = agent.process_message(prompt)
        print(f"Agent:\n{reply}\n" + "-" * 80)

if __name__ == "__main__":
    main()

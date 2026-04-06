# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

In my initial UML design, I picked four main classes because they match what the app is trying to do: store info about the person, store info about the pet, keep a list of care tasks, and then build a daily plan from those tasks.

- **Owner**: This represents the human using the app. It holds the owner’s basic info plus their available time and preferences, since those things affect what the schedule can realistically fit.
- **Pet**: This represents the pet being cared for. It stores the pet’s details (like species and age) and links back to the owner, because each pet belongs to someone.
- **Task**: This represents individual pet care tasks (like feeding, walking, grooming, meds, etc.). It includes a time, frequency, duration (minutes), a priority number, and a completed flag to track progress.
- **Scheduler**: This is the “planner” part of the system. It collects tasks across pets and generates a daily plan. When the owner has limited time, it chooses higher-priority tasks first and only includes tasks that fit.

**Three core user actions**

1. **Add and track pets**: the owner registers one or more pets (name, species, age) so tasks can be tied to the right animal.
2. **Add and complete care tasks**: the owner records what needs to happen (time, duration, priority, frequency) and marks tasks done; daily/weekly tasks roll forward to the next occurrence.
3. **Generate a daily schedule**: the app builds a plan from all pets’ tasks—optionally fitting available minutes, sorting by time for display, filtering by pet or completion, and warning about same-time conflicts.

**b. Design changes**

Yes — after reviewing `pawpal_system.py`, I made a few changes to make the relationships clearer and to better match the assignment requirements.

- I connected the classes directly: `Owner` keeps a list of `Pet` objects, and each `Pet` keeps a list of `Task` objects.
- I clarified time units by using `available_time_minutes` on `Owner`, so it’s obvious what the scheduler is counting.
- I added `duration_minutes` and `priority` to `Task` so the scheduler can make “what fits” decisions (not just sorting).
- I made recurring behavior explicit: when a daily/weekly task is completed using `Pet.complete_task(...)`, the next occurrence is automatically created.

These changes keep the design simple, but reduce confusion (especially when there are multiple pets/tasks) and make scheduling behavior more consistent.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers:

- **Time available (minutes)**: if the owner sets `available_time_minutes` to a non-zero number, the schedule only includes tasks that fit within that time.
- **Priority**: tasks have a priority number (1 is highest). When time is limited, higher-priority tasks are chosen first.
- **Time of day (HH:MM)**: after tasks are chosen, the schedule is displayed in time order so it reads like a realistic day plan.

I decided these constraints mattered most because they are easy to explain and test, and they match the app goal: help a busy owner fit the most important care tasks into a limited amount of time.

**b. Tradeoffs**

One tradeoff I made is that conflict detection only checks for exact time matches (like two tasks both at "07:30"). It does not try to detect overlaps based on duration ranges. This is reasonable for this project because it still catches the most obvious problem (two things scheduled at the same exact time), but I know it could miss real-life conflicts (like a 20-minute walk at 7:30 and a 10-minute feeding at 7:40). If I improved it later, I’d use `duration_minutes` to check for overlapping time ranges instead of just matching strings.

---

## 3. AI Collaboration

**a. How you used AI**

I used VS Code Copilot kind of like a helper while I was building the scheduler. The most useful thing was the inline suggestions when I was writing small methods or repeating patterns. Copilot Chat also helped when I got stuck, like when I needed to talk through why something wasn’t working or when I wanted to turn my scheduling rules into a basic starting point.

The best prompts were the really specific ones. Like “here’s my task list and available minutes, what’s a simple way to choose what fits?” or “what are a few edge cases I should try?” If I was too vague, the answers got kind of generic.

**b. Judgment and verification**

One time I didn’t take the suggestion was when it wanted me to add extra classes (like a whole `TimeSlot` / `CalendarEvent` thing) to make scheduling more “real.” For this project that felt like overkill, so I kept it simpler with `Scheduler` and `Task` and just made smaller fixes that actually helped.

When I did use AI suggestions, I didn’t just copy/paste them. I checked if they matched my UML and what the assignment actually wants, and then I tried a few quick scenarios to see if it broke anything (like not enough time, different priorities, or two tasks at the same time). If it made the code messier, I changed it or skipped it.

I also used separate chat sessions for different parts of the project (design/UML vs coding vs debugging). That honestly kept me way more organized, because I wasn’t mixing everything together in one long chat and getting lost.

---

## 4. Testing and Verification

**a. What you tested**

I tested the most important scheduling behaviors:

- **Fit-to-time scheduling**: when available minutes are limited, the scheduler only includes tasks that fit.
- **Recurring task creation**: completing a daily/weekly task creates the next occurrence.
- **Conflict detection**: tasks with the exact same `HH:MM` time are reported as conflicts.

These tests matter because they cover the “smart” parts of the app (decision-making and edge cases), not just the UI.

**b. Confidence**

I’m moderately confident because the core behaviors are tested, and I also tried a few manual scenarios in the Streamlit app.

If I had more time, I would test edge cases like invalid time strings (ex: "7:3"), zero/negative durations, ties when two tasks have the same priority, and a more realistic conflict checker that detects overlaps (not just exact matching times).

---

## 5. Reflection

**a. What went well**

I’m most satisfied with the way the UI and backend connect cleanly: I can add pets and tasks in Streamlit, then generate a schedule and immediately see the results. The recurring-task behavior also feels like a real “assistant” feature.

**b. What you would improve**

If I had another iteration, I would improve conflict detection to consider duration overlaps, add a nicer way to edit tasks in the UI (not just add/complete), and use preferences more directly (for example, “morning walk preferred” or “avoid late-night tasks”).

**c. Key takeaway**

The main thing I learned is that even with Copilot, I still have to be the “lead architect.” Copilot can generate a lot of ideas fast, but it doesn’t really know what my project should look like. I had to make the calls on what to keep simple, what to leave out, and how the design stays consistent.

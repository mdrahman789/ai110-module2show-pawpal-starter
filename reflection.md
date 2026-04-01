# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

In my initial UML design, I picked four main classes because they match what the app is trying to do: store info about the person, store info about the pet, keep a list of care tasks, and then build a daily plan from those tasks.

- **Owner**: This represents the human using the app. It holds the owner’s basic info plus their available time and preferences, since those things affect what the schedule can realistically fit.
- **Pet**: This represents the pet being cared for. It stores the pet’s details (like species and age) and links back to the owner, because each pet belongs to someone.
- **Task**: This represents individual pet care tasks (like feeding, walking, grooming, meds, etc.). It includes duration and priority so the scheduler can make decisions, plus notes and a completed flag to track progress.
- **Scheduler**: This is the “planner” part of the system. It connects an owner, a pet, and a list of tasks, and its job is to add/edit tasks and generate a daily plan with a short explanation of why that plan makes sense.

**b. Design changes**

Yes — after reviewing `pawpal_system.py`, I made a few small changes to make the relationships clearer and the classes easier to use.

- I connected the classes more directly: `Owner` now keeps a list of their `Pet` objects, `Pet` can keep a list of its `Task` objects, and each `Task` includes a `pet_id` so it’s clear which pet the task belongs to.
- I clarified time units by renaming `available_time` to `available_minutes`, so it’s obvious what the scheduler is counting.
- I also replaced a few placeholder methods (`pass`) with simple working updates (like updating info/preferences and marking tasks complete), and I changed `Scheduler.edit_task` to update fields on an existing task instead of replacing the whole task object.

These changes keep the design simple, but reduce confusion (especially when there are multiple pets/tasks) and make scheduling behavior more consistent.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

One tradeoff I made is that conflict detection only checks for exact time matches (like two tasks both at "07:30"). It does not try to detect overlaps based on how long a task takes, because my tasks don’t track duration in a reliable way yet and I wanted the logic to stay simple. This is reasonable for this project because it still catches the most obvious problem (two things scheduled at the same exact time), but I know it could miss real-life conflicts (like a 20-minute walk at 7:30 and a 10-minute feeding at 7:40). If I improved it later, I’d add a duration field and then check for overlapping time ranges instead of just matching strings.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

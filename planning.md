# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

This domain covers mostly real student experiences with a little bit of official course description. What makes this information hard to find is that you may need to scroll for several minutes through reviews/forums to find the exact information you want.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Reddit | Discussion about free time as a CS student | https://www.reddit.com/r/csMajors/comments/tyd551/as_a_cs_undergraduate_how_much_free_time_do_you/ |
| 2 | Reddit | Discussion about time spent studying CS | https://www.reddit.com/r/berkeley/comments/19as3vo/choosing_between_cs_courses_workload_and_advice/ |
| 3 | Reddit | Discussion about time spent on CS classes | https://www.reddit.com/r/BrownU/comments/mwzx77/how_is_the_workload_for_intro_cs_classes_how_many/ |
| 4 | Reddit | Discussion about time spent studying CS | https://www.reddit.com/r/csMajors/comments/9q87g2/cs_majors_how_many_hours_per_week_do_you/ |
| 5 | Sac State | Course Catalog with class descriptions | https://catalog.csus.edu/courses-a-z/csc/ |
| 6 | OMS Central | ML class student reviews | https://www.omscentral.com/courses/machine-learning/reviews |
| 7 | OMS Central | Computer Networks class student reviews | https://www.omscentral.com/courses/computer-networks/reviews |
| 8 | OMS Central | Software Dev Process class reviews | https://www.omscentral.com/courses/software-development-process/reviews |
| 9 | OMS Central | AI class reviews | http://omscentral.com/courses/artificial-intelligence/reviews |
| 10 | Reddit | Time Management advice with CS workload | https://www.reddit.com/r/csMajors/comments/13ie714/how_to_manage_time_with_heavy_workload_classes/ |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**

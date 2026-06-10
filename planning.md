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
250 - 350 tokens

**Overlap:**
25 tokens

**Reasoning:**
These documents are already small semantic units, so the chunk size should align to fit a single review boundaries rather than a fixed count. For longer reddit comments, we can split at each paragraph. Therefore, a chunk sizes between 250 and 350 would work well with a small overlap of 25 in case certain longer reviews exceed the limit. Fixed size chunking is better for optimized long documents, not small reviews.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
all-MiniLM-L6-v2 via sentence transformers

**Top-k:**
Top 4 chunks

**Production tradeoff reflection:**
If I were deploying this for real users, and cost wasn't a constraint, I would consider upgrading to something more fine tuned for educational and forum content/ This would provide better ranking when a user asks a question and the reviews yse indirect language as an answer.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | How many hours per week do CS students typically spend on coursework outside of class? | Students on r/csMajors report spending roughly 20–40 hours per week on coursework, with the range depending on course load and difficulty |
| 2 | How many hours per week do students say the OMS Central Machine Learning course requires? | OMS Central reviewers report the ML course requires approximately 10–20 hours per week |
| 3 | What do students say about free time when taking multiple CS classes simultaneously? | Students report having limited free time (under 10 hours/week) when taking 3+ CS courses at once |
| 4 | What do OMS Central reviewers say about the difficulty of the Software Development Process course? | Reviewers describe it as one of the lighter OMSCS courses, often citing it as manageable alongside other courses |
| 5 | What strategies do CS students on Reddit recommend for managing a heavy course workload? | Students recommend starting assignments early and attending office hours as the most commonly cited strategies |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. My documents may become noisy because reddit comments can be people saying simple things like "I agree".

2. Chunks may split key information accross boundaries due to the lack of labeling. Reviews may not have enough specificity to what they are referring to.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RAG PIPELINE — UNOFFICIAL GUIDE                     │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────┐
  │  1. DOCUMENT         │   Sources: Reddit threads, OMS Central reviews,
  │     INGESTION        │            Sac State course catalog
  │                      │   Tools:   requests + BeautifulSoup (web scraping)
  └──────────┬───────────┘            PRAW (Reddit API)
             │  raw text per source
             ▼
  ┌──────────────────────┐
  │  2. CHUNKING         │   Strategy: split at review/comment boundaries
  │                      │   Chunk size: 200–350 tokens
  │                      │   Overlap:    20–30 tokens (only when split needed)
  └──────────┬───────────┘   Tools:     LangChain RecursiveCharacterTextSplitter
             │  list of text chunks
             ▼
  ┌──────────────────────┐
  │  3. EMBEDDING +      │   Model:  all-MiniLM-L6-v2 (sentence-transformers)
  │     VECTOR STORE     │   Dims:   384
  │                      │   Store:  ChromaDB (local persistent collection)
  └──────────┬───────────┘
             │  vector index on disk
             ▼
  ┌──────────────────────┐
  │  4. RETRIEVAL        │   Method: cosine similarity search
  │                      │   Top-k:  4 chunks per query
  │                      │   Tools:  ChromaDB .query()
  └──────────┬───────────┘
             │  top-4 relevant chunks + metadata
             ▼
  ┌──────────────────────┐
  │  5. GENERATION       │   Model:  Groq API (llama-3.3-70b-versatile)
  │                      │   Input:  user query + retrieved chunks as context
  │                      │   Output: grounded answer citing student experiences
  └──────────────────────┘
```

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
I will use Groq to give it the user query, top k chunks, and I expect it to produce a grounded response based on the documentation provided. I will verify that the outputs match my spec by verifying if the output is in one of the documents word for word.

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**

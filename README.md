# The Unofficial Guide — Project 1

[Demo Video](https://www.loom.com/share/6df740ec6aea461eb83eeb4ae5e9079c)

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This system covers real CS student experiences: how many hours coursework actually takes, what specific courses feel like from the inside, how students manage heavy workloads, and how much free time remains. This knowledge is valuable because official course descriptions say nothing about workload, stress, or pacing — they list topics and credit hours, not what it costs a student per week. Finding it through unofficial channels requires scrolling through long Reddit threads and hundreds of course reviews to find the handful of comments that answer your specific question. This system retrieves that information directly.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Reddit r/csMajors | Reddit thread (manual .txt) | https://www.reddit.com/r/csMajors/comments/tyd551/as_a_cs_undergraduate_how_much_free_time_do_you/ |
| 2 | Reddit r/berkeley | Reddit thread (manual .txt) | https://www.reddit.com/r/berkeley/comments/19as3vo/choosing_between_cs_courses_workload_and_advice/ |
| 3 | Reddit r/BrownU | Reddit thread (manual .txt) | https://www.reddit.com/r/BrownU/comments/mwzx77/how_is_the_workload_for_intro_cs_classes_how_many/ |
| 4 | Reddit r/csMajors | Reddit thread (manual .txt) | https://www.reddit.com/r/csMajors/comments/9q87g2/cs_majors_how_many_hours_per_week_do_you/ |
| 5 | Sac State CSC Catalog | Course catalog (scraped) | https://catalog.csus.edu/courses-a-z/csc/ |
| 6 | OMS Central | ML course reviews (scraped) | https://www.omscentral.com/courses/machine-learning/reviews |
| 7 | OMS Central | Computer Networks reviews (scraped) | https://www.omscentral.com/courses/computer-networks/reviews |
| 8 | OMS Central | Software Dev Process reviews (scraped) | https://www.omscentral.com/courses/software-development-process/reviews |
| 9 | OMS Central | AI course reviews (scraped) | http://omscentral.com/courses/artificial-intelligence/reviews |
| 10 | Reddit r/csMajors | Reddit thread (manual .txt) | https://www.reddit.com/r/csMajors/comments/13ie714/how_to_manage_time_with_heavy_workload_classes/ |

---

## Chunking Strategy

**Chunk size:** 200–350 tokens (~800–1400 characters); hard cap at 300 tokens / 1200 characters enforced by the splitter.

**Overlap:** 25 tokens (~100 characters).

**Why these choices fit your documents:**
The sources are already small semantic units — individual Reddit comments and course reviews — rather than long documents like textbooks or FAQs. Fixed-size chunking optimized for long documents would split reviews mid-thought. Instead, chunks are aligned to review and comment boundaries using `RecursiveCharacterTextSplitter` with paragraph (`\n\n`) and sentence (`. `) separators, so the splitter only cuts mid-paragraph when a review genuinely exceeds the cap.

The original target of 250–350 tokens assumed longer reviews. In practice, OMS Central reviews average ~200 tokens and Sac State course descriptions average ~130 tokens — both below 250 tokens when complete. Forcing them to hit an arbitrary minimum would require merging unrelated documents. The floor was lowered to 200 tokens to match actual document structure.

Because many reviews are still shorter than 200 tokens individually, a merge step runs before splitting: consecutive documents from the same source are concatenated (separated by a blank line) until the combined block approaches 3× the chunk size cap. The paragraph separator is preserved so the splitter can still break at natural boundaries if a merged block exceeds the maximum.

Preprocessing before chunking removed HTML entities, bare URLs, markdown formatting (bold, italic, inline code, blockquote markers), and UI boilerplate lines (share, reply, report, save, load more, posted by, etc.). Section-header artifacts shorter than 40 characters were dropped after splitting.

**Final chunk count:** 2,783 chunks across all 10 sources.

**Sample chunks:**

> **Chunk 1** — Source: `reddit_comment` | r/csMajors (free time thread)
> `https://www.reddit.com/r/csMajors/comments/tyd551/`
>
> *"I'm a senior high school student getting ready for college... It's kinda weird. I know people with great time management skills who have ridiculous amounts of free time as a CS major, and I know people who are always stressed out and have no free time at all. It really depends on how you approach the major and what you want to get out of it."*

> **Chunk 2** — Source: `reddit_comment` | r/csMajors (hours per week thread)
> `https://www.reddit.com/r/csMajors/comments/9q87g2/`
>
> *"Taking 15 hours of classes, I average 25-30 hours/week for studies. A professor told me for every hour spent in class you'll have to spend roughly two hours studying to maintain a 4.0. I can absolutely attest to that. I was studying 55-60 hours a week last year taking 17 credits. Got a 4.0 but it is definitely a lot of work."*

> **Chunk 3** — Source: `reddit_comment` | r/csMajors (time management thread)
> `https://www.reddit.com/r/csMajors/comments/13ie714/`
>
> *"Do a high level plan for the rest of your degree (meaning, decide what classes you will take in each semester). Try to evenly spread out CS major classes with general electives (one strategy that worked for me was 2 CS classes + 1 hard GE + 2 easy GEs). Go through all course syllabi at the beginning of the semester and put all deadlines and exam/quiz dates on a calendar."*

> **Chunk 4** — Source: `course_catalog` | Sac State CSC Catalog
> `https://catalog.csus.edu/courses-a-z/csc/`
>
> *"CSC 1. Introduction to Computer Science. 3 Units. Prerequisite(s): Intermediate algebra. Fundamental concepts of computers, computation and programming; history and principles of computing; problem solving; input, output; data representation, storage, and file organization; computer hardware, networking and data communication; social, economic and ethical implications; computer security and privacy."*

> **Chunk 5** — Source: `omscentral_review` | Software Development Process reviews
> `https://www.omscentral.com/courses/software-development-process/reviews`
>
> *"I've been a developer/coder for 18yrs; so the concepts that this course taught were nothing new to me. I didn't learn anything new; however I would recommend this course as someone's first OMSCS course. The projects in the course were fairly easy and didn't take much time. I would rate the difficulty of this course as perhaps the easiest one in the OMSCS program."*

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`. This model runs locally (no API call), produces 384-dimensional embeddings, and is fast enough to embed 2,783 chunks in under a minute on a laptop CPU. It performs well on short, informal English text like forum posts and reviews, which matches the corpus.

**Production tradeoff reflection:**
If deploying for real users without cost constraints, I would consider a model fine-tuned on educational or forum content, or a larger model like `text-embedding-3-large` (OpenAI) or `e5-large-v2`. The main limitation of `all-MiniLM-L6-v2` is that it cannot sharply distinguish between different OMSCS course reviews because they all share workload vocabulary ("hours per week", "difficult", "manageable"). A domain-adapted model would encode course-specific context more distinctly. The tradeoff is latency and cost: larger models are slower and API-hosted models add per-query cost and a network dependency. For a local prototype serving CS students, the MiniLM tradeoff is acceptable.

---

## Retrieval Test Results

**Query 1:** "How many hours per week do CS students typically spend on coursework outside of class?"

| Rank | Distance | Source type | Source |
|------|----------|-------------|--------|
| 1 | 0.26 | reddit_comment | r/berkeley — "you normally go from the time you wake up until you go to bed 7 times a week" |
| 2 | 0.32 | reddit_comment | r/csMajors — "30 min–1 hour for theory courses; 10–20 hours for programming-heavy courses per assignment" |
| 3 | 0.33 | reddit_comment | r/csMajors — "I try to shoot for 5 hours every day; 15–20 hours outside of classes as a Senior" |
| 4 | 0.38 | reddit_comment | r/csMajors — "For discrete math I put in 10 hrs; for CS I put in 10 hrs; for government I put in 0" |

*Why these chunks are relevant:* All four are Reddit comments directly answering how many hours CS students study per week. The distances (0.26–0.38) are the tightest of any query, which makes sense — the query language ("hours per week", "coursework outside of class") closely matches the vocabulary students actually use in these threads.

---

**Query 2:** "What do OMS Central reviewers say about the difficulty of the Software Development Process course?"

| Rank | Distance | Source type | Source |
|------|----------|-------------|--------|
| 1 | 0.35 | omscentral_review | SDP — "seasoned software engineer… approached it to gain an academic perspective" (rating 2.1/5 difficulty) |
| 2 | 0.37 | omscentral_review | SDP — "a lot of software programming background but very little Java; one project was particularly challenging" |
| 3 | 0.37 | omscentral_review | SDP — "18 years as a developer; concepts were nothing new; easiest in OMSCS program" |
| 4 | 0.39 | omscentral_review | SDP — "if you're unfamiliar with Git, testing, Java, or OOP you might struggle; if you're a professional developer it'll be too easy" |

*Why these chunks are relevant:* All four chunks come exclusively from the SDP reviews page (source_id=8). The query names both the source (OMS Central) and the course (Software Development Process), giving the embedding model enough signal to retrieve only SDP content with no cross-course contamination.

---

**Query 3:** "What strategies do CS students on Reddit recommend for managing a heavy course workload?"

| Rank | Distance | Source type | Source |
|------|----------|-------------|--------|
| 1 | 0.39 | reddit_comment | r/csMajors hours thread — student breakdown of hours per course per week |
| 2 | 0.39 | reddit_comment | r/csMajors time management thread — degree planning, spreading CS/GE mix, deadline calendar |
| 3 | 0.39 | omscentral_review | SDP — "if you have previous education in CS this is a very easy course… workload is a little on the heavy side but not complicated" |
| 4 | 0.39 | omscentral_review | SDP — "this is my 7th course… by far my least favorite… if you already have a job in software development, this is not a useful class" |

*Note:* Results 3 and 4 are OMS Central SDP reviews, not Reddit strategy advice. This is a known retrieval limitation: all four results have nearly identical distances (0.389–0.392), meaning the embedding model treats "heavy workload" vocabulary in SDP reviews as equivalent to workload management advice on Reddit. See Failure Case Analysis for detail.

---

## Grounded Generation

**System prompt grounding instruction:**
The system prompt explicitly forbids answering outside the provided documents:

> "You are a helpful assistant for CS students. You answer questions ONLY using the documents provided to you in the user message. You must NOT draw on any outside knowledge, general facts about CS programs, or information from your training data. If the provided documents do not contain enough information to answer the question, respond with exactly: 'I don't have enough information on that.' Never fabricate statistics, quotes, or claims that are not explicitly present in the documents."

The instruction uses "ONLY" and "must NOT" rather than softer phrasing like "try to use" or "prefer" — this enforces grounding rather than suggesting it. The model temperature is set to 0.2 to keep responses close to the retrieved text and reduce paraphrasing drift.

**How source attribution is surfaced in the response:**
Source URLs are extracted programmatically from retrieval metadata (`hit["source_url"]`) in Python and appended after generation — the LLM never generates them. This guarantees attribution cannot be hallucinated: if a source URL appears in the output, it is because a real chunk from that URL was in the top-k results, not because the model invented it.

---

## Example Responses

**Response 1** — Grounded answer with source attribution

> **Query:** What do OMS Central reviewers say about the difficulty of the Software Development Process course?
>
> **Answer:** According to the reviewers, the difficulty of the Software Development Process course varies depending on the individual's background. Reviewers with significant software development experience, such as 18 years or many years, found the course to be "relatively easy" (Document 1, rating 2.1/5 in difficulty), "fairly easy" (Document 2), and "the easiest one in the OMSCS program" (Document 4). However, reviewers suggest that students with limited software engineering background, or those new to Java, may find the course more challenging (Documents 1, 2, and 4). One reviewer mentions that the course is "ideal for someone who knows just Java and OOP but has no experience with version control, testing, or working in a team."
>
> **Retrieved from:**
> • https://www.omscentral.com/courses/software-development-process/reviews

Source attribution is programmatically appended from retrieval metadata — not generated by the LLM.

---

**Response 2** — Grounded answer with multiple sources

> **Query:** How many hours per week do CS students typically spend on coursework outside of class?
>
> **Answer:** According to the documents, CS students spend widely varying hours on coursework outside of class. One student spends 30 min–1 hour per week for a theory-based CS course, and 3–4 hours on homework weeks, with 10–20 hours per assignment for a programming-heavy course. Another student tries to spend 5 hours every day, totaling around 35 hours per week, and mentions spending 15–20 hours per week outside of classes as a Senior. A third student studies about 20 hours a week to maintain mostly As. Overall, the documents suggest a range of roughly 15–50+ hours per week depending on course load and individual habits.
>
> **Retrieved from:**
> • https://www.reddit.com/r/berkeley/comments/19as3vo/choosing_between_cs_courses_workload_and_advice/
> • https://www.reddit.com/r/csMajors/comments/9q87g2/cs_majors_how_many_hours_per_week_do_you/

---

**Response 3** — Out-of-scope query showing refusal

> **Query:** What is the GPA requirement to join the CS honors program at Sac State?
>
> **Answer:** I don't have enough information on that.
>
> **Retrieved from:**
> • https://catalog.csus.edu/courses-a-z/csc/

The system correctly refused to answer rather than generating a plausible GPA figure from general training knowledge. The Sac State catalog was retrieved but it only contains course descriptions, not honors program eligibility requirements.

---

## Query Interface

The interface is a Gradio web app (`app.py`) accessible at `http://localhost:7860` after running `python3 app.py`.

**Input fields:**
- **Your question** — A multi-line text box where the user types a free-form question about CS student experiences, course workloads, or course reviews. Submitting with Enter or clicking the Ask button triggers retrieval and generation.

**Output fields:**
- **Answer** — An 8-line read-only text box showing the LLM's grounded response, which cites document numbers inline (e.g., "according to Document 2…").
- **Retrieved from** — A 4-line read-only text box listing the source URLs of the top-k retrieved chunks, one per line with a bullet prefix. These are extracted programmatically from metadata, not generated by the model.

**Sample interaction transcript:**

```
User input:
  What do students say about free time when taking multiple CS classes?

Answer:
  According to Document 1, a student mentions that they "normally took at least
  Friday night off" to relax, implying limited free time during the week. They
  also note studying "from the time you wake up until you go to bed 7 times a
  week" with minor distractions, suggesting a heavy workload with minimal free
  time. In Document 2, a student shares a packed schedule of ~40 hours per week
  on campus with additional time for internship and self-study, leaving little
  room for unstructured free time.

Retrieved from:
  • https://www.reddit.com/r/berkeley/comments/19as3vo/...
  • https://www.reddit.com/r/csMajors/comments/9q87g2/...
  • https://www.omscentral.com/courses/computer-networks/reviews
  • https://www.omscentral.com/courses/software-development-process/reviews
```

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | How many hours per week do CS students typically spend on coursework outside of class? | Students on r/csMajors report spending roughly 20–40 hours per week, depending on course load | Cited specific student examples: 3–4 hrs/week for one course, 15–20 hrs/week as a senior, 20 hrs/week to maintain mostly As. Gave a range of "a few hours to over 50 hours" | Relevant — retrieved Reddit sources 2 and 4 | Partially accurate — range is wider than expected but all figures are grounded in real quotes |
| 2 | How many hours per week do students say the OMS Central Machine Learning course requires? | OMS Central reviewers report the ML course requires approximately 10–20 hours per week | "I don't have enough information on that." — even though ML reviews were in the retrieved sources | Partially relevant — ML reviews retrieved but chunks didn't contain explicit hour estimates | Inaccurate — the answer exists in the corpus but the top-4 chunks missed the hour-specific content |
| 3 | What do students say about free time when taking multiple CS classes simultaneously? | Students report having limited free time (under 10 hours/week) when taking 3+ CS courses | Cited "studying from wake to bed" and packed 40-hr/week schedules; noted limited explicit free time data | Partially relevant — Reddit sources retrieved but also OMS Central chunks on workload vocabulary overlap | Partially accurate — captures the heavy schedule theme but misses the "multiple classes simultaneously" angle directly |
| 4 | What do OMS Central reviewers say about the difficulty of the Software Development Process course? | Reviewers describe it as one of the lighter OMSCS courses, manageable alongside other courses | "Relatively easy", "fairly easy", "easiest in OMSCS" for experienced developers; harder for those new to Java/OOP/Git | Relevant — retrieved only SDP reviews | Accurate — matches expected answer and adds useful nuance about experience level |
| 5 | What strategies do CS students on Reddit recommend for managing a heavy course workload? | Students recommend starting assignments early and attending office hours | Recommended degree-level planning, spreading CS courses across semesters, and putting all deadlines on a calendar at the start of the semester | Partially relevant — retrieved time management thread but also SDP reviews | Partially accurate — strategies are real and grounded but different from the expected ones; no mention of office hours |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "How many hours per week do students say the OMS Central Machine Learning course requires?"

**What the system returned:** "I don't have enough information on that." — The retrieved sources included the ML reviews page, but the model correctly reported that the specific chunks it received did not contain explicit hour estimates.

**Root cause (tied to a specific pipeline stage):** This is a retrieval precision failure at the **embedding + retrieval stage**. The ML reviews corpus (source 6) contains hundreds of reviews, and some of them do mention hours-per-week estimates. However, with `top_k=4`, the retrieval only surfaces 4 chunks. The `all-MiniLM-L6-v2` model encodes all OMSCS course reviews with similar vectors because they share workload vocabulary ("challenging", "manageable", "hours per week", "assignments"). As a result, the top-4 slots are competed for by AI, ML, Computer Networks, and SDP reviews simultaneously. The chunks that happened to rank highest were general ML and AI reviews that discussed difficulty without naming specific hour counts. The hour-specific ML chunks existed in the index but ranked below the top-4 cutoff.

**What you would change to fix it:** Increase `top_k` from 4 to 8–10 for queries that target a specific course, giving more of that course's reviews a chance to appear. Alternatively, add a metadata pre-filter in ChromaDB (`where={"source_id": "6"}`) when the query mentions a specific course name, so retrieval only searches that course's chunks instead of competing across all sources.

---

## Spec Reflection

**One way the spec helped you during implementation:**
The architecture diagram in `planning.md` — labeling each stage with the specific tool (RecursiveCharacterTextSplitter, sentence-transformers, ChromaDB, Groq) — made it possible to implement each milestone independently without re-deciding the stack each time. When writing `embed.py`, the diagram confirmed that cosine similarity was the intended distance metric and `all-MiniLM-L6-v2` was the chosen model, so there was no ambiguity about which ChromaDB collection settings to use or which embedding library to import.

**One way your implementation diverged from the spec, and why:**
The spec set a chunk size floor of 250 tokens. During implementation, measuring actual document lengths revealed that OMS Central reviews average ~200 tokens and Sac State course descriptions average ~130 tokens — both below the floor even when complete. Enforcing 250 tokens as a minimum would have required merging unrelated reviews into the same chunk, which would contaminate retrieval (a chunk containing two different students' opinions about two different courses would match queries it shouldn't). The floor was lowered to 200 tokens and a merge step was added that only combines consecutive documents from the same source, preserving semantic coherence. The planning.md was updated to reflect this change.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The full Chunking Strategy and Document Sources sections from `planning.md`, plus a description of the document structure (Reddit .txt files, OMS Central scraped HTML, Sac State catalog). Asked Claude to generate the ingestion and chunking code matching the spec.
- *What it produced:* A complete `ingest.py` with `load_local_file()`, `fetch_omscentral_reviews()`, `fetch_sacstate_catalog()`, `clean_text()`, and `chunk_documents()` functions using `RecursiveCharacterTextSplitter` with the specified chunk size and overlap.
- *What I changed or overrode:* The initial scraper used `<p>` tags for OMS Central reviews, which split multi-paragraph reviews into fragments (116 out of 1708 chunks ended mid-sentence). I directed Claude to switch to `div.wrap-break-word` selectors after discovering that each full review was contained in one div, not split across paragraphs. I also added the `merge_short_docs()` step after measuring that most chunks were below the 250-token floor. Claude generated this function after I explained the problem and the constraint that only same-source documents should be merged.

**Instance 2**

- *What I gave the AI:* The Retrieval Approach section from `planning.md` (embedding model, top-k, ChromaDB with cosine similarity) and the Evaluation Plan (3 test queries). Asked Claude to generate `embed.py` with a `build_index()` function and a `retrieve()` function.
- *What it produced:* A complete `embed.py` with batched ChromaDB ingestion (batches of 500 to stay under ChromaDB's per-call limit), cosine similarity collection settings, and a CLI with `--build`, `--eval`, and `--query` flags.
- *What I changed or overrode:* After running `--eval`, Query 2 (OMS ML hours) and Query 3 (time management) returned OMS Central review chunks for queries that were intended to target Reddit sources. I analyzed the retrieval distances and noted this as a known limitation — `all-MiniLM-L6-v2` encodes all workload-related content similarly regardless of source type. Rather than changing the retrieval logic, I documented this as a failure case in the evaluation report since it reflects a real constraint of the chosen embedding model.x

---
name: seo-content-briefing
description: Builds search-intent briefs with entities, outlines, internal links, and quality checks. Use for editorial planning and content refreshes.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: creative-content
---

# SEO Content Briefing

## Overview

A content brief that leads with word count and keyword density produces pages that match a query string but not the reason someone typed it. Search intent, the current results page, and the entities a complete answer must cover decide whether a page is useful. Volume and difficulty only decide whether it is worth building.

This skill turns a target query into an executable brief: intent classification, a dated SERP review, an entity map with coverage priorities, an outline with budgets, internal link slots, evidence requirements, and acceptance gates that block thin or cannibalizing pages.

## When to use

- Commissioning a new article, landing page, or comparison page for organic search.
- Refreshing a page that lost rankings, traffic, or conversion.
- Reviewing a draft against search intent before publication.
- Building an editorial calendar with defensible priorities.
- Auditing internal links and topical coverage for a cluster.
- Do not use for paid search copy, pure social discovery, or app store optimization; those have different ranking systems.

## Workflow

### 1. Fix the target query, locale, and device

Record the exact query, market, language, and device. A brief for "project management software" in the US on desktop is not the same as "project management app" in the UK on mobile.

Classify intent:

| Intent | Evidence in the SERP | Page type that satisfies it |
| --- | --- | --- |
| Informational | Guides, definitions, videos, People Also Ask | Article, tutorial, explainer |
| Commercial investigation | Comparisons, reviews, "best of" lists | Comparison, alternatives, buying guide |
| Transactional | Product pages, pricing, free trials | Landing or pricing page |
| Navigational | Brand or product name dominates | Homepage, docs, login help |

If the top 10 results disagree on intent, the query is ambiguous. Pick the dominant intent and note the secondary one; do not try to satisfy both on one URL.

### 2. Review the results page and record the date

Capture for each of the top 10 organic results: URL, page type, title, H2 structure, approximate word count, publish and update dates, and the entities it covers. Note features that change the click path: AI overview, featured snippet, video pack, shopping units, local pack.

Rules:

- Review logged out, in the target locale, on the target device class.
- Record the date and search engine. SERPs shift weekly; an undated review is folklore.
- Respect terms of service and robots directives; use the search UI and manual notes, not unauthorized scraping.
- Separate ranking pages from ranking domains. A forum thread ranking first signals that first-hand experience beats polish.

### 3. Build the entity and subtopic map

An entity is a thing or concept the answer must address: a product, standard, metric, person, or method. Extract candidates from titles, H2s, People Also Ask, related searches, autocomplete, and your own search query reports.

| Entity | Source | Coverage in top 10 | Priority | Notes |
| --- | --- | --- | --- | --- |
| SOC 2 Type II | 8 of 10 | Common | Must cover | Define and distinguish from Type I |
| Observation window | 4 of 10 | Partial | Differentiator | Explain length and evidence |
| Pen test | 6 of 10 | Common | Must cover | Clarify annual cadence |

Priority rules: must cover (appears in 6 or more of 10, or is required for correctness), differentiator (3 to 5 of 10 and relevant to your audience), optional (1 to 2, or off-intent). A brief with 40 must-cover entities is a textbook, not a page. Cap must-cover at 8 to 12.

### 4. Write the outline with answer-first structure

```text
H1: <primary intent in plain language>
Answer block: 40-60 words that resolve the query without a click.
H2: <subtopic 1>       target 180-260 words
H2: <subtopic 2>       target 220-300 words
  H3: <specific question>
H2: <comparison table>
H2: <how to choose>    include decision criteria
H2: <FAQ>              3-5 real questions, answers 40-60 words
```

Rules:

- Put the direct answer in the first 60 words, then expand. Snippet and AI overview extraction favor this shape.
- Use one H1 and a logical H2/H3 tree; no heading exists only to hold a keyword.
- Set word targets from the job of the section, not a competitor average. Typical informational pages land between 1,200 and 2,000 words; comparison pages between 1,800 and 2,800. These are planning ranges, not ranking factors.
- Place a table or diagram where it removes 150 or more words of prose.
- Leave placeholders for original evidence: test results, screenshots, quotes, or datasets.

### 5. Plan internal links and citations

| Link type | Rule | Example |
| --- | --- | --- |
| Parent to child | Link from the pillar to this page with descriptive anchor | "SOC 2 readiness checklist" |
| Child to parent | One contextual link back to the cluster hub | "guide to compliance audits" |
| Sibling | 1 to 3 links to genuinely related pages | "ISO 27001 control mapping" |
| Conversion | Link to the product or demo where intent supports it | "see evidence collection" |

Anchor text must describe the destination. "Click here" and exact-match repetition both waste the link. Check that each target URL returns 200 and is indexable before adding it.

For external citations, prefer primary sources: standards bodies, vendor documentation, peer-reviewed papers, government data. Every statistic needs a source, a date, and a scope. If a number cannot be traced, cut it.

### 6. Set the experience, expertise, and trust requirements

E-E-A-T is not a score you add at the end; it is evidence you plan for.

- First-hand experience: name the test, sample, or deployment the author draws on.
- Author: real name, relevant role, bio, and a page that links to their other work.
- Review: a named technical reviewer for regulated or high-stakes topics.
- Dates: publish date and a meaningful "last updated" date tied to a content change.
- Transparency: methodology, limitations, conflicts, and who funded the work.
- Contact and policy pages reachable from the page.

For health, finance, and legal topics, assume a higher bar and require a qualified reviewer before publishing.

### 7. Check cannibalization, then run the acceptance gate

Search the site and Search Console for the target query and close variants. If an existing page already targets the same intent, refresh it instead of publishing a new URL.

Refresh checklist:

- Re-check the SERP and update the date.
- Add missing must-cover entities.
- Replace decayed statistics and dead links.
- Improve the answer block and title.
- Merge thin sibling pages and redirect.
- Update internal links to the surviving URL.

Gate the brief before a writer starts. Reject if intent is ambiguous, must-cover coverage is incomplete, no original evidence is planned, or another URL owns the query.

## Validation

| Gate | Check | Pass criterion | Fail action |
| --- | --- | --- | --- |
| Intent | Dominant SERP type identified | 7 of top 10 share one page type, or documented split | Rescope or split the brief |
| SERP review | Date, locale, device recorded | All three present | Re-run the review |
| Entity coverage | Must-cover entities in outline | 100 percent mapped to a heading | Add sections or demote entity |
| Answer block | First 60 words resolve the query | Yes, without requiring a click | Rewrite the opening |
| Cannibalization | Site search and Search Console check | Zero existing URL owns the intent | Refresh instead |
| Links | Every internal target resolves | 200 and indexable | Fix or remove |
| Claims | Every statistic has a source and date | 100 percent | Cut or source |
| Originality | At least one planned first-hand asset | Test, dataset, screenshot, or quote | Add or reframe as secondary |
| Title and meta | Length and intent match | Title 50-60 chars, meta 140-160 chars | Rewrite |

```bash
# Illustrative link check for the URLs named in the brief.
while read -r url; do
  code=$(curl -s -o /dev/null -w '%{http_code}' -L "$url")
  echo "$code $url"
done < internal_links.txt
```

## Gotchas

- Word count becomes the goal. A 3,000 word page that misses the intent loses to a 900 word page that answers it.
- SERP reviews are undated. Record the date, locale, and device or the brief cannot be defended later.
- One query gets two pages, and both underperform. Check cannibalization before assigning a new URL.
- Entities are stuffed into headings without explanation. Cover the concept, not the string.
- AI overviews and featured snippets absorb the click. Plan for zero-click visibility and a clear next step.
- Competitor pages are copied structurally, including their gaps. Use them as a floor, then add original evidence.
- Statistics are cited to other blog posts. Follow the chain to the primary source or drop the claim.
- Internal links point to redirects or noindex pages. Verify status and indexability at brief time.
- Briefs dictate sentences instead of requirements. Give the writer the goal and evidence, not a transcription.
- Local intent is ignored. "Near me" and city queries need local proof, hours, and service area.
- Refresh dates are bumped without changes. Update only when the content materially changes.
- Search Console data is treated as complete. It underreports long-tail queries and anonymizes rare terms.

## Output contract

```yaml
brief:
  target_query: "soc 2 readiness checklist"
  locale: "en-US"
  device: "desktop"
  intent: informational
  secondary_intent: commercial
  serp_review_date: "2026-11-24"
  serp_notes: "8 of 10 results are guides; 2 vendor checklists rank"
  cannibalization_check:
    existing_url: null
    action: create
  audience: "SaaS security leads preparing for their first audit"
  answer_block: "40-60 word direct answer draft"
  entities:
    - name: "SOC 2 Type II"
      priority: must
      source: "8 of 10 SERP titles"
      heading: "H2: Type I versus Type II"
  outline:
    - level: h2
      text: "What auditors actually test"
      words: 240
      entities: ["observation window"]
      evidence: "screenshot of evidence tracker"
  internal_links:
    - from: "/guides/soc2"
      to: "/checklists/soc2-readiness"
      anchor: "SOC 2 readiness checklist"
      status: 200
  external_sources:
    - claim: "Type II covers a minimum observation period"
      url: "https://example.org/standard"
      date: "2025-09-01"
  experience_requirements:
    original_assets: ["redacted evidence tracker screenshot", "auditor interview"]
    author: "named practitioner with audit experience"
    reviewer: "qualified compliance reviewer"
  acceptance:
    must_cover_complete: true
    original_evidence_planned: true
    answer_block_written: true
  refresh_plan:
    review_in_days: 180
    triggers: ["standard revision", "ranking drop over 5 positions"]
```

## Checklist

- [ ] Target query, locale, language, and device recorded.
- [ ] Intent classified with SERP evidence.
- [ ] SERP review dated, logged out, and locale-correct.
- [ ] Must-cover entities capped at 8 to 12 and mapped to headings.
- [ ] Answer block resolves the query in 60 words or fewer.
- [ ] Outline has one H1 and a logical H2/H3 tree.
- [ ] Word targets derive from section jobs, not competitor averages.
- [ ] Internal links resolve and anchors are descriptive.
- [ ] Every statistic has a primary source and date.
- [ ] Cannibalization checked before creating a new URL.
- [ ] Original evidence, author, and reviewer requirements named.
- [ ] Acceptance gates pass before the brief is assigned.

## Related skills

- `long-form-content-outlining` for turning the brief into section claims, budgets, and evidence requests.
- `brand-voice-consistency` for keeping titles, meta copy, and body text on voice.
- `source-grounded-citation-verification` for checking that published statistics match their cited sources.

---
name: video-script-storyboarding
description: Develops scripts, shot lists, and storyboards aligned to runtime, platform, and production constraints. Use for explainers, ads, and course videos.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: creative-content
---

# Video Script and Storyboarding

## Overview

A video script is a production plan, not an essay with timecodes. Scripts fail when the narration is written to runtime by feel, when visuals are described after the shoot is booked, and when the edit discovers that the required shot was never captured. The fix is arithmetic and coverage: estimate duration from word count, prove that every line has a shot, and check feasibility before the crew is scheduled.

This skill produces a beat sheet, a two-column audio and visual script, a numbered shot list with durations, and storyboard frames with on-screen text that survives small screens.

## When to use

- Writing an explainer, product demo, ad, or course video.
- Converting a webinar, article, or deck into a video treatment.
- Planning a shoot and need a shot list that the crew can execute.
- Reviewing a script for runtime fit before recording or animation.
- Repurposing one long video into platform-specific cuts.
- Do not use for audio-only podcasts or live event run-of-show; use an audio or event brief instead.

## Workflow

### 1. Lock the delivery brief

| Field | Why it changes the script | Example (illustrative) |
| --- | --- | --- |
| Objective | One action the viewer takes | Start a free trial |
| Audience | Determines vocabulary and proof | Developers evaluating an API |
| Platform and placement | Sets aspect ratio, safe zones, sound assumptions | YouTube pre-roll, 16:9, sound on |
| Runtime | Constrains beats and words | 60 seconds, hard cap 63 |
| Format | Live action, animation, screen capture, mixed | Screen capture plus lower thirds |
| Budget and shoot days | Limits locations, talent, and coverage | One shoot day, one presenter |
| Accessibility | Captions, audio description, contrast | Burned-in captions for social cut |

Confirm platform specs at production time; they change. Record the source and date rather than trusting memory.

### 2. Choose a beat structure and do the math

```text
Narration duration ≈ words ÷ 2.5   (150 words per minute, moderate pace)
On-screen reading time ≈ words ÷ 3  (plus 0.5 s per line for scanning)
Total runtime = narration + pauses + title/end cards
```

Beat sheet for a 60 second explainer:

| Beat | Time | Job | Word budget |
| --- | --- | --- | --- |
| Hook | 0:00-0:04 | Name the pain or the promise | 10 |
| Setup | 0:04-0:12 | Stakes and who this is for | 20 |
| Mechanism | 0:12-0:34 | How it works, one idea per shot | 55 |
| Proof | 0:34-0:46 | Demo, number, or customer evidence | 30 |
| Objection | 0:46-0:53 | Address the main hesitation | 18 |
| CTA | 0:53-1:00 | One action, one destination | 17 |

Total word budget for 60 seconds at 2.5 words per second is about 150. Include a 10 percent buffer; do not plan to 100 percent.

### 3. Write the two-column script

```text
00:00-00:04
VIDEO: Close on a developer staring at a failing deploy log. Screen glow, no music.
AUDIO: "Your deploy failed again. The log says nothing useful."
ON-SCREEN: Deploy failed: unknown error
```

Rules:

- Write for the ear: short sentences, contractions, one clause per breath.
- Put the visual instruction before the line so the shot is not an afterthought.
- Every claim in narration needs a visual or a cited source in the proof beat.
- Mark pronunciation for product names and technical terms.
- Number every line so the edit and the voiceover session share references.

### 4. Build the numbered shot list

| Shot | Time | Framing | Movement | Subject | Location | Duration | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | 0:00-0:04 | ECU | Static | Monitor with error text | Desk set | 4.0 s | Practical glow, no flicker |
| 02 | 0:04-0:08 | MS | Slow push | Presenter to camera | Desk set | 4.0 s | Leave right third for text |
| 03 | 0:08-0:12 | Screen | None | Terminal, typed live | Screen capture | 4.0 s | Record at 60 fps, scale 125 percent |

Coverage rules: no single shot longer than 8 seconds in an explainer, no more than three consecutive shots of the same subject and framing, and a visual change at least every 5 seconds. If a line has no shot, the line is a candidate for cutting.

### 5. Storyboard the key frames

Sketch or describe one frame per shot change. Include camera height, lens feel, and the position of on-screen text.

- Keep on-screen text to 6 words per line and 2 lines per frame.
- Keep text inside the platform safe zone (about 10 percent margin on each edge).
- Minimum legible size in a 1080x1920 vertical cut: roughly 40 px for body text; verify on a phone, not a monitor.
- Maintain 4.5:1 contrast for text over imagery; add a scrim if the background moves.
- Reserve the lower third for captions, not for critical UI.

### 6. Run the production feasibility pass

| Constraint | Check | Fail action |
| --- | --- | --- |
| Shoot day | Sum of setup and shot time plus 30 percent | Cut shots or add a day |
| Locations | Unique locations per day | Combine or schedule a second day |
| Talent | Presenter available for all sync lines | Convert to voiceover or split the shoot |
| Permissions | Releases, location access, music license | Replace asset or clear rights before shooting |
| Screen capture | Demo environment stable and seeded | Record a fallback and a backup take |
| Animation | Seconds of animation versus artist capacity | Reduce or simplify transitions |
| Accessibility | Captions, audio description, flashing limits | Add before lock |

Check rights: music, stock footage, fonts, and client logos each need a license that covers the placement and territory. "We found it online" is not a license.

### 7. Time, review, and lock

Record a table read and time it with a stopwatch. If narration exceeds the target by more than 10 percent, cut lines rather than speed up the read. Build an animatic (storyboard plus scratch VO) and watch it end to end. Lock picture and script before the shoot, then version the document.

```text
v0.3  2026-11-20  script locked, 58.2 s table read
v0.2  2026-11-18  cut beat 4 by 6 s, added proof clip
v0.1  2026-11-16  first draft, 71 s
```

## Validation

| Gate | Check | Pass criterion | Fail action |
| --- | --- | --- | --- |
| Runtime | Words divided by 2.5 plus cards and pauses | Within plus or minus 10 percent of target | Cut lines |
| Coverage | Every script line mapped to a shot | Zero lines without a shot ID | Add shot or cut line |
| Shot duration | Sum of shot durations | Equals runtime within 1 second | Rebalance shot list |
| Visual pace | Longest static run | No shot over 8 s, no 5 s without a change | Add coverage |
| Legibility | Text over video on a phone | 6 words per line, inside safe zone, 4.5:1 contrast | Rewrite text |
| Rights | Music, footage, fonts, logos | All licensed for placement and territory | Replace asset |
| Accessibility | Captions and description | Captions complete, flashing under 3 Hz | Fix before delivery |
| CTA | Action and URL | One action, on screen for 3 s or more | Re-time the close |

Timing check:

```python
lines = [
    {"id": "01", "words": 10, "shot": "01"},
    {"id": "02", "words": 20, "shot": "02"},
]
seconds = sum(l["words"] for l in lines) / 2.5
assert all(l["shot"] for l in lines), "unmapped line"
print(f"estimated narration: {seconds:.1f} s")
```

## Gotchas

- Scripts written to feel long overrun by 20 percent. Count words and divide by 2.5 before approval.
- The hook gets the most effort and the CTA gets one second. Budget the close in the beat sheet.
- Visuals described after the shoot become wishful stage directions. Write the shot before the line.
- Narration and on-screen text repeat each other. Make them complementary: one says why, the other shows what.
- Vertical cuts inherit 16:9 compositions. Reframe for the aspect ratio instead of center-cropping.
- Music rights cover one placement, not all platforms. Confirm territory, term, and channel.
- Burned-in captions cannot be corrected after delivery. Proof them with a second reader.
- Flashing and rapid cuts can trigger seizures. Keep flashes under 3 Hz and avoid full-frame strobes.
- Presenter lines are written in prose paragraphs. Break them into breath-sized chunks for teleprompter.
- Stock footage shows the wrong product or a competitor logo. Review every frame at full size.
- Animation time is estimated from final frames, not keyframes. Add review and render time to the schedule.
- One script is reused for every placement. Version each cut with its own runtime and safe zones.

## Output contract

```json
{
  "brief": {
    "objective": "one action",
    "audience": "...",
    "platform": "YouTube pre-roll",
    "aspect_ratio": "16:9",
    "target_runtime_s": 60,
    "format": "screen capture plus presenter",
    "constraints": ["..."]
  },
  "beats": [
    {"name": "hook", "start_s": 0, "end_s": 4, "job": "...", "word_budget": 10}
  ],
  "script": [
    {"line_id": "L01", "start_s": 0, "end_s": 4, "audio": "...", "video": "...", "on_screen": "...", "shot_id": "01"}
  ],
  "shot_list": [
    {"shot_id": "01", "start_s": 0, "duration_s": 4, "framing": "ECU", "movement": "static", "subject": "...", "location": "desk set", "notes": "..."}
  ],
  "storyboard": [
    {"shot_id": "01", "frame": "description or path", "text_safe_zone": true, "contrast_ratio": 5.1}
  ],
  "timing": {"words": 150, "narration_s": 60.0, "variance_pct": 0.0, "table_read_s": 58.2},
  "rights": [{"asset": "track A", "license": "...", "territory": "...", "expires": "2027-06-30"}],
  "accessibility": {"captions": "burned-in plus SRT", "flashing_hz": 0, "audio_description": false},
  "version": "v0.3"
}
```

## Checklist

- [ ] Objective, audience, platform, ratio, and runtime locked.
- [ ] Platform specs verified and dated.
- [ ] Beat sheet sums to the target runtime.
- [ ] Word budget counts at 2.5 words per second with buffer.
- [ ] Script written for the ear with numbered lines.
- [ ] Every line mapped to a shot ID.
- [ ] Shot list has framing, movement, subject, location, and duration.
- [ ] Storyboard text fits safe zones and contrast rules.
- [ ] Rights confirmed for music, footage, fonts, and logos.
- [ ] Table read or animatic timed within 10 percent.
- [ ] Accessibility requirements met before lock.
- [ ] One CTA, on screen long enough to act.

## Related skills

- `long-form-content-outlining` for sourcing the argument and evidence that the video compresses.
- `brand-voice-consistency` for narration tone and terminology across cuts.
- `technical-documentation-writing` for accurate product steps in demos and screen capture.

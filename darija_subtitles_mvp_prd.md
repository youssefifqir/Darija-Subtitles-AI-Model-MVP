# PRD: AI Subtitles for Moroccan Darija — MVP

**Status:** Draft for review
**Owner:** [you]
**Product name:** TBD

---

## 1. One-liner

An AI subtitle and transcription tool built specifically for Moroccan Darija video content — accurate on code-switched, colloquial, regionally-varied speech in a way generalist Arabic-dialect tools aren't, and designed to get *more* accurate the more it's used.

## 2. Problem

- Commercial ASR (Google, Azure, AWS) transcribes Modern Standard Arabic well; Darija — an uncodified spoken dialect blending Arabic, French, Spanish, and Amazigh influences — is a different problem entirely and is poorly served.
- Human subtitling agencies produce good Arabic captions but are slow (24h+ typical turnaround) and expensive (~$2.25+/min).
- Existing AI players split into two camps, and neither is optimizing for what we think actually matters:
  - **Breadth-first** (ArabCap: 6 dialects) — spreads training/product effort thin across dialects instead of going deep on any one.
  - **Speed-first** (DarijaCC: Darija-only, ~20s turnaround claim) — fast and dialect-specific, but nothing published suggests an accuracy moat or a way to keep improving.
- The specific failure mode that breaks Darija subtitles isn't obscure vocabulary — it's **French/Spanish code-switching**. Independent benchmarking (Atlasia's MoulSot project) found GPT-4o and ElevenLabs both mangled or mistranscribed code-switched Darija phrases; this is a known, common, and fixable failure point competitors aren't clearly solving.

## 3. Target user (MVP)

**Primary:** Independent Moroccan and diaspora content creators — YouTubers, podcasters, TikTok/Reels creators — producing regular Darija video who need captions for accessibility, reach (captions materially boost watch-through and algorithmic distribution), and audiences who read along without sound.

**Explicitly not MVP focus:** enterprises, localization agencies, live/broadcast captioning. These are v2+ once the core accuracy claim is proven.

## 4. Competitive snapshot

| Player | Angle | Gap we can exploit |
|---|---|---|
| ArabCap | Multi-dialect breadth (Darija, Masri, Khaleeji, Levantine, etc.) | Generalist model likely underperforms a Darija-dedicated one on code-switching and regional accent |
| DarijaCC | Darija-only, fast, simple | No visible data/correction flywheel — static accuracy over time |
| Exemplary AI | Broad Arabic dialect support + styling/customization | Not Darija-specialized; customization-first, not accuracy-first |
| Human agencies (HappyScribe etc.) | High accuracy, native linguists | Slow (24h+), expensive ($2.25+/min) — wrong tool for a creator posting daily |

## 5. Why this wins (the actual thesis)

1. **Darija-only at launch.** No shared model capacity spent on five other dialects. Every fine-tuning cycle makes this product better at exactly one thing.
2. **Code-switching as a first-class design constraint**, not an edge case — reflected in model selection, evaluation set, and prompt/fine-tuning design.
3. **A compounding data flywheel.** Every subtitle correction a user makes is captured and periodically folded back into fine-tuning. Competitors shipping a static model get worse, relatively, every month we don't. This is the actual moat — not the UI.
4. **Cost structure.** Self-hosted open-source models on serverless GPU infra means a materially lower cost base than agencies and probably than API-wrapper competitors — this funds either better margins or a lower price to undercut on.

## 6. MVP scope

### In scope
- Upload video/audio (MP4, MOV, MP3, WAV) or paste a YouTube/TikTok/Instagram link
- Batch pipeline: VAD → Darija ASR → segment-level timestamps → subtitle formatting
- Minimal review screen: video playback with subtitle overlay, click a line to fix its text. No waveform, no drag-to-retime, no multi-track editing.
- Export: SRT, VTT, TXT
- Accounts + simple usage-based pricing (credits or free-minutes-per-month)
- Silent correction logging — every manual text edit is captured as future fine-tuning data (user-visible only as "help us improve accuracy," no separate workflow required of them)

### Explicitly out of scope for MVP (deferred, not forgotten)
| Feature | Why deferred | Target phase |
|---|---|---|
| Burned-in styled captions | Nice-to-have, not the accuracy differentiator | v1.1 |
| Additional dialects (Algerian, Tunisian, etc.) | Prove Darija depth first | v2 |
| Live/real-time captioning | Different infra problem entirely | v2+ |
| Speaker diarization | Adds compute cost with limited MVP value | v1.1 |
| Full timeline/waveform editor | You called this correctly — not the wedge | v1.1, if users actually ask for it |
| Public API | Validate the core product with real users first | v1.1 |
| Dual-language / translated exports | Scope creep for MVP | v2 |

## 7. Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| F1 | Accept file upload up to [X] min / [Y] MB | P0 |
| F2 | Accept a public video URL and extract audio server-side | P0 |
| F3 | Run VAD → ASR → subtitle-segment pipeline, return SRT/VTT/TXT | P0 |
| F4 | Show processing status (queued / processing / done) | P0 |
| F5 | Simple in-browser text-only correction of generated subtitles | P0 |
| F6 | Log every correction (original text, corrected text, audio segment ref) to a training-data store | P0 |
| F7 | Download exports in SRT, VTT, TXT | P0 |
| F8 | Basic auth + usage metering | P0 |
| F9 | Burned-in caption export | P1 (post-MVP) |
| F10 | REST API access | P1 (post-MVP) |

## 8. Model & accuracy bar

Don't launch on a guessed WER number — set the bar empirically:

1. Build a small internal test set (20-30 min) from real target content: a mix of genres and accents your actual users will upload.
2. Run the benchmark script from earlier against every open-source Darija checkpoint, plus Google Cloud STT's `ar-MA` Chirp_3 model as a commercial baseline, plus DarijaCC's own output on the same clips if feasible.
3. **Launch bar: the shipped model must be clearly and consistently better than the best free/commercial baseline on your own test set** — not just better than a public leaderboard number, which won't reflect your real content mix.
4. Re-run this evaluation after every fine-tuning pass on flywheel data, and don't ship a new checkpoint unless it beats the previous one on the held-out set.

## 9. Non-functional requirements

- **Turnaround:** competitive bar is DarijaCC's ~20s claim for short clips; realistic MVP target is "faster than the creator would take to type it themselves" — a few minutes for a typical 10-15 min video is acceptable at launch, optimize later.
- **Cost per audio-minute:** must stay meaningfully below the $2.25/min human-agency anchor — validate against actual rented-GPU throughput once the pipeline is built, don't assume.
- **Data handling:** creator content is often unpublished/pre-release — treat uploaded audio/video as confidential by default, auto-delete raw media after a defined retention window, keep only the derived training corrections (with consent) longer-term.
- **Availability:** best-effort for MVP; formal uptime SLAs are a v1+ concern.

## 10. Success metrics

- Videos processed / week (adoption)
- **Edit rate**: % of words corrected per video — this is both a product quality metric *and* the flywheel signal. Track it trending down over time as proof the moat is working.
- Retention: % of users who upload a second video within 30 days
- Cost per audio-minute vs. revenue per audio-minute (unit economics)

## 11. Business model (rough)

- Free tier: small monthly minute allowance to get creators trying it
- Paid: per-minute credits or a flat monthly subscription with a minute cap
- Price meaningfully below $2.25/min (human-agency anchor) — exact number depends on validated unit costs from step 9

## 12. Technical approach (summary, see prior discussion for full detail)

Self-hosted open-source Darija ASR (benchmark `atlasia/moulsot.v0.3` against Whisper-family Darija fine-tunes on your own test set) → VAD-based segmentation → serverless/spot GPU workers behind a job queue → SRT/VTT/TXT export → correction logging feeding periodic LoRA fine-tuning.

## 13. Risks & open questions

- **Accuracy risk:** none of the current open checkpoints may be "good enough" out of the box. Mitigation: budget time for an initial fine-tuning pass on curated data *before* public launch, not after.
- **Cold start:** the flywheel needs volume to matter — early users see today's accuracy, not the improved future version. Mitigation: front-load quality with your own fine-tuning pass rather than relying on the flywheel from day one.
- **Data licensing:** some public Darija datasets (e.g. YouTube-scraped corpora) have unclear commercial-use terms — confirm before using them to train a product you're charging for.
- **Competitive response:** nothing stops DarijaCC or ArabCap from adding their own correction loop once they see it working — the real defensibility is compounding faster than they do, not the idea itself.

## 14. Phased roadmap

| Phase | Goal |
|---|---|
| 0 | Benchmark existing checkpoints on your own test set, pick a starting model |
| 1 | Build the batch pipeline end to end (script, no UI) |
| 2 | Minimal web product: upload, process, review/correct, export — closed beta with a small group of real Darija creators |
| 3 | Public launch, once edit-rate data shows the model is genuinely competitive against free baselines |
| 4 (post-MVP) | Burned-in captions, API access, second dialect |

## 15. Open decisions (need your input)

- Product name / brand
- Exact free-tier minute allowance and paid pricing
- Which specific creators to recruit for closed beta, and how

# Competition checklist (2026-27 season) — written 2026-09-05

Fair: Connecticut Science & Engineering Fair (CSEF), ISEF-affiliated.
Entry type: first-time entry (no Form 7 continuation). Project category:
Environmental Engineering or Earth & Environmental Sciences (computational).
Adult sponsor: **not yet secured — critical path.**

## Dates (from the CSEF site, screenshot 2026-09-05)

| Date | What | Owner | Status |
|---|---|---|---|
| Sept 12 | Ask counselor to name a science teacher as adult sponsor | Vihaan | **OVERDUE** as of 2026-09-18; nudge drafted in notes/SPONSOR_ASK.md |
| Sept 19 | Fallback: any faculty member agrees to sponsor | Vihaan | due tomorrow; cold ask drafted in notes/SPONSOR_ASK.md |
| **Sept 25** | **HARD STOP: Forms 1A, 1, 3, 1B signed.** No hands-on work before this (notes/LAB_PROTOCOL.md s1) | Vihaan + sponsor + supervisor | open |
| Sept 28 | First hands-on work: build the rake, jar rig, controller | Vihaan | blocked by Sept 25 |
| Oct 15 | Deadline to seek approval for independent-student status (only if the school does not register) | Vihaan | n/a if school registers |
| Oct 31 | School registration closes 11:59 pm | school + Vihaan | open |
| Nov 15 | Registration due for independent student projects | (fallback path) | n/a |
| Dec 1 | All high-school registrations close 11:59 pm | Vihaan | open |
| Feb 15 | High-school projects selected by school fairs due 11:59 pm | Vihaan | open |
| Feb 25 | Upload portal opens | Vihaan | open |
| mid-March | Fair | | |
| ~mid-April 2027 | Stockholm Junior Water Prize, US state round (via WEF member association; 20-page paper) | Vihaan | open |

## ISEF forms

- Form 1 (Checklist for Adult Sponsor): sponsor signs.
- Form 1A (Student Checklist + Research Plan): use notes/ISEF_RESEARCH_PLAN.md;
  sign **before** the first prospective forecast is issued.
- Form 1B (Approval Form): student, parent, sponsor signatures, dated before
  the new work starts.
- Form 3 (Risk Assessment): **required.** The device workstream uses PAC powder
  (an acidic aluminium coagulant), a home-built 12 V electrical device and
  protist cultures. Designated Supervisor (school chemistry teacher, also named
  on Form 1) and Adult Sponsor both sign. Form 3 only — no SRC pre-review
  (notes/DEVICE_PROTOTYPE.md s6).
- **All four (1A, 1, 3, 1B) signed by Fri Sep 25, 2026**, before the first
  hands-on work on Mon Sep 28 (notes/LAB_PROTOCOL.md s1; DEVICE_PROTOTYPE.md s6).
- Not needed: Form 2 (Qualified Scientist) — optional for computational work on
  public data; Forms 4–7 — no human, vertebrate, PHBA, or continuation.
- Regulated Research Institution form: no; computational work done at home on
  public data. The bench work is done at school under the Designated Supervisor.

_2026-09-18: corrected. This block previously read "Form 3 (Risk Assessment) —
no hazards", which contradicted DEVICE_PROTOTYPE.md s6 and LAB_PROTOCOL.md s11;
Form 3 is required. The forms deadline is Fri Sep 25, not the Oct 5 shown in the
deliverables row below (now also corrected)._

## Deliverables and where they come from

| Deliverable | Source | Target date |
|---|---|---|
| Research plan | notes/ISEF_RESEARCH_PLAN.md | Sept 12 draft; final with sponsor |
| Abstract (250 words, five elements) | notes/ABSTRACT.md, written after the prospective readout | Jan |
| Paper (also serves SJWP) | notes/PAPER_OUTLINE.md rewrite → paper | Nov–Jan |
| Board / poster text | notes/BOARD.md | Jan |
| Judge Q&A sheet | notes/BOARD.md appendix | Jan |
| Project data book / log | git history of both repos + SCIENTIFIC_METHOD.md | continuous |
| Figures | figures/ in both repos; atlas screenshot | Jan |
| Device (Phase 11, MVP): order CCMP1332 + kaolin, PAC powder, magnetite pigment, **22** N52 blocks, square tube, ESP32 | notes/DEVICE_PROTOTYPE.md s3, s7; quote sheet notes/ORDER_LIST.md | **Sept 16-18** (was Sept 21, which is Yom Kippur; block count cut from 24 to 22 by Amendment A1) |
| Device: Forms 1/1A/1B/3 signed, Designated Supervisor (chemistry teacher) named | DEVICE_PROTOTYPE.md s6; LAB_PROTOCOL.md s1 | **Fri Sep 25** (was Oct 5; corrected 2026-09-18) |
| Device: week-1 chemistry + stock-preparation pilot; clay-only blank (gate) | SCIENTIFIC_METHOD.md Phase 11 | Oct 9 / Oct 23 |
| Device: three-arm jars, dose screen, 3 tank runs, board panel | DEVICE_PROTOTYPE.md s3, s9 | Nov 9 - Dec 18 |

## Outside contacts

| Who | For | Sent | Reply | Next nudge |
|---|---|---|---|---|
| CT DEEP (K. O'Brien-Clayton) + UConn (J. O'Donnell, T. Fake) | 2014 method/column change (corrected-to-raw ratio 0.4 -> 0.8 in 2014, corrected empty 2022-24); 2026 cruises to ERDDAP | 2026-09-14 (reply on June thread) | UConn replied 2026-09-17 (see the UConn row below); DEEP silent so far | Sept 28, DEEP only |
| UConn (J. O'Donnell) | same 2014 question; presenting the work to his team | 2026-09-14 (on the joint DEEP/UConn thread) | **2026-09-17 — replied, interested in the work, offered a slot to present to his team once he is back from a conference** | Vihaan replied 2026-09-17 with availability (Mondays, Thursdays, Fridays); waiting on a time. Follow up if no time proposed by **Sep 25** |
| IEC (S. Wilder, cc E. Powers) | 2026 posting date / early share; IEC chlorophyll method stable through 2014? | 2026-09-14 | — | Sept 28 |
| CT DEEP (M. Becker, E. Marquis) | same 2014 question | not sent (drafts gone) | — | only if the thread above is silent by Sept 28 |
| College counselor | sponsor referral | 2026-09-05 | — | Sept 12 |
| UConn LISICOS PI | fallback for buoy data questions | — | — | Oct 1 if DEEP silent |
| RIDEM Narragansett Bay program | training-bay confirmation | — | — | Oct 1 |

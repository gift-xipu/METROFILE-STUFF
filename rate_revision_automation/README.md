# Rate Revision Automation — New User Guide

A "press a button" workflow that generates every client price-increase letter and rate
schedule due in a given month, lets you review them, and sends them to the right sales
person by email.

This document explains the whole system from scratch — no prior context assumed.

---

## Contents

1. [The problem this solves](#1-the-problem-this-solves)
2. [Key concept: Price Levels](#2-key-concept-price-levels)
3. [Key concept: the 3-month notice rule](#3-key-concept-the-3-month-notice-rule)
4. [The big picture — how the pieces fit together](#4-the-big-picture--how-the-pieces-fit-together)
5. [Building block 1: the Tracker](#5-building-block-1-the-tracker)
6. [Building block 2: the Master Rate Table](#6-building-block-2-the-master-rate-table)
7. [Building block 3: the Streamlit App](#7-building-block-3-the-streamlit-app)
8. [The app, step by step](#8-the-app-step-by-step)
9. [Your monthly checklist](#9-your-monthly-checklist)
10. [What to watch out for](#10-what-to-watch-out-for)
11. [Glossary](#11-glossary)

---

## 1. The problem this solves

| Before | After |
|---|---|
| ❌ Every letter typed by hand, one client at a time | ✅ One click generates every letter due this month |
| ❌ Rates copied out of separate PDFs per client | ✅ Rates pulled automatically from one master table |
| ❌ 100+ clients tracked across scattered spreadsheets | ✅ Every client's status tracked in a single spreadsheet |
| ❌ Easy to miss the 3-month notice deadline | ✅ The 3-month deadline is calculated for you |
| ❌ No record of what's been sent and what hasn't | ✅ A clear Sent / Not Sent record for every client |

---

## 2. Key concept: Price Levels

Every client is linked to a **Price Level** — an ID that points to the exact rates they
pay. New clients start on the Standard price level; as they negotiate, they get their own.

### Anatomy of a Price Level

```
   JHB          1234
   ────         ────
Region code   Unique 4-digit ID
```

### Standard vs. negotiated

| | |
|---|---|
| **`POL0000012`** | The Standard / Master price level. Every new client starts here. |
| **e.g. `JHB1234`, `NAT2612`** | A negotiated price level, unique to one client's agreement. |

> **Regional vs. National:** Most price levels apply to one region (JHB, CPT, DBN…).
> Some clients operate branches across the whole country and are given a **National**
> price level (`NAT…`) instead — one rate, applied everywhere they operate.

---

## 3. Key concept: the 3-month notice rule

Every client must be told about their rate increase **3 months before it takes effect**,
so the sales person has time to prepare the client.

```
   Notification Due Date              Rate Increase Month
      01 April 2027    ── 3 months ──►    01 July 2027
            │                                   │
  System flags the client —           New rates take effect
  sales must notify them by now       automatically on the account
```

This is exactly what the **"Notification Due Date"** column in the Tracker calculates
for you — and it's the filter the automation uses to decide which clients belong in a
given month's batch.

---

## 4. The big picture — how the pieces fit together

```
 Tracker          Master Rate       Templates         Streamlit         Outlook
 ───────          Table             ─────────         App               ───────
 Who, when,   →   The actual   →    Your real    →    Generate,    →    Letter +
 which price      rate for          letter, with      review,           schedule
 level             every level      blanks            send — the        attached
                                                        button            & sent
```

- The **Tracker** and **Master Rate Table** hold your data.
- The **Templates** define what a letter and rate schedule look like.
- The **Streamlit App** is the only piece you actually click on — it reads the data,
  fills in the templates, and hands the finished letter + schedule to Outlook to email
  the right sales person.

---

## 5. Building block 1: the Tracker

**File:** `Rate_Revision_Schedule.xlsx` — the single source of truth.

One row per client. This is the **only** file anyone edits by hand — add a client,
change a sales person, or move an increase month here, and everything downstream
follows automatically.

| Column | What it's for |
|---|---|
| Price Level | Which rate table to use |
| Region | Where the client is based |
| Client Name | Who the letter goes to |
| Sales Person + Email | Who gets notified |
| Rate Increase Month | When new rates apply |
| Notification Due Date | Auto-calculated: 3 months before the increase |
| Price Schedule / Letter Sent | Status tracking |
| Comments | Exceptions, notes |

---

## 6. Building block 2: the Master Rate Table

**File:** `master_rates.xlsx` — every price level's actual rates, in one place.

One row per Price Level per charge line (Storage, Transport, Handling, and so on). When
the app builds a client's rate schedule, this is the table it looks the numbers up in —
nobody re-types a rate by hand.

| Price Level | Category | Item | Charge Code | Rate |
|---|---|---|---|---|
| POL0000012 | Storage | SM2 Carton | SM2 | R 5.03 |
| JHB1234 | Storage | SM2 Carton | SM2 | R 5.29 |
| NAT2612 | Transport | New Box Collection | CB | R 26.86 |

> ⚠️ **Right now, most of this table is placeholder data.** Only the Standard rate
> (`POL0000012`) is real, taken from the existing rate card. Every negotiated client's
> real rates still need to be entered here — the app clearly flags which clients are
> running on placeholder numbers so nothing gets sent by accident with the wrong figures.

---

## 7. Building block 3: the Streamlit App

**File:** `app.py` — the only screen anyone needs to open each month.

| Step | What it does |
|---|---|
| **1. Generate** | Pick a month. The app finds every client due for notification. |
| **2. Review** | Check the letters and rate schedules it built, one client at a time. |
| **3. Send** | Preview, draft, or send — your choice, with a confirmation step. |

Run it with:

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 8. The app, step by step

### Step 1 — Generate

Clicking **Generate pack**:

- Reads every row in the Tracker
- Works out each client's Notification Due Date (3 months before their increase)
- Keeps only the clients due in the month you picked
- Looks up each client's rates in the Master Rate Table
- Builds a personalised letter (`.docx`) and rate schedule (`.xlsx`) for every match
- Files everything neatly by sales person, ready to review

**Output structure:**

```
output/
  └─ Sales Person A/
       └─ Client X/
            • Letter.docx
            • Rate Schedule.xlsx
  └─ Sales Person B/ ...

  └─ email_manifest.xlsx
```

### Step 2 — Review

The review table shows every matched client:

| Client | Price Level | Sales Person | Effective Date | Rates |
|---|---|---|---|---|
| Highveld Motors (Pty) Ltd | PE1832 | Andre Kruger | 01 July 2027 | ✅ Standard |
| Baobab Packaging (Pty) Ltd | PE4919 | Pieter Fourie | 01 July 2027 | ⚠️ Placeholder |

- **✅ Standard / Real rates** — safe to send as-is
- **⚠️ Placeholder rates** — a negotiated price level with no real rates loaded yet;
  check before sending
- Preview any individual letter or rate schedule, or download everything as one zip

### Step 3 — Send it, three ways

| Mode | What happens |
|---|---|
| **Dry Run** | Shows exactly what would be sent to whom. Nothing happens. |
| **Create Drafts** | Builds real Outlook drafts so a manager can check them before anything sends. |
| **Send Now** | Actually emails every sales person. Requires ticking a confirmation box first. |

> **Important:** Create Drafts and Send Now only work when the app is running on the
> Windows machine with Outlook installed and logged in — that's what actually gets
> driven. Running it anywhere else, it safely falls back to Dry Run.

---

## 9. Your monthly checklist

1. Open a terminal in the project folder and run `streamlit run app.py`
2. Pick the current month and click **Generate pack**
3. Read the review table — note any client flagged **⚠️ Placeholder rates**
4. Open a couple of letters/schedules to sanity-check names, dates and figures
5. Choose **Create Drafts** first, and have someone check the drafts in Outlook
6. Once happy, come back, choose **Send Now**, tick the confirmation box, and execute
7. Update the Tracker's Sent columns so everyone can see it's done

---

## 10. What to watch out for

**Most rates are still placeholder data.**
Only the Standard price level's rates are real today. Every negotiated client needs its
real rates entered into the Master Rate Table before its letters are safe to send
unreviewed.

**Sending needs a specific machine.**
Real emails only go out from the Windows PC with Outlook installed and logged in.
Running the app elsewhere is fine for generating and reviewing, just not for sending.

**Nothing runs on its own — yet.**
Someone has to open the app and click Generate each month. A scheduled task or Power
Automate flow is the natural next step once the output is trusted.

**The Tracker is still the source of truth.**
Add clients, fix a sales person's email, or move an increase month — always edit the
Tracker, never the generated output files.

---

## 11. Glossary

| Term | Meaning |
|---|---|
| **Tracker** | The spreadsheet listing every client, their price level, sales person, and increase month. |
| **Master Rate Table** | The lookup table of actual rates for every Price Level. |
| **Price Level** | The ID (e.g. `JHB1234`) linking a client to their rates. |
| **Manifest** | The list the app builds of exactly who should be emailed what. |
| **Dry Run** | Preview mode — shows what would happen without doing it. |
| **Draft** | A real Outlook email created but not sent, for review. |

---

**Questions?** Reach out to the Pricing Team.

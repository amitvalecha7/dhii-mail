# 🛑 V1 Launch Readiness: Gap Analysis & Roadmap

## 📊 Executive Summary
**Current State**: Alpha (Technical Preview)
**Target V1 Criteria**: "Suite is able to analyze emails and calendar" (Sync + AI Analysis).
**Verdict**: **NOT READY**.

---

## 🔍 Gap Analysis

### 1. Transport Layer (The Senses) - ❌ MISSING
*   **Gap**: The system is currently "Passive". `EmailPlugin` and `Holo-Meet` read from a static/mock database. They do **not** run background syncs with Gmail/Outlook or CalDAV.
*   **Impact**: Users see no real data updates unless they manually insert rows into the DB. This fails the basic "Email Client" definition.

### 2. Intelligence Layer (The Brain) - ❌ MISSING
*   **Gap**: There is no "Loop" that processes incoming data. The `NeuralLink` is a UI placeholder.
*   **Impact**: The "Analysis" criteria (Summary, Urgency Scoring, Auto-Tagging) cannot be met.

---

## 🛠️ The Fix: "Intelligent Transport" Roadmap

We must pivot to implement the following hierarchy:

### Phase 1: The Active Sync Engine (Transport)
*   **Email Sync Service**: Background background worker polling IMAP.
*   **Calendar Sync Service**: CalDAV/Google API poller.

### Phase 2: The Neural Loop (Intelligence)
*   **Event Bus Triggers**: Sync Service -> emits `EMAIL_RECEIVED`.
*   **Analysis Processor**: Listens to Event -> Sends to LLM -> Stores Meta-Data.

### Phase 3: The Persistence Layer
*   **Migration**: Move `Holo-Meet` from In-Memory to SQLite/Postgres to prevent data loss on restart.

---

## 🏗️ Build Plan: Email Sync Engine (Immediate Priority)

### Architecture
*   **Component**: `EmailSyncService` (Background Asyncio Task in Kernel).
*   **Logic**:
    1.  Wake up every X minutes.
    2.  Check for `last_synced_uid`.
    3.  Fetch new UIDs from IMAP.
    4.  Download & Parse content.
    5.  Save to `received_emails` DB.
    6.  **Fire Event**: `EventType.EMAIL_RECEIVED` (This is key for Phase 2).

### Technical Tasks
- [ ] Add `last_synced_uid` to `email_accounts` table.
- [ ] Implement `plugins/email/services/sync_service.py`.
- [ ] Integrate startup/shutdown hooks in `EmailPlugin`.
- [ ] Add exponential backoff for network resilience.

**Recommendation**: Start execution on **Email Sync Engine** immediately.

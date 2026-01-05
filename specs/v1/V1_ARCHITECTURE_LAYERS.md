# V1 Architecture Layers: The Launch Stack

To achieve the goal *"Suit is able to analyze emails and calendar"*, we are implementing a 4-Layer Architecture.

## 1. Phase 5.1: The Transport Layer (The Senses)
**Goal**: Fetch Real Data.
*   **Email Sync Engine** (Completed): Background worker to poll IMAP and populate `received_emails`.
*   **Calendar Sync Engine** (Pending): Background worker to poll CalDAV/Google API and populate `events` table (replacing `Holo-Meet` mock data).
*   **Outcome**: The database reflects reality.

## 2. Phase 5.2: The Intelligence Layer (The Brain)
**Goal**: Make Data Useful.
*   **Event Bus Triggers**: Listen for `EMAIL_RECEIVED` and `EVENT_CREATED`.
*   **Analysis Service**:
    *   **Input**: Raw usage data (Email Body, Meeting Description).
    *   **Process**: Send to LLM (Gemini/OpenAI) with system prompt *"Analyze this for urgency, summary, and action items"*.
    *   **Output**: Structured JSON (Summary, Tags, Sentiment).
*   **Storage**: Save to `email_analysis` and `meeting_analysis` tables linked to the raw records.

## 3. Phase 5.3: The Application Layer (The Face)
**Goal**: Visualize the Intelligence.
*   **Smart Inbox**: Update UI to show "AI Summary" instead of just first lines.
*   **Intelligence Badges**: Display "Urgent", "Action Required" chips.
*   **Daily Briefing**: A dashboard widget aggregating the analysis (e.g., "3 Urgent Emails, 2 Conflicts").

## 4. Phase 5.4: The Persistence Layer (The Memory)
**Goal**: Prevent Data Loss.
*   **Holo-Meet Migration**:
    *   Current: `self.meetings = []` (Lost on restart).
    *   Target: SQLite `meetings` table.
*   **Secrets Management**: Secure storage for IMAP/CalDAV credentials using `cryptography` (Fernet) instead of current basic implementation.

---

## 📅 Roadmap to Launch
1.  **Email Sync** (Done)
2.  **Calendar Sync** (Next)
3.  **Intelligence Service** (High Value)
4.  **UI Integration** (Final Polish)

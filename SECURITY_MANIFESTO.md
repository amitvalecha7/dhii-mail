# Security & Privacy Manifesto (Issue #55)

**Status**: DRAFT  
**Version**: 1.0.0  
**Last Updated**: 2026-01-04

---

## 1. Core Philosophy: "Your Data, Your Device"

In an era of cloud-first surveillance capitalism, Dhii-Mail takes a radical stance: **The Kernel runs locally.**
We do not want your data. We do not store your emails. We do not train models on your private conversations without explicit, granular consent.

## 2. Data Handling Policies

### A. Local-First Architecture
*   **Storage**: All emails, contacts, and embeddings are stored in a local SQLite/DuckDB database within the user's home directory (`~/.dhii-mail/`).
*   **Sync**: Synchronization happens directly between the user's device and the provider (Gmail, Outlook) via IMAP/SMTP/Graph API. No intermediate Dhii-Mail servers process this data.

### B. Encryption
*   **At Rest**: The local database is encrypted using SQLCipher with a key derived from the user's master password.
*   **In Transit**: All network requests (even to localhost) use TLS 1.3.

## 3. The "Glass Wall" (Plugin Isolation)

Plugins are the biggest security risk. We mitigate this with the **Glass Wall** architecture.

### A. Network Air-Gapping
By default, a Plugin has **NO** internet access.
*   If a plugin needs to fetch a stock price, it must request `network.host: "api.finance.com"`.
*   The Kernel proxies this request. The plugin never touches the raw socket.

### B. File System Jail
Plugins can only read/write to their dedicated sandbox directory (`~/.dhii-mail/plugins/<plugin_id>/`). They cannot see other plugins' data or the user's documents.

## 4. User Consent Model

We reject "Accept All" permission dialogs.
*   **Just-in-Time Consent**: Permission is requested *when it is needed*.
    *   *Example*: A plugin asks "Can I read your calendar?" only when you click "Schedule Meeting".
*   **Human-Readable Scopes**: No opaque codes.
    *   ✅ "Allow 'Marketing Bot' to **READ** your **LAST 5 EMAILS**?"
    *   ❌ "Allow 'Marketing Bot' scope `https://mail.google.com/`?"

## 5. Audit & Transparency

### The "Black Box" Recorder
Every action taken by an Agent is logged to an immutable, user-accessible Audit Log.
*   "Agent X read Email Y at 10:00 AM."
*   "Agent Z sent data to `api.crm.com` at 10:05 AM."

The user can view this log at any time via the "Security & Trust" dashboard.

## 6. AI Safety

*   **Local Inference**: Whenever possible, we use SLMs (Small Language Models) running locally (e.g., Llama-3-8B via Ollama).
*   **Data Sanitization**: Before sending data to a cloud LLM (e.g., GPT-4), PII (Personally Identifiable Information) is redacted or tokenized unless explicitly allowed.

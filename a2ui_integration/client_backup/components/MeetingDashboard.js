import { LitElement, html, css } from 'lit';
import { glassStyles } from './styles.js';

export class MeetingDashboard extends LitElement {
    static properties = {
        meetings: { type: Array },
        emails: { type: Array },
        stats: { type: Object }
    };

    static styles = [
        glassStyles,
        css`
            :host {
                display: block;
                height: 100%;
                overflow-y: auto;
            }

            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 24px;
                padding: 24px;
            }

            .stats-row {
                grid-column: 1 / -1;
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
                margin-bottom: 8px;
            }

            .stat-card {
                text-align: center;
                padding: 16px;
            }

            .stat-value {
                font-size: 2rem;
                font-weight: 700;
                background: linear-gradient(to right, #fff, #a5b4fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .stat-label {
                font-size: 0.875rem;
                color: rgba(255, 255, 255, 0.7);
                margin-top: 4px;
            }

            .list-item {
                padding: 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .list-item:last-child {
                border-bottom: none;
            }

            .item-title {
                font-weight: 500;
                color: rgba(255, 255, 255, 0.9);
            }

            .item-subtitle {
                font-size: 0.8rem;
                color: rgba(255, 255, 255, 0.6);
            }

            .status-badge {
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.75rem;
                background: rgba(16, 185, 129, 0.2);
                color: #34d399;
            }
        `
    ];

    render() {
        return html`
            <div class="dashboard-grid">
                <!-- Stats Row -->
                <div class="stats-row">
                    <div class="glass-card stat-card">
                        <div class="stat-value">${this.stats?.totalMeetings || 0}</div>
                        <div class="stat-label">Meetings</div>
                    </div>
                    <div class="glass-card stat-card">
                        <div class="stat-value">${this.stats?.pendingEmails || 0}</div>
                        <div class="stat-label">Unread Emails</div>
                    </div>
                    <div class="glass-card stat-card">
                        <div class="stat-value">${this.stats?.activeVideoMeetings || 0}</div>
                        <div class="stat-label">Active Calls</div>
                    </div>
                    <div class="glass-card stat-card">
                        <div class="stat-value">${this.stats?.runningCampaigns || 0}</div>
                        <div class="stat-label">Campaigns</div>
                    </div>
                </div>

                <!-- Calendar Widget -->
                <div class="glass-card">
                    <div class="glass-header">
                        <span>Today's Schedule</span>
                        <button class="glass-btn">+ New</button>
                    </div>
                    <div class="list">
                        ${this.meetings?.map(m => html`
                            <div class="list-item">
                                <div>
                                    <div class="item-title">${m.title}</div>
                                    <div class="item-subtitle">${m.time}</div>
                                </div>
                                <span class="status-badge">Scheduled</span>
                            </div>
                        `)}
                        ${(!this.meetings || this.meetings.length === 0) ? html`<div class="list-item" style="justify-content:center; color:rgba(255,255,255,0.5)">No meetings today</div>` : ''}
                    </div>
                </div>

                <!-- Email Widget -->
                <div class="glass-card">
                    <div class="glass-header">
                        <span>Recent Emails</span>
                        <button class="glass-btn">Compose</button>
                    </div>
                    <div class="list">
                        ${this.emails?.map(e => html`
                            <div class="list-item">
                                <div>
                                    <div class="item-title">${e.subject}</div>
                                    <div class="item-subtitle">${e.from} • ${e.date}</div>
                                </div>
                                ${!e.read ? html`<span class="status-badge" style="background:rgba(239,68,68,0.2); color:#fca5a5">New</span>` : ''}
                            </div>
                        `)}
                         ${(!this.emails || this.emails.length === 0) ? html`<div class="list-item" style="justify-content:center; color:rgba(255,255,255,0.5)">Inbox zero!</div>` : ''}
                    </div>
                </div>
            </div>
        `;
    }
}

customElements.define('meeting-dashboard', MeetingDashboard);

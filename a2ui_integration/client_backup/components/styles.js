import { css } from 'lit';

export const glassStyles = css`
  .glass-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
    border-radius: 16px;
    padding: 20px;
    color: white;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.25);
    border-color: rgba(255, 255, 255, 0.3);
  }

  .glass-header {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: rgba(255, 255, 255, 0.95);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .glass-btn {
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 8px 16px;
    border-radius: 8px;
    color: white;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
  }

  .glass-btn:hover {
    background: rgba(255, 255, 255, 0.25);
  }
`;

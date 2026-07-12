# EcoSphere Frontend — ESG Dashboard 📊🌱

This directory contains the premium React + Vite + TypeScript frontend dashboard for the EcoSphere ESG platform.

## Features Implemented
1. **Interactive ESG Overview**: Displays weighted scores for Environmental (E), Social (S), and Governance (G).
2. **Emissions Trend Visualizer**: Interactive line and bar charts using `recharts`.
3. **Department Performance rankings**: Real-time tracking of organizational units.
4. **Interactive Carbon Logging**: Allows manual carbon transaction submissions which dynamically award user XP points.
5. **Governance Sign-off Flow**: Review active corporate policies and digitally sign/acknowledge them.
6. **Gamification & XP center**: Tracking user level, current XP progression, and unlocked achievement badges.

## How to Run Locally

### 1. Install Dependencies
Ensure you have [Node.js](https://nodejs.org) installed, then run:
```bash
npm install
```

### 2. Start Development Server
Boot up the local development hot-reload server:
```bash
npm run dev
```
Open the provided URL (e.g. `http://localhost:5173`) in your browser to view the interactive dashboard.

### 3. Build for Production
To generate optimized production bundle files in `dist/`:
```bash
npm run build
```

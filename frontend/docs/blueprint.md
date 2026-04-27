# **App Name**: Urban Flood Intelligence Platform

## Core Features:

- Geospatial Flood Risk Visualization: Displays Delhi wards on an interactive map, colored according to real-time and simulated flood risk levels, with detailed information on interaction.
- Predictive Flood Simulation Interface: Allows municipal authorities to simulate the impact of increased rainfall on ward-level flood risks in real-time, aiding proactive planning.
- Detailed Ward Analytics Panel: Provides a deep-dive analysis for selected wards, showing historical risk trends, drainage capacity vs. flood load, and estimated population at risk.
- Real-time Environmental Monitoring: Presents live weather conditions, including temperature, rainfall, and humidity, along with critical severe rainfall alerts.
- Critical Flood Hotspot Alerts: Identifies and lists top wards with high flood risk, providing quick access to details for priority action and response coordination.
- City-wide Readiness Assessment: Calculates and displays an aggregate City Readiness Score, offering a high-level overview of Delhi's overall flood preparedness.
- AI-Powered Mitigation Advisor: An AI tool that suggests ward-specific flood mitigation strategies and recommendations based on current flood risk, drainage capacity, and historical data.

## Style Guidelines:

- Primary interactive elements will use a vibrant, authoritative blue (accent-blue: #3B82F6; HSL 217, 92%, 60%) to signify critical functionality and build trust within the dark interface.
- The foundational color scheme will utilize a palette of deep, desaturated blue-grays (e.g., bg-base: #060D1A; HSL 217, 61%, 6%) for backgrounds and surfaces, creating a focused, 'government-grade' aesthetic.
- Functional accent colors such as distinct greens (risk-low: #22C55E), oranges (risk-medium: #F59E0B), and reds (risk-high: #EF4444) will provide immediate, high-contrast visual indicators for varying flood risk levels.
- Subtle borders and secondary textual elements will employ lighter, desaturated blue tones (e.g., text-muted: #6B8EB3; HSL 210, 31%, 65%) for clear hierarchy and readability without overpowering core data displays.
- Data and numerical displays will use 'IBM Plex Mono' (monospace) for precision and clarity. UI labels and general text will utilize 'Inter' (sans-serif) for its modern and neutral readability. Note: currently only Google Fonts are supported.
- Icons will be precise and clear, such as a prominent wave icon for branding, trend arrows (↑↓→) to indicate changes, and warning symbols (⚠) for alerts and simulation mode, all consistent with a data intelligence dashboard.
- The application will feature a full-viewport, fixed layout without page scrolling. A 56px height TopBar will be positioned above a primary content area split into a 60% width interactive Flood Map and a 40% width scrollable Sidebar. The HotspotPanel will appear as a slide-in overlay from the right, ensuring continuous map visibility.
- Interactive elements, particularly cards, will subtly glow blue on hover. High-risk wards will feature a pulsing CSS animation during simulation mode to draw immediate attention. The HotspotPanel will smoothly slide in from the right edge upon activation for a modern user experience.
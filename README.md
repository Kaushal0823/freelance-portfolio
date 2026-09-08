# Freelance Portfolio — 4 Starter Projects

These four projects cover the domains you picked, so your portfolio shows range: front-end, automation, data analysis, and full-stack.

## 1. Web Development — `web-landing/index.html`
A landing page for a fictional coffee roastery ("Ember & Oak Roasters"), built in plain HTML/CSS/JS — no framework, no build step. Shows you can deliver a polished, responsive business site, which is the single most-requested freelance web gig.
- **How to present it:** Open the file in a browser, or deploy free on Netlify/GitHub Pages, and link the live URL in your portfolio.
- **What it demonstrates:** responsive layout, custom design (not a template), working contact form (client-side), CSS animation, mobile breakpoints.

## 2. Python Automation — `python-automation/file_organizer.py`
A CLI tool that sorts a messy folder into sub-folders by file type and finds duplicate files by content hash (not just filename). Has a `--dry-run` safety mode.
- **How to present it:** Record a 30-second terminal screen capture showing `--dry-run`, then the real run. Put the recording + code on GitHub.
- **What it demonstrates:** real filesystem scripting, CLI design with `argparse`, hashing, and thinking about safety (dry-run) — the kind of "automate my repetitive task" job that's common on Upwork/Fiverr.

## 3. Data Analysis — `data-analysis/build_workbook.py` → `Sales_Analysis.xlsx`
Generates a year-half of synthetic retail sales data and builds an Excel dashboard from it: KPI cards, category/region/monthly breakdowns, top-5 products, and two charts — all using **live formulas** (SUMIF, INDEX/MATCH, LARGE), not hardcoded numbers, so the sheet recalculates if the raw data changes.
- **How to present it:** Share the `.xlsx` directly, or screenshot the Dashboard tab. Mention it uses formulas, not static values — clients doing "analyze my sales data" gigs care about that.
- **What it demonstrates:** pandas/openpyxl, Excel formula literacy, and dashboard design — the "analyze my Excel data" and "build me a dashboard" gig types.

## 4. Full Stack — `fullstack-app/TaskBoard.jsx`
A drag-and-drop task board (To do / In progress / Done) built in React, with a small "API layer" that persists every change so tasks survive a page reload — the same shape as a React frontend talking to a real backend.
- **How to present it:** Paste it into a Claude Artifact to demo live, or wire the storage calls to a real backend (Firebase/Supabase/Express) later — the component is already structured for that swap.
- **What it demonstrates:** React state management, async data flow, drag-and-drop UX, loading/error states — signals "can build a real app," not just a static page.

---

### Putting these on your freelance profile
1. Push all 4 to GitHub (one repo each, or one repo with 4 folders).
2. Write a 2-3 line description per project focused on **what problem it solves**, not just the tech used.
3. For the web page and task board, deploy them live (Netlify/Vercel are free) so clients can click and interact — a live link converts far better than a screenshot.

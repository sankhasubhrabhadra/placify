# Placify (Resume Scanner)

Small static site for coding practice and a built-in Resume Scanner.

## Overview

- Replaced the previous Job Board with a client-side Resume Scanner available at `jobs.html`.
- Scanner supports uploading PDF or plain-text resumes and pasting resume text.
- PDF text extraction uses `pdf.js` loaded from a public CDN.

## Key files

- `index.html` — Dashboard
- `jobs.html` — Resume Scanner page (upload/paste and scan)
- `script.js` — Application scripts; includes resume parsing and pdf.js integration
- `style.css`, `style-additions.css` — Styles

## Run locally

Serve the folder with a simple static server and open `jobs.html` in your browser.

Using Python 3 built-in server:

```bash
python -m http.server 8080
```

Or using `http-server` (npm):

```bash
npx http-server . -p 8080
```

Then open: http://localhost:8080/jobs.html

## Usage

- Upload a `.pdf` or `.txt` resume, or paste text into the textarea.
- Click `Scan Resume` to extract name (heuristic), email, phone, and common skills.
- Results are shown on the page; the scanner is intentionally lightweight and client-side.

## Notes & next steps

- PDF extraction relies on an external CDN for `pdf.js`; offline use requires bundling the library locally.
- Currently supports PDF and plain text only. Adding DOCX parsing, improved name detection, and exporting parsed JSON are straightforward improvements.

## License

This repo contains example code; adapt and reuse as needed.

# 📚 Sanfoundry Scraper (PC-Based) Pro

**"Built for Precision, Not Just Velocity."** > *It may be slow, but it's blindly reliable.*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Engine-Playwright-2EAD33?style=for-the-badge&logo=playwright)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

Most scrapers fail when they hit Sanfoundry's anti-bot layers, complex math symbols, or image-heavy explanations. This **PC-Based version** is engineered for **100% data integrity**, capturing every subscript, superscript, and technical diagram with surgical precision.

### 🛡️ The Reliability Manifest

In the world of scraping, speed often leads to broken images and missing symbols. This tool follows the philosophy of **Slow is Smooth, Smooth is Fast**:

* **Blindly Reliable:** Designed to handle ad-popups and network stutters without losing data.
* **Math-First:** Every exponent ($x^2$), subscript ($H_2O$), and expression is captured exactly as intended.
* **Context-Aware:** Images are intelligently "baked" into their specific MCQ context, not just appended to the end.

---

### 🚀 Progressive Updates (v2.8) — *The "Intelligent Router" Release*

The latest updates transform the scraper from a linear script into a context-aware intelligence tool:

* **🧠 Intelligent Link Router:** The script now automatically detects the hierarchy of the URL provided. Whether you paste a full **Subject URL**, a **Chapter Anchor link** (`#`), or a **Single Topic MCQ URL**, the scraper adapts its progression logic instantly.
* **🔗 Resilient-Slug Matching:** Fixed issues where chapter scraping returned empty results. The script now employs a "Greedy Header-to-Header" scanner that converts DOM titles into URL-friendly slugs, specifically ignoring `and` and `&` to match Sanfoundry's internal anchor generation.
* **💾 State-Persistence Engine:** Scraped data is saved to `scrape_progress.json` in real-time. If the mission is interrupted by a crash or network loss, simply restart to **pick up exactly where it failed.**
* **🛡️ Global Vignette Watcher:** Actively monitors for Google full-screen Ads (`#google_vignette`). The script pauses the progress bar and alerts the user via the HUD to clear the ad manually, ensuring zero data loss during high-intensity scraping.
* **📊 Tactical Terminal HUD:** Integrated the `Rich` library for a professional console experience, featuring **real-time progress bars** and color-coded status panels.

---

### 🔢 Key Upgrades (v2.0)

* **📦 Bulk Subject Processing:** Scrape entire subjects (100+ chapters) in a single session without memory leaks.
* **🔢 Math-Logic Engine:** Robust support for subscripts, superscripts, and complex mathematical notation.
* **🖼️ Optimal Image Placement:** Precise rendering of technical diagrams within the PDF flow using Base64 embedding.

---

### ✨ Features

* **Deep-Render Engine:** Uses Playwright to "paint" the page, ensuring lazy-loaded images are fully rendered.
* **Self-Contained PDFs:** Converts images to **Base64**—your PDFs work perfectly offline, forever.
* **Anti-Bot Bypass:** Leverages SeleniumBase UC (Undetected) mode to navigate smoothly through security layers.

---

### 🛠️ Installation & Setup

1. **Clone & Navigate**

```bash
git clone https://github.com/omsusi/sanfoundry-scraper-pc-based.git
cd sanfoundry-scraper-pc-based

```

2. **Setup Environment**

```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
pip install rich
playwright install chromium

```

---

### ⚙️ How to Use

1. **Configure:** Open the script and set your `TARGET_MAIN_URL` (accepts Subject, Chapter, or Topic links) and `SUBJECT_TITLE`.
2. **Execute:** Run `python refined.py`.
3. **Initialize:** A Chrome window will open. Clear any initial ad-popups, then press **Enter** in your terminal.
4. **Monitor:** Watch the **Tactical HUD** for progress. If a vignette ad pops up, the terminal will alert you to close it.
5. **Compile:** Once complete, Playwright renders the HTML buffer into a professional, searchable A4 PDF.

---

### 💼 Custom Scraping Services

**Need a custom scraper for another platform? I am open for professional commissions.**

I specialize in building scrapers that handle:

* High-Accuracy Math & Technical Rendering
* Complex Auth & Bot Protection
* Structured Data Export (PDF, Excel, JSON)

📫 **Let's Talk:** [LinkedIn](https://linkedin.com/in/omsubhra-singha-30447a254) | [Email](mailto:omsubhrasingha21@gmail.com)

---

### ⚖️ Legal Disclaimer & License

*Educational purposes only. Please respect the robots.txt and Terms of Service of the target website.* This project is licensed under the **MIT License**.

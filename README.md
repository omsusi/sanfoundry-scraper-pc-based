# 📚 Sanfoundry Scraper (PC-Based) Pro
**The Ultimate High-Fidelity MCQ & Image Extraction Engine**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Engine-Playwright-2EAD33?style=for-the-badge&logo=playwright)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

Most scrapers fail when they hit Sanfoundry's anti-bot layers, complex math symbols, or image-heavy explanations. This **PC-Based version** is engineered for **100% data integrity**, capturing every subscript, superscript, and technical diagram.

### 🚀 Key Upgrades (v2.0)
* **📦 Bulk Subject Processing:** Scrape entire subjects (100+ chapters) in a single session without memory leaks or link timeouts.
* **🔢 Math-Logic Engine:** Enhanced support for complex mathematical symbols, subscripts, superscripts, and LaTeX-style expressions.
* **🖼️ Optimal Image Placement:** Images are no longer just "appended"; they are intelligently placed within their respective MCQ context.
* **⚡ Automated Link Classification:** (Upcoming) Intelligent routing that adjusts scraping methodology based on the specific Sanfoundry link structure.

---

### ✨ Features
- **Deep-Render Engine:** Uses Playwright to "paint" the page, ensuring lazy-loaded images are fully rendered before PDF baking.
- **Self-Contained PDFs:** Images are converted to **Base64**—your PDFs work perfectly offline, forever.
- **Anti-Bot Bypass:** Leverages SeleniumBase UC (Undetected) mode to navigate smoothly through security layers.

---

### 🛠️ Installation & Setup

1. **Clone & Navigate**
   ```bash
   git clone [https://github.com/omsusi/sanfoundry-scraper-pc-based.git](https://github.com/omsusi/sanfoundry-scraper-pc-based.git)
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


3. **Install Core & Browser Engines**
```bash
pip install -r requirements.txt
playwright install chromium

```



---

### ⚙️ How to Use

1. **Configure:** Open `refined.py` and set your `TARGET_MAIN_URL`, `SUBJECT_TITLE`, and range (`START_CHAPTER` to `END_CHAPTER`).
2. **Execute:** Run `python refined.py`.
3. **Initialize:** A Chrome window will open. Clear any initial ad-popups/cookie consents manually, then press **Enter** in your terminal.
4. **Relax:** The script will automatically cycle through topics, click "View Answer" buttons, and compile your professional PDF.

---

### 💼 Custom Scraping Services

**Need a custom scraper for another platform? I am open for professional commissions.**

I specialize in building scrapers that handle:

* **Complex Auth & Bot Protection**
* **Image/Media Extraction**
* **Structured Data Export (PDF, Excel, JSON)**
* **High-Accuracy Math & Technical Rendering**

📫 **Let's Talk:** [LinkedIn](https://linkedin.com/in/omsubhra-singha-30447a254) | [Email](mailto:omsubhrasingha21@gmail.com)

---

### ⚖️ Legal Disclaimer & License

*Educational purposes only. Please respect the robots.txt and Terms of Service of the target website.* This project is licensed under the **MIT License**.

```

---

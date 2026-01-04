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

### 🚀 Key Upgrades (v2.0)
* **📦 Bulk Subject Processing:** Scrape entire subjects (100+ chapters) in a single session without memory leaks.
* **🔢 Math-Logic Engine:** Robust support for subscripts, superscripts, and complex mathematical notation.
* **🖼️ Optimal Image Placement:** Precise rendering of technical diagrams within the PDF flow.
* **⚡ Automated Link Classification:** (Upcoming) Intelligent routing that adjusts scraping logic based on the Sanfoundry link structure.

---

### ✨ Features
- **Deep-Render Engine:** Uses Playwright to "paint" the page, ensuring lazy-loaded images are fully rendered.
- **Self-Contained PDFs:** Converts images to **Base64**—your PDFs work perfectly offline, forever.
- **Anti-Bot Bypass:** Leverages SeleniumBase UC (Undetected) mode to navigate smoothly through security.

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


3. **Install Dependencies**
```bash
pip install -r requirements.txt
playwright install chromium

```



---

### ⚙️ How to Use

1. **Configure:** Open `refined.py` and set your `TARGET_MAIN_URL`, `SUBJECT_TITLE`, and chapter range.
2. **Execute:** Run `python refined.py`.
3. **Initialize:** A Chrome window will open. Clear any ad-popups manually, then press **Enter** in your terminal.
4. **Relax:** The script will automatically cycle through topics, click "View Answer" buttons, and compile your professional PDF.

---

### 💼 Custom Scraping Services

**Need a custom scraper for another platform? I am open for professional commissions.**

I specialize in building scrapers that handle:

* **High-Accuracy Math & Technical Rendering**
* **Complex Auth & Bot Protection**
* **Structured Data Export (PDF, Excel, JSON)**

📫 **Let's Talk:** [LinkedIn](https://linkedin.com/in/omsubhra-singha-30447a254) | [Email](mailto:omsubhrasingha21@gmail.com)

---

### ⚖️ Legal Disclaimer & License

*Educational purposes only. Please respect the robots.txt and Terms of Service of the target website.* This project is licensed under the **MIT License**.

**Would you like me to help you write a 'Troubleshooting' section for common issues like 'Playwright timeout' to make it even more professional?**

```

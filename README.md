Sanfoundry Scraper (PC-Based) 📚

A robust, high-fidelity web scraper designed to crawl Sanfoundry MCQ chapters and convert them into professionally formatted, offline-ready PDFs. This tool uses SeleniumBase to navigate anti-bot protections and Playwright to ensure math equations and diagrams are rendered perfectly before being "baked" into the final PDF.

🚀 Features

Deep-Render Engine: Uses Playwright to scroll and "paint" images before PDF generation.

Image Embedding: Automatically converts images to Base64 to ensure the PDF is self-contained (no broken links).

Anti-Bot Bypass: Uses SeleniumBase's Undetected ChromeDriver (UC) mode.

Math-Ready: Specifically handles small inline math images and large structural diagrams differently for optimal layout.

🛠️ Installation & Setup

1. Clone the Repository

git clone [https://github.com/omsusi/sanfoundry-scraper-pc-based.git](https://github.com/omsusi/sanfoundry-scraper-pc-based.git)
cd sanfoundry-scraper-pc-based


2. Create a Virtual Environment (Recommended)

Keep your global Python installation clean by using a virtual environment:

Windows:

python -m venv venv
.\venv\Scripts\activate


macOS/Linux:

python3 -m venv venv
source venv/bin/activate


3. Install Dependencies

pip install -r requirements.txt
playwright install chromium


⚙️ Configuration

Open refined.py in your text editor and modify the configuration block at the top:

TARGET_MAIN_URL: The URL of the Sanfoundry "1000 MCQs" table of contents page.

SUBJECT_TITLE: This will be the name of your generated PDF.

START_CHAPTER / END_CHAPTER: Define the range of chapters to scrape.

📖 Usage Instructions

Run the script:

python refined.py


The Ad-Closing Logic: A Chrome window will open. You must manually close any ad popups or cookie consents. Once the main page content is visible, go back to the terminal and press Enter to start the scraping process.

Wait for Scraping: The script will visit each link, click the "View Answer" buttons automatically, and gather the data.

Final Rendering: After gathering data, a second browser window (Playwright) will launch. It will automatically scroll the page to ensure all images are decoded before saving the final PDF.

⚠️ Important Warnings

🚩 Batch Size Limits

Do not attempt to scrape huge batches (e.g., 5+ chapters) in one go. Scraping very large amounts of data in a single session can lead to:

Images not fetching correctly (leaving blank spaces in the PDF).

Memory exhaustion during the PDF rendering phase.

Timeouts in the Playwright engine.
Best Practice: Scrape in batches of 10–20 chapters at a time for the highest quality results.

🚩 Browser Visibility & Ads

Do not minimize the Chrome window: If the window opened during the scraping phase is minimized or closed, ads may reappear.

Ad Interference: If an ad covers the page and isn't closed, the program may be unable to find the content and might skip that page entirely. Keep an eye on the browser window if you notice the script skipping topics.

⚖️ Legal Disclaimer

This tool is for educational and personal use only. Scraping copyrighted content may violate the Terms of Service of the target website. The developer is not responsible for any misuse of this tool. Please respect the robots.txt files and use the data responsibly.

📜 License

This project is licensed under the MIT License. See the LICENSE file for details.

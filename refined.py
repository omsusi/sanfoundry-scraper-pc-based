import os
import requests
import re
import time
import base64
from bs4 import BeautifulSoup
from seleniumbase import SB
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
TARGET_MAIN_URL = "https://www.sanfoundry.com/1000-structural-analysis-questions-answers/"
SUBJECT_TITLE = "structural-analysis-questions"
START_CHAPTER = 1 
END_CHAPTER = 99   # Set to 99 for full subject
# ---------------------

def get_image_base64(url):
    """Downloads image and returns Base64 string to bake it directly into the HTML."""
    if not url: return ""
    if url.startswith("/"): url = "https://www.sanfoundry.com" + url
    
    clean_url = url.split('?')[0].split(',')[0]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.sanfoundry.com/"
    }
    try:
        r = requests.get(clean_url, headers=headers, timeout=15)
        if r.status_code == 200:
            b64 = base64.b64encode(r.content).decode('utf-8')
            mime = r.headers.get('content-type', 'image/png')
            return f"data:{mime};base64,{b64}"
    except: pass
    return ""

def process_element(element, soup_context):
    """Refined element processor that handles classification and sizing."""
    for ns in element.find_all("noscript"):
        ns.replace_with(ns.decode_contents())

    def classify_and_embed(img_tag, source_url):
        b64 = get_image_base64(source_url)
        if not b64: return None
        
        # EXTRACT ORIGINAL DIMENSIONS
        orig_w = int(img_tag.get('width', 0) or 0)
        orig_h = int(img_tag.get('height', 0) or 0)
        
        # DECISION: Scale up if it's likely a diagram (based on dims or data weight)
        is_diagram = (orig_w > 50 or orig_h > 40 or len(b64) > 5000)
        
        new_img = soup_context.new_tag("img", src=b64)
        new_img['class'] = "diagram" if is_diagram else "math-img"
        
        if is_diagram:
            # Force a readable minimum width for line drawings like Q.12
            new_img['style'] = f"width: {max(orig_w, 350)}px;"
            
        return new_img

    # 1. Handle link-wrapped images
    for a_tag in element.find_all("a"):
        img = a_tag.find("img")
        href = a_tag.get("href", "").lower()
        if img:
            src = img.get("data-src") or img.get("src") or img.get("data-lazy-src")
            new_node = classify_and_embed(img, src)
            if new_node: a_tag.replace_with(new_node)
            else: a_tag.decompose()
        elif any(ext in href for ext in [".png", ".jpg", ".jpeg"]):
            b64 = get_image_base64(href)
            if b64:
                new_img = soup_context.new_tag("img", src=b64, **{"class": "diagram", "style": "width: 400px;"})
                a_tag.replace_with(new_img)
            else: a_tag.decompose()

    # 2. Handle standalone images
    for img in element.find_all("img"):
        if not img.get("src", "").startswith("data:"):
            src = img.get("data-src") or img.get("src") or img.get("data-lazy-src")
            new_node = classify_and_embed(img, src)
            if new_node: img.replace_with(new_node)
            else: img.decompose()

    for btn in element.find_all(class_=re.compile("collapseomatic")):
        btn.decompose()

    return element.decode_contents()

def scrape_to_html():
    all_content_html = ""
    with SB(uc=True, headless=False) as sb:
        print(f"[*] Connecting to: {TARGET_MAIN_URL}")
        sb.uc_open_with_reconnect(TARGET_MAIN_URL, 6)
        print("\n" + "!"*50 + "\nACTION: Close ads, then press ENTER.\n" + "!"*50)
        input(">>> ")

        main_soup = BeautifulSoup(sb.get_page_source(), "lxml")
        content_div = main_soup.find("div", class_="entry-content")
        chapter_nodes = content_div.find_all("h2") if content_div else []
        
        full_structure = []
        for h2 in chapter_nodes:
            title = h2.get_text(strip=True)
            if not re.match(r"^\d+\.", title): continue
            table = h2.find_next(["table", "ul"])
            if table:
                links = [(a.text, a['href']) for a in table.find_all("a") if "sanfoundry" in a.get('href', '')]
                full_structure.append({"title": title, "topics": links})

        for ch in full_structure[START_CHAPTER-1 : END_CHAPTER]:
            print(f"\n[>>>] CHAPTER: {ch['title']}")
            all_content_html += f"<div class='chapter-header'>{ch['title']}</div>"

            for t_name, t_url in ch['topics']:
                print(f"  [*] Scraping Topic: {t_name}")
                sb.uc_open_with_reconnect(t_url, 5)
                sb.execute_script('document.querySelectorAll(".collapseomatic").forEach(el => el.click())')
                time.sleep(3) 

                t_soup = BeautifulSoup(sb.get_page_source(), "lxml")
                t_content = t_soup.find("div", class_="entry-content")
                if not t_content: continue

                all_content_html += f"<h2 class='topic-header'>{t_name}</h2>"

                for el in t_content.find_all(["p", "div", "center", "table"], recursive=False):
                    text = el.get_text(strip=True)
                    if any(x in text for x in ["Enroll", "Certification", "advertisement"]): continue
                    
                    if re.match(r"^\d+\.", text):
                        all_content_html += f"<div class='question'>Q. {process_element(el, t_soup)}</div>"
                    elif "collapseomatic_content" in el.get("class", []):
                        ans_match = re.search(r"Answer:\s*([a-d])", text)
                        ans_letter = ans_match.group(1) if ans_match else "?"
                        raw_expl = el.decode_contents().split("Explanation:")[-1] if "Explanation:" in el.decode_contents() else el.decode_contents()
                        expl_container = BeautifulSoup(f"<div>{raw_expl}</div>", "lxml")
                        all_content_html += f"""
                        <div class='ans-block'>
                            <span class='ans-label'>Ans: {ans_letter}</span> | 
                            <span class='expl'><strong>Explanation:</strong> {process_element(expl_container, t_soup)}</span>
                        </div>"""
                    elif re.search(r"^[a-d]\)\s", text) or (len(text) < 100 and "a)" in text):
                        all_content_html += f"<div class='option'>{process_element(el, t_soup)}</div>"
                    else:
                        processed_snippet = process_element(el, t_soup)
                        if "<img" in processed_snippet:
                            all_content_html += f"<div class='standing-img'>{processed_snippet}</div>"
    return all_content_html

def save_to_pdf(html_body):
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ margin: 10mm; }}
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; font-size: 8.5pt; line-height: 1.15; color: #111; }}
            .chapter-header {{ background: #1a252f; color: white; padding: 8px; margin: 20px 0 10px 0; font-size: 14pt; text-align: center; font-weight: bold; border-radius: 4px; page-break-before: always; }}
            .topic-header {{ color: #a00; border-bottom: 1.5px solid #a00; margin: 12px 0 4px 0; font-size: 10.5pt; font-weight: bold; text-transform: uppercase; }}
            .question {{ font-weight: bold; display: block; margin-top: 10px; font-size: 9.2pt; color: #000; }}
            .option {{ margin-left: 20px; display: block; font-size: 9pt; color: #333; }}
            .ans-block {{ margin-top: 4px; padding: 5px 12px; background: #f6fff6; border-left: 4px solid #27ae60; font-size: 8.5pt; page-break-inside: avoid; }}
            .ans-label {{ color: #27ae60; font-weight: bold; }}
            
            /* DYNAMIC IMAGE SIZING FIXES */
            .diagram {{ 
                max-width: 95%; 
                height: auto;
                display: block; 
                margin: 12px auto; 
                border: 1px solid #ddd; 
                padding: 8px;
                background: #fff;
            }}
            .math-img {{ 
                display: inline-block; 
                height: 1.6em; 
                vertical-align: middle; 
                margin: 0 3px; 
            }}
            .standing-img {{ width: 100%; text-align: center; }}
            sub, sup {{ font-size: 70%; line-height: 0; position: relative; vertical-align: baseline; }}
            sup {{ top: -0.5em; }}
            sub {{ bottom: -0.25em; }}
        </style>
    </head>
    <body>{html_body}</body></html>
    """

    file_path = os.path.abspath("render_buffer.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_template)

    print("[*] Launching Playwright Deep-Render Engine...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file:///{file_path}", wait_until="load")

        # Scroll to force image painting
        print("[*] Forcing image decode via auto-scroll...")
        page.evaluate('''async () => {
            await new Promise((resolve) => {
                let totalHeight = 0, distance = 500;
                let timer = setInterval(() => {
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if(totalHeight >= document.body.scrollHeight){
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }''')
        
        print("[*] Generating Final PDF...")
        time.sleep(5) # Final settle
        page.pdf(path=f"{SUBJECT_TITLE}.pdf", format="A4", print_background=True)
        browser.close()
    print(f"\n[+] SUCCESS! Professional PDF created: {SUBJECT_TITLE}.pdf")

if __name__ == "__main__":
    html_data = scrape_to_html()
    save_to_pdf(html_data)
import os
import requests
import re
import time
import base64
from bs4 import BeautifulSoup
from seleniumbase import SB
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
TARGET_MAIN_URL = "https://www.sanfoundry.com/1000-basic-civil-engineering-questions-answers/"
SUBJECT_TITLE = "basic-civil-engineering-questions"
START_CHAPTER = 1 
END_CHAPTER = 99   
# ---------------------

def get_image_base64(url):
    """Downloads the actual image and returns a Base64 string."""
    if not url: return ""
    if url.startswith("/"): url = "https://www.sanfoundry.com" + url
    
    clean_url = url.split('?')[0].split(',')[0]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.sanfoundry.com/"
    }
    
    try:
        r = requests.get(clean_url, headers=headers, timeout=12)
        if r.status_code == 200:
            b64 = base64.b64encode(r.content).decode('utf-8')
            mime = r.headers.get('content-type', 'image/png')
            return f"data:{mime};base64,{b64}"
    except: pass
    return ""

def process_node(element, soup_context):
    """Uses link-presence and sizing logic to correctly scale diagrams vs math symbols."""
    # 1. Expand noscript wrappers
    for ns in element.find_all("noscript"):
        ns.replace_with(ns.decode_contents())

    # 2. Extract and Classify Images
    for img in element.find_all("img"):
        src = img.get("data-src") or img.get("data-lazy-src") or img.get("src")
        
        # LOGIC: If it has a Sanfoundry upload link, it is a DIAGRAM.
        is_external_upload = "wp-content/uploads" in src if src else False
        
        b64 = get_image_base64(src)
        if b64:
            img['src'] = b64
            # Strip alt/title to prevent text clutter
            if img.has_attr('alt'): del img['alt']
            if img.has_attr('title'): del img['title']
            
            # Apply classes based on source verification
            if is_external_upload or len(b64) > 4500:
                img['class'] = "diagram-scaled"
            else:
                img['class'] = "math-inline"
                
            # Clean junk attributes
            attrs_to_keep = ["src", "class", "style"]
            for attr in list(img.attrs):
                if attr not in attrs_to_keep: del img[attr]
        else:
            img.decompose()

    # 3. Handle images wrapped in or pointed to by <a> tags (Fixes the NameError)
    for a_tag in element.find_all("a"):
        href = a_tag.get("href", "").lower()
        if any(ext in href for ext in [".png", ".jpg"]) and "wp-content/uploads" in href:
            b64 = get_image_base64(href)
            if b64:
                new_img = soup_context.new_tag("img", src=b64)
                new_img['class'] = "diagram-scaled"
                a_tag.replace_with(new_img)
            else:
                # Keep text if download fails, otherwise unwrap
                a_tag.unwrap() if a_tag.string else a_tag.decompose()
        else:
            a_tag.unwrap() # Ensure links don't interfere with rendering

    # 4. Remove UI Clutter
    for btn in element.find_all(class_=re.compile("collapseomatic")):
        btn.decompose()

    return element.decode_contents()

def scrape_to_html():
    all_content_html = ""
    with SB(uc=True, headless=False) as sb:
        print(f"[*] Connecting to Sanfoundry...")
        sb.uc_open_with_reconnect(TARGET_MAIN_URL, 6)
        print("\nACTION: Close ads, then press ENTER.")
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
                links = [(a.text, a['href']) for a in table.find_all("a") if "sanfoundry.com" in a.get('href', '')]
                full_structure.append({"title": title, "topics": links})

        for ch in full_structure[START_CHAPTER-1 : END_CHAPTER]:
            all_content_html += f"<div class='chapter-header'>{ch['title']}</div>"
            for t_name, t_url in ch['topics']:
                print(f"  [*] Scraping: {t_name}")
                sb.uc_open_with_reconnect(t_url, 5)
                # Forced scroll to trigger lazy-load on original site
                sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
                sb.execute_script('document.querySelectorAll(".collapseomatic").forEach(el => el.click())')
                time.sleep(2) 

                t_soup = BeautifulSoup(sb.get_page_source(), "lxml")
                t_content = t_soup.find("div", class_="entry-content")
                if not t_content: continue
                all_content_html += f"<h2 class='topic-header'>{t_name}</h2>"

                for el in t_content.find_all(["p", "div", "center", "table"], recursive=False):
                    text = el.get_text(strip=True)
                    if any(x in text for x in ["Enroll", "Certification", "advertisement"]): continue
                    
                    if re.match(r"^\d+\.", text):
                        all_content_html += f"<div class='question'>Q. {process_node(el, t_soup)}</div>"
                    elif "collapseomatic_content" in el.get("class", []):
                        ans_match = re.search(r"Answer:\s*([a-d])", text)
                        ans_letter = ans_match.group(1) if ans_match else "?"
                        raw_expl = el.decode_contents().split("Explanation:")[-1]
                        expl_div = BeautifulSoup(f"<div>{raw_expl}</div>", "lxml")
                        all_content_html += f"""
                        <div class='ans-block'>
                            <span class='ans-label'>Ans: {ans_letter}</span> | 
                            <span class='expl'>{process_node(expl_div, t_soup)}</span>
                        </div>"""
                    elif re.search(r"^[a-d]\)\s", text) or (len(text) < 100 and "a)" in text):
                        all_content_html += f"<div class='option'>{process_node(el, t_soup)}</div>"
                    else:
                        snippet = process_node(el, t_soup)
                        if "<img" in snippet:
                            all_content_html += f"<div class='standing-img'>{snippet}</div>"
    return all_content_html

def save_to_pdf(html_body):
    html_template = f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><style>
        @page {{ margin: 10mm; }}
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; font-size: 8.5pt; line-height: 1.15; color: #111; }}
        .chapter-header {{ background: #1a252f; color: white; padding: 8px; margin: 15px 0 10px 0; font-size: 13pt; text-align: center; font-weight: bold; border-radius: 4px; page-break-before: always; }}
        .topic-header {{ color: #a00; border-bottom: 1.5px solid #a00; margin: 12px 0 4px 0; font-size: 10pt; font-weight: bold; text-transform: uppercase; }}
        .question {{ font-weight: bold; display: block; margin-top: 10px; font-size: 9.2pt; }}
        .option {{ margin-left: 20px; display: block; font-size: 8.8pt; color: #333; }}
        .ans-block {{ margin-top: 4px; padding: 5px 12px; background: #f6fff6; border-left: 4px solid #27ae60; font-size: 8.5pt; page-break-inside: avoid; }}
        .ans-label {{ color: #27ae60; font-weight: bold; }}
        
        /* IMAGE SIZING FIXES */
        .diagram-scaled {{ 
            max-width: 90%; 
            min-width: 420px; /* Forces line drawings to be large enough */
            min-height: 150px; /* Prevents flattening of wide diagrams */
            height: auto; 
            display: block; 
            margin: 12px auto; 
            border: 1px solid #eee; 
            padding: 10px;
            background: #fff;
        }}
        .math-inline {{ 
            display: inline-block; 
            height: 1.6em; 
            vertical-align: middle; 
            margin: 0 2px; 
        }}
        .standing-img {{ width: 100%; text-align: center; }}
        sub, sup {{ font-size: 70%; line-height: 0; position: relative; vertical-align: baseline; }}
        sup {{ top: -0.5em; }} sub {{ bottom: -0.25em; }}
    </style></head><body>{html_body}</body></html>
    """
    file_path = os.path.abspath("render_buffer.html")
    with open(file_path, "w", encoding="utf-8") as f: f.write(html_template)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file:///{file_path}", wait_until="load")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(6)
        page.pdf(path=f"{SUBJECT_TITLE}.pdf", format="A4", print_background=True)
        browser.close()
    print(f"\n[+] SUCCESS! Professional PDF created: {SUBJECT_TITLE}.pdf")

if __name__ == "__main__":
    html_data = scrape_to_html()
    save_to_pdf(html_data)

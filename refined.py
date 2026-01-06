import os
import requests
import re
import time
import base64
import json
from bs4 import BeautifulSoup
from seleniumbase import SB
from playwright.sync_api import sync_playwright
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.panel import Panel

# --- CONFIGURATION ---
# Works with Subject, Chapter (#), or Topic links
TARGET_MAIN_URL = "[YOUR SANFOUNDRY URL]"
SUBJECT_TITLE = "[YOUR PDF NAME]"
START_CHAPTER = 1 
END_CHAPTER = 99 
PROGRESS_FILE = "scrape_progress.json"
# ---------------------

console = Console()

def create_slug(text):
    text = text.lower()
    text = re.sub(r'\band\b|&', '', text)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text).strip('-')

def classify_link(url):
    if "#" in url: return "CHAPTER"
    if re.search(r"/(1000-)?.*-questions-answers/?$", url): return "SUBJECT"
    return "TOPIC"

def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"completed_topics": [], "html_buffer": "", "failed_chapters": []}

def check_for_vignette(sb):
    is_ad_url = "#google_vignette" in sb.get_current_url()
    ad_elements = ["ins.adsbygoogle", "div#google_ads_iframe", "div.google-vignette-container"]
    is_ad_dom = any(sb.is_element_visible(selector) for selector in ad_elements)
    if is_ad_url or is_ad_dom:
        console.print(Panel("[bold red]🛑 AD BLOCK DETECTED (Google Vignette)[/bold red]\nClear ad manually in browser, then press ENTER.", border_style="red"))
        input(">>> ")
        return True
    return False

def get_image_base64(url):
    if not url: return ""
    if url.startswith("/"): url = "https://www.sanfoundry.com" + url
    try:
        r = requests.get(url.split('?')[0], headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            return f"data:{r.headers.get('content-type', 'image/png')};base64,{base64.b64encode(r.content).decode('utf-8')}"
    except: pass
    return ""

def process_node(element, soup_context):
    for ns in element.find_all("noscript"): ns.replace_with(ns.decode_contents())
    for img in element.find_all("img"):
        src = img.get("data-src") or img.get("data-lazy-src") or img.get("src")
        b64 = get_image_base64(src)
        if b64:
            img['src'] = b64
            img['class'] = "diagram-scaled" if (len(b64) > 4500) else "math-inline"
            for attr in list(img.attrs):
                if attr not in ["src", "class", "style"]: del img[attr]
        else: img.decompose()
    for a in element.find_all("a"): a.unwrap()
    for btn in element.find_all(class_=re.compile("collapseomatic")): btn.decompose()
    return element.decode_contents()

def scrape_page_content(sb, t_name, t_url):
    sb.uc_open_with_reconnect(t_url, 7)
    check_for_vignette(sb)
    sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2) # Tactical delay for diagram rendering
    sb.execute_script('document.querySelectorAll(".collapseomatic").forEach(el => el.click())')
    time.sleep(1.5)
    t_soup = BeautifulSoup(sb.get_page_source(), "lxml")
    t_content = t_soup.find("div", class_="entry-content")
    html_out = ""
    if t_content:
        html_out += f"<h2 class='topic-header'>{t_name}</h2>"
        for el in t_content.find_all(["p", "div", "center", "table"], recursive=False):
            text = el.get_text(strip=True)
            if any(x in text for x in ["Enroll", "Certification", "advertisement"]): continue
            if re.match(r"^\d+\.", text):
                html_out += f"<div class='question'>Q. {process_node(el, t_soup)}</div>"
            elif "collapseomatic_content" in el.get("class", []):
                ans_match = re.search(r"Answer:\s*([a-d])", text)
                raw_expl = el.decode_contents().split("Explanation:")[-1]
                html_out += f"<div class='ans-block'><b>Ans: {ans_match.group(1) if ans_match else '?'}</b> | {process_node(BeautifulSoup(raw_expl, 'lxml'), t_soup)}</div>"
            elif re.search(r"^[a-d]\)\s", text) or (len(text) < 100 and "a)" in text):
                html_out += f"<div class='option'>{process_node(el, t_soup)}</div>"
    return html_out

def scrape_to_html():
    state = load_progress()
    all_content_html = state["html_buffer"]
    link_type = classify_link(TARGET_MAIN_URL)
    
    with SB(uc=True, headless=False) as sb:
        console.print(Panel(f"[bold cyan]Mode: {link_type}[/bold cyan]\n[dim]{TARGET_MAIN_URL}[/dim]"))
        
        base_url = TARGET_MAIN_URL.split("#")[0]
        sb.uc_open_with_reconnect(base_url, 6)
        check_for_vignette(sb)
        soup = BeautifulSoup(sb.get_page_source(), "lxml")
        content_div = soup.find("div", class_="entry-content")
        
        topic_links = []
        chapter_display_title = "Sanfoundry Intel Export"

        if link_type == "CHAPTER":
            target_frag = TARGET_MAIN_URL.split("#")[-1].lower()
            headers = content_div.find_all("h2")
            start_header = None

            for h2 in headers:
                clean_title = re.sub(r'^\d+\.\s*', '', h2.get_text(strip=True))
                h2_id = h2.get('id') or (h2.find('span') and h2.find('span').get('id'))
                if (h2_id and h2_id.lower() == target_frag) or (create_slug(clean_title) == target_frag):
                    start_header = h2
                    chapter_display_title = h2.get_text(strip=True)
                    break
            
            if start_header:
                # GREEDY SCAN: Capture all tables/lists until the next H2 header
                curr = start_header.find_next()
                while curr and curr.name != "h2":
                    if curr.name in ["table", "ul", "ol"]:
                        for a in curr.find_all("a", href=True):
                            if "sanfoundry.com" in a['href'] and a.text.strip():
                                topic_links.append((a.text.strip(), a['href']))
                    curr = curr.find_next()
        
        elif link_type == "SUBJECT":
            # Normal Subject full range logic
            all_headers = content_div.find_all("h2")
            for h2 in all_headers[START_CHAPTER-1 : END_CHAPTER]:
                chapter_display_title = "Bulk Subject Export"
                curr = h2.find_next()
                while curr and curr.name != "h2":
                    if curr.name in ["table", "ul", "ol"]:
                        for a in curr.find_all("a", href=True):
                            if "sanfoundry.com" in a['href'] and a.text.strip():
                                topic_links.append((a.text.strip(), a['href']))
                    curr = curr.find_next()
        else:
            topic_links = [("Single Topic", TARGET_MAIN_URL)]

        if not topic_links:
            console.print("[bold red]❌ Critical: No topics identified.[/bold red]")
            return ""

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), 
                      BarColumn(bar_width=40), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                      TimeElapsedColumn(), console=console) as progress:
            
            main_task = progress.add_task("[green]Harvesting Topics", total=len(topic_links))
            all_content_html += f"<div class='chapter-header'>{chapter_display_title}</div>"

            for t_name, t_url in topic_links:
                if t_url in state["completed_topics"]: 
                    progress.advance(main_task)
                    continue
                try:
                    progress.console.print(f"  [blue]▶ Processing:[/blue] {t_name}")
                    content = scrape_page_content(sb, t_name, t_url)
                    if content:
                        all_content_html += content
                        state["completed_topics"].append(t_url)
                        state["html_buffer"] = all_content_html
                        save_progress(state)
                except Exception as e:
                    progress.console.print(f"    [red]⚠️ Error: {e}[/red]")
                progress.advance(main_task)

    return all_content_html

def save_to_pdf(html_body):
    if not html_body: return
    html_template = f"<html><head><meta charset='UTF-8'><style>@page {{ margin: 10mm; }} body {{ font-family: sans-serif; font-size: 8.5pt; line-height: 1.15; }} .chapter-header {{ background: #1a252f; color: white; padding: 8px; margin: 15px 0; text-align: center; font-weight: bold; page-break-before: always; }} .topic-header {{ color: #a00; border-bottom: 1.5px solid #a00; font-size: 10pt; font-weight: bold; margin-top: 20px; }} .question {{ font-weight: bold; margin-top: 10px; }} .ans-block {{ background: #f6fff6; border-left: 4px solid #27ae60; padding: 10px; margin-top: 5px; page-break-inside: avoid; }} .diagram-scaled {{ max-width: 95%; min-width: 450px; display: block; margin: 15px auto; border: 1px solid #eee; padding: 5px; }} .math-inline {{ display: inline-block; height: 1.6em; vertical-align: middle; }}</style></head><body>{html_body}</body></html>"
    file_path = os.path.abspath("render_buffer.html")
    with open(file_path, "w", encoding="utf-8") as f: f.write(html_template)
    with sync_playwright() as p:
        browser = p.chromium.launch(); page = browser.new_page()
        page.goto(f"file:///{file_path}", wait_until="load")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(5); page.pdf(path=f"{SUBJECT_TITLE}.pdf", format="A4", print_background=True)
        browser.close()
    console.print(f"\n[bold green]✔ MISSION SUCCESS![/bold green] PDF created: {SUBJECT_TITLE}.pdf")
    if os.path.exists(PROGRESS_FILE): os.remove(PROGRESS_FILE)

if __name__ == "__main__":
    try:
        html_data = scrape_to_html()
        save_to_pdf(html_data)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]STOPPED.[/bold yellow]")

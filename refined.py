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
TARGET_MAIN_URL = "https://www.sanfoundry.com/1000-construction-building-materials-questions-answers/"
SUBJECT_TITLE = "construction-building-materials-questions"
START_CHAPTER = 1 
END_CHAPTER = 99 
PROGRESS_FILE = "scrape_progress.json"
# ---------------------

console = Console()

def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"completed_topics": [], "html_buffer": "", "failed_chapters": []}

def check_for_vignette(sb):
    """
    Checks if a Google Vignette (full-screen ad) is blocking the view.
    """
    is_ad_url = "#google_vignette" in sb.get_current_url()
    # Also check for the common ad overlay containers
    ad_elements = ["ins.adsbygoogle", "div#google_ads_iframe", "div.google-vignette-container"]
    
    is_ad_dom = any(sb.is_element_visible(selector) for selector in ad_elements)

    if is_ad_url or is_ad_dom:
        console.print(Panel(
            "[bold red]🛑 AD BLOCK DETECTED (Google Vignette)[/bold red]\n"
            "The scraper is being blocked by a full-screen ad.\n"
            "1. Switch to the browser window.\n"
            "2. [bold yellow]Close the ad manually[/bold yellow].\n"
            "3. Return here and press [bold green]ENTER[/bold green].",
            border_style="red"
        ))
        input(">>> PRESS ENTER TO RESUME...")
        return True
    return False

def get_image_base64(url):
    if not url: return ""
    if url.startswith("/"): url = "https://www.sanfoundry.com" + url
    clean_url = url.split('?')[0].split(',')[0]
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.sanfoundry.com/"}
    try:
        r = requests.get(clean_url, headers=headers, timeout=10)
        if r.status_code == 200:
            b64 = base64.b64encode(r.content).decode('utf-8')
            mime = r.headers.get('content-type', 'image/png')
            return f"data:{mime};base64,{b64}"
    except: pass
    return ""

def process_node(element, soup_context):
    for ns in element.find_all("noscript"):
        ns.replace_with(ns.decode_contents())
    for img in element.find_all("img"):
        src = img.get("data-src") or img.get("data-lazy-src") or img.get("src")
        is_external_upload = "wp-content/uploads" in src if src else False
        b64 = get_image_base64(src)
        if b64:
            img['src'] = b64
            if img.has_attr('alt'): del img['alt']
            if img.has_attr('title'): del img['title']
            img['class'] = "diagram-scaled" if (is_external_upload or len(b64) > 4500) else "math-inline"
            attrs_to_keep = ["src", "class", "style"]
            for attr in list(img.attrs):
                if attr not in attrs_to_keep: del img[attr]
        else:
            img.decompose()
    for a_tag in element.find_all("a"):
        href = a_tag.get("href", "").lower()
        if any(ext in href for ext in [".png", ".jpg"]) and "wp-content/uploads" in href:
            b64 = get_image_base64(href)
            if b64:
                new_img = soup_context.new_tag("img", src=b64)
                new_img['class'] = "diagram-scaled"
                a_tag.replace_with(new_img)
            else:
                a_tag.unwrap() if a_tag.string else a_tag.decompose()
        else:
            a_tag.unwrap()
    for btn in element.find_all(class_=re.compile("collapseomatic")):
        btn.decompose()
    return element.decode_contents()

def scrape_to_html():
    state = load_progress()
    all_content_html = state["html_buffer"]
    
    with SB(uc=True, headless=False) as sb:
        console.print(Panel(f"[bold cyan]Connecting to Sanfoundry...[/bold cyan]\n[dim]{TARGET_MAIN_URL}[/dim]"))
        sb.uc_open_with_reconnect(TARGET_MAIN_URL, 6)
        
        # Check initial vignette on home page
        check_for_vignette(sb)
        
        console.print("[bold yellow]ACTION:[/bold yellow] Press [bold green]ENTER[/bold green] to begin the sequence.")
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

        target_chapters = full_structure[START_CHAPTER-1 : END_CHAPTER]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            ch_task = progress.add_task("[green]Total Progress", total=len(target_chapters))

            for ch in target_chapters:
                ch_topics_urls = [t[1] for t in ch['topics']]
                if all(url in state["completed_topics"] for url in ch_topics_urls):
                    progress.advance(ch_task)
                    continue

                all_content_html += f"<div class='chapter-header'>{ch['title']}</div>"
                
                for t_name, t_url in ch['topics']:
                    if t_url in state["completed_topics"]: continue

                    retries = 3
                    success = False
                    while retries > 0 and not success:
                        try:
                            progress.console.print(f"  [blue]▶ Scraping:[/blue] {t_name}")
                            sb.uc_open_with_reconnect(t_url, 7)
                            
                            # INTERRUPT LOGIC: Check for ad before processing content
                            if check_for_vignette(sb):
                                # Re-open the URL if we had to click out of a vignette to ensure clean state
                                sb.uc_open_with_reconnect(t_url, 4)

                            sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(2)
                            sb.execute_script('document.querySelectorAll(".collapseomatic").forEach(el => el.click())')
                            time.sleep(2) 

                            t_soup = BeautifulSoup(sb.get_page_source(), "lxml")
                            t_content = t_soup.find("div", class_="entry-content")
                            
                            if t_content:
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
                                
                                success = True
                                state["completed_topics"].append(t_url)
                        except Exception as e:
                            retries -= 1
                            progress.console.print(f"    [red]⚠️ Error on {t_name}: {e}.[/red]")
                            time.sleep(4)

                    if not success:
                        state["failed_chapters"].append(f"{ch['title']} -> {t_name}")

                    state["html_buffer"] = all_content_html
                    save_progress(state)

                progress.advance(ch_task)

    if state["failed_chapters"]:
        console.print(Panel("\n".join(state["failed_chapters"]), title="[bold red]Failed Intel Locations[/bold red]", border_style="red"))
    
    return all_content_html

def save_to_pdf(html_body):
    if not html_body:
        console.print("[bold red]No data collected![/bold red]")
        return

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
        .diagram-scaled {{ max-width: 90%; min-width: 420px; min-height: 150px; height: auto; display: block; margin: 12px auto; border: 1px solid #eee; padding: 10px; background: #fff; }}
        .math-inline {{ display: inline-block; height: 1.6em; vertical-align: middle; margin: 0 2px; }}
        .standing-img {{ width: 100%; text-align: center; }}
    </style></head><body>{html_body}</body></html>
    """
    file_path = os.path.abspath("render_buffer.html")
    with open(file_path, "w", encoding="utf-8") as f: f.write(html_template)
    
    with console.status("[bold green]Rendering PDF...[/bold green]"):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file:///{file_path}", wait_until="load")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(5)
            page.pdf(path=f"{SUBJECT_TITLE}.pdf", format="A4", print_background=True)
            browser.close()
    
    console.print(f"\n[bold green]✔ MISSION SUCCESS![/bold green] PDF created: [white underline]{SUBJECT_TITLE}.pdf[/white underline]")
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)

if __name__ == "__main__":
    try:
        html_data = scrape_to_html()
        save_to_pdf(html_data)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]STOPPED BY USER.[/bold yellow] Run again to resume.")

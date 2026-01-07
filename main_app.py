import os, sys, threading, subprocess, shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox

# --- EXE RESOURCE HANDLING & STABILITY ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Resolve path once and ensure it's in sys.path BEFORE importing
_REFINED_PATH = resource_path(".")
if _REFINED_PATH not in sys.path:
    sys.path.append(_REFINED_PATH)

# Import engine logic after path stability is verified
try:
    from refined import run_scrape_logic, save_to_pdf, classify_link
except ImportError:
    print("[!] Critical Import Error: refined.py not found in bundle.")

def bootstrap():
    """Sets environment to use a local, bundled browser folder next to the EXE."""
    if getattr(sys, 'frozen', False):
        root_dir = os.path.dirname(sys.executable)
    else:
        root_dir = os.path.dirname(os.path.abspath(__file__))
    
    bundled_browser_path = os.path.join(root_dir, "browsers")
    
    # Force Playwright to ONLY use the local 'browsers' folder
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = bundled_browser_path
    
    if not os.path.exists(bundled_browser_path):
        messagebox.showwarning("RESOURCE ALERT", 
            "Local 'browsers' folder not found. The app may attempt to download binaries if internet is available.")

class LegionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LEGION COMMAND: Ephemeral Intel Fetcher")
        self.geometry("800x750")
        
        # Flow Control Events
        self.resume_event = threading.Event()
        self.stop_event = threading.Event() 
        
        # Internal State
        self.active_thread = None
        self.temp_pdf_path = None

        # --- UI LAYOUT ---
        self.header = ctk.CTkLabel(self, text="INTEL_HARVEST_UNIT", font=("Impact", 32), text_color="#d4ff00")
        self.header.pack(pady=(25, 15))

        self.url_input = ctk.CTkEntry(self, width=700, placeholder_text="Mission Target (URL)...", height=45)
        self.url_input.pack(pady=10)

        # Control Panel
        self.ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.ctrl_frame.pack(pady=10)

        self.deploy_btn = ctk.CTkButton(self.ctrl_frame, text="DEPLOY", command=self.start_mission, 
                                        fg_color="#d4ff00", text_color="black", font=("Arial", 14, "bold"), width=150, height=40)
        self.deploy_btn.grid(row=0, column=0, padx=15)

        self.terminate_btn = ctk.CTkButton(self.ctrl_frame, text="TERMINATE", command=self.emergency_stop, 
                                           fg_color="#ff4444", text_color="white", width=150, height=40)
        self.terminate_btn.grid(row=0, column=1, padx=15)

        self.resume_btn = ctk.CTkButton(self, text="⚠️ RESUME MISSION (Ad Cleared)", command=self.resume, fg_color="orange", text_color="black", height=35)
        self.resume_btn.pack_forget()

        self.log_box = ctk.CTkTextbox(self, width=750, height=320, font=("Consolas", 12))
        self.log_box.pack(pady=20)

        # Tactical Options
        self.opt_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=12)
        self.opt_frame.pack(fill="x", padx=35, pady=10)

        self.stealth_var = ctk.BooleanVar(value=False)
        self.stealth_cb = ctk.CTkCheckBox(self.opt_frame, text="Stealth Mode (Hidden Browser)", variable=self.stealth_var, text_color="#36BCF7")
        self.stealth_cb.pack(side="left", padx=25, pady=20)

        self.auto_open_var = ctk.BooleanVar(value=True)
        self.auto_open_cb = ctk.CTkCheckBox(self.opt_frame, text="Auto-Open on Save", variable=self.auto_open_var)
        self.auto_open_cb.pack(side="left", padx=25)

        self.clear_btn = ctk.CTkButton(self.opt_frame, text="WIPE_LOGS", command=lambda: self.log_box.delete("1.0", "end"), width=120)
        self.clear_btn.pack(side="right", padx=25)

    def update_log(self, msg):
        self.log_box.insert("end", f"{msg}\n")
        self.log_box.see("end")

    def show_ad_alert(self):
        self.update_log("[!!!] AD BLOCK DETECTED. Intervene in browser.")
        self.resume_btn.pack(pady=10)
        self.bell()

    def resume(self):
        self.resume_btn.pack_forget()
        self.resume_event.set()

    def emergency_stop(self):
        """ Graceful shutdown prevents _MEI folder locks """
        if messagebox.askyesno("TERMINATE", "Abort mission and exit application?"):
            self.stop_event.set()
            self.resume_event.set() # Unblock if waiting
            self.cleanup_temp()
            self.after(500, self.safe_exit)

    def safe_exit(self):
        self.quit()
        self.destroy()

    def start_mission(self):
        url = self.url_input.get()
        if not url: return
        self.deploy_btn.configure(state="disabled")
        self.resume_event.clear()
        self.stop_event.clear()
        threading.Thread(target=self.mission_wrapper, args=(url,), daemon=True).start()

    def mission_wrapper(self, url):
        try:
            import refined
            refined.TARGET_MAIN_URL = url
            refined.SUBJECT_TITLE = "session_buffer"
            is_stealth = self.stealth_var.get()
            
            self.update_log(f"[*] Initializing Session | Mode: {classify_link(url)}")
            html = run_scrape_logic(self, headless=is_stealth)
            
            if self.stop_event.is_set():
                self.update_log("[!] Mission terminated by user.")
                return

            if html:
                self.update_log("[*] Finalizing Mission Data...")
                save_to_pdf(html)
                self.temp_pdf_path = os.path.abspath("session_buffer.pdf")
                self.after(0, self.prompt_save)
            else:
                self.update_log("[!] Mission aborted: Harvest empty.")
        except Exception as e:
            self.update_log(f"[!] CRITICAL_ERROR: {str(e)}")
        finally:
            self.deploy_btn.configure(state="normal")

    def prompt_save(self):
        if messagebox.askyesno("MISSION COMPLETE", "Intel harvested. Download PDF?"):
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if save_path:
                try:
                    shutil.move(self.temp_pdf_path, save_path)
                    self.update_log(f"[+] INTEL STORED: {save_path}")
                    if self.auto_open_var.get(): os.startfile(save_path)
                except Exception as e:
                    self.update_log(f"[!] Save Failed: {str(e)}")
            else: self.cleanup_temp()
        else: self.cleanup_temp()

    def cleanup_temp(self):
        if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
            try: os.remove(self.temp_pdf_path)
            except: pass

if __name__ == "__main__":
    bootstrap()
    LegionApp().mainloop()
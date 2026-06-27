#!/usr/bin/env python3
import time
import random
import gc
from playwright.sync_api import sync_playwright

# --- CONFIGURATION (UPDATED TO 100 CLICKS) ---
TARGET_URL = "https://yott.netlify.app/"
CLICK_COUNT = 100        # Changed to 100 clicks per execution run
MIN_WAIT = 2             
MAX_WAIT = 5             
HEADLESS_MODE = True    # Kept True for seamless execution on GitHub Actions
# ---------------------------------------------

def run_automation():
    print(f"[*] Starting browser automation targeting: {TARGET_URL}")
    print(f"[*] Total target interactions for this job: {CLICK_COUNT}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS_MODE,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            accept_downloads=True
        )
        
        page = context.new_page()
        
        # --- MULTI-TAB & AD POPUP HANDLER ---
        def handle_popup(popup_page):
            print("    [+] Ad Popup / New Tab detected! Waiting for load...")
            try:
                popup_page.wait_for_load_state("domcontentloaded", timeout=5000)
                time.sleep(2)  
                print("    [+] Closing Ad window.")
                popup_page.close()
            except Exception as popup_err:
                print(f"    [!] Popup handling timed out or failed: {popup_err}")
                try:
                    popup_page.close()  
                except:
                    pass

        context.on("page", handle_popup)
        # ------------------------------------------

        try:
            print(f"[*] Navigating to targets...")
            page.goto(TARGET_URL, wait_until="networkidle")
            time.sleep(4) 
            
            print(f"[*] Simulating {CLICK_COUNT} button/ad target clicks...")
            
            for i in range(1, CLICK_COUNT + 1):
                selector = "button, a, [role='button'], .play-btn, .btn, div[onclick]"
                buttons = page.locator(selector).all()
                visible_buttons = [b for b in buttons if b.is_visible()]
                
                if not visible_buttons:
                    print("[-] No valid visible targets left to click.")
                    break
                
                target_button = random.choice(visible_buttons)
                
                try:
                    target_button.scroll_into_view_if_needed()
                    print(f"    [Click {i}/{CLICK_COUNT}] Pressing element...")
                    target_button.click(timeout=3000, force=True)
                except Exception:
                    continue
                
                # Dynamic human-like pace
                sleep_duration = random.uniform(MIN_WAIT, MAX_WAIT)
                time.sleep(sleep_duration)

                # Periodic cleanup to protect the cloud runner's memory over 100 cycles
                if i % 20 == 0:
                    gc.collect()
                
        except Exception as e:
            print(f"[-] Runtime interrupted: {e}")
            
        finally:
            print("[*] Tearing down browser instances.")
            context.close()
            browser.close()
            print("[*] Complete.")

if __name__ == "__main__":
    run_automation()

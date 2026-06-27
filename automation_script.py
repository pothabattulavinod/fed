#!/usr/bin/env python3
import time
import random
from playwright.sync_api import sync_playwright

# --- CONFIGURATION (OPTIMIZED FOR GITHUB ACTIONS) ---
TARGET_URL = "https://yott.netlify.app/"
CLICK_COUNT = 15         
MIN_WAIT = 2             
MAX_WAIT = 5             
HEADLESS_MODE = True    # MUST BE TRUE FOR GITHUB ACTIONS RUNNERS
# ---------------------------------------------------

def run_automation():
    print(f"[*] Starting browser automation targeting: {TARGET_URL}")
    
    with sync_playwright() as p:
        # Launching with specific arguments required for container/headless stability
        browser = p.chromium.launch(
            headless=HEADLESS_MODE,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage" # Prevents memory exhaustion crashes in Linux runners
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
                
                sleep_duration = random.uniform(MIN_WAIT, MAX_WAIT)
                time.sleep(sleep_duration)
                
        except Exception as e:
            print(f"[-] Runtime interrupted: {e}")
            
        finally:
            print("[*] Tearing down browser instances.")
            context.close()
            browser.close()
            print("[*] Complete.")

if __name__ == "__main__":
    run_automation()

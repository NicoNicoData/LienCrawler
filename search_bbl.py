import sys
import time
from playwright.sync_api import sync_playwright

BOROUGH_MAP = {
    "MANHATTAN": "1", "NEW YORK": "1", "MANHATTAN / NEW YORK": "1",
    "BRONX": "2",
    "BROOKLYN": "3", "KINGS": "3", "BROOKLYN / KINGS": "3",
    "QUEENS": "4",
    "STATEN ISLAND": "5", "RICHMOND": "5", "STATEN ISLAND / RICHMOND": "5"
}

def run(playwright, borough, block, lot):
    browser = playwright.chromium.launch(headless=False)
    # Using a typical user agent can help avoid arbitrary blocking
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    page.goto("https://a836-acris.nyc.gov/DS/DocumentSearch/BBL", wait_until="networkidle")
    
    # Resolve borough argument to the correct option value (1-5)
    borough_upper = borough.upper().strip()
    borough_val = BOROUGH_MAP.get(borough_upper)
    
    if not borough_val:
        # If it's a prefix match like "QUEEN"
        for key, val in BOROUGH_MAP.items():
            if key.startswith(borough_upper):
                borough_val = val
                break
                
    if not borough_val:
        print(f"Error: Could not resolve borough '{borough}' to a valid option.")
        sys.exit(1)
        
    page.wait_for_selector("select[name='borough']")
    
    # Select borough
    page.locator("select[name='borough']").select_option(value=borough_val)
    
    # Fill block
    page.locator("input[name='edt_block']").fill(str(block))
    
    # Fill lot
    page.locator("input[name='edt_lot']").fill(str(lot))
    
    # Click search button
    time.sleep(0.5)
    page.locator("input[name='Submit2']").click()
    
    # Wait for result page
    page.wait_for_url("**/DocumentSearch/BBLResult**", timeout=60000)
    
    print("Page loaded successfully!")
    context.close()
    browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python search_bbl.py <borough> <block> <lot>")
        sys.exit(1)
        
    borough = sys.argv[1]
    block = sys.argv[2]
    lot = sys.argv[3]
    
    with sync_playwright() as playwright:
        run(playwright, borough, block, lot)

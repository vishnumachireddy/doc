import os
from playwright.sync_api import sync_playwright

def capture():
    print("="*60)
    print("      RESUMEIQ WEB APP UI SCREENSHOT CAPTURE PROCESS")
    print("="*60)
    
    os.makedirs("uploads", exist_ok=True)
    
    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        # Create a clean browser page at standard 1280x800 desktop aspect ratio
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        
        # 1. Capture Login Screen
        print("[+] Step 1: Navigating to Auth Screen...")
        page.goto("http://localhost:5173")
        page.wait_for_timeout(3000)
        page.screenshot(path="uploads/screenshot_1_auth.png")
        print("    [OK] Saved: uploads/screenshot_1_auth.png")

        # 2. Perform Login
        print("[+] Step 2: Inputting credentials and logging in...")
        page.fill("input[type='email']", "demo@gmail.com")
        page.fill("input[type='password']", "password123")
        page.click("button[type='submit']")
        
        # Wait for Dashboard to mount
        page.wait_for_selector("text=Dashboard Overview", timeout=10000)
        page.wait_for_timeout(3000)  # Wait for charts animation to settle
        page.screenshot(path="uploads/screenshot_2_dashboard.png")
        print("    [OK] Saved: uploads/screenshot_2_dashboard.png")

        # 3. Open ATS Analysis
        print("[+] Step 3: Opening parsed Resume Intelligence Analysis...")
        page.click("button[title='View ATS & AI Analysis']")
        page.wait_for_selector("text=Resume Intelligence", timeout=10000)
        page.wait_for_timeout(3000)
        page.screenshot(path="uploads/screenshot_3_analysis_profile.png")
        print("    [OK] Saved: uploads/screenshot_3_analysis_profile.png")

        # Click ATS tab
        print("[+] Step 4: Loading ATS Improvement tab...")
        page.click("text=ATS Improvements")
        page.wait_for_timeout(1500)
        page.screenshot(path="uploads/screenshot_4_analysis_ats.png")
        print("    [OK] Saved: uploads/screenshot_4_analysis_ats.png")

        # Click Authorship tab
        print("[+] Step 5: Loading AI Authorship evaluation report...")
        page.click("text=Authorship Report")
        page.wait_for_timeout(1500)
        page.screenshot(path="uploads/screenshot_5_analysis_ai.png")
        print("    [OK] Saved: uploads/screenshot_5_analysis_ai.png")

        # Return to Dashboard
        page.click("button:has(svg.lucide-arrow-left)")
        page.wait_for_selector("text=Dashboard Overview", timeout=10000)
        
        # 4. Open Job Matcher
        print("[+] Step 6: Loading Semantic Job Description Matcher...")
        page.click("button[title='Match Job Description']")
        page.wait_for_selector("text=Semantic Job Matching", timeout=10000)
        page.wait_for_timeout(2000)
        page.screenshot(path="uploads/screenshot_6_jobmatcher_blank.png")
        print("    [OK] Saved: uploads/screenshot_6_jobmatcher_blank.png")
        
        # Fill JD and evaluate
        print("[+] Step 7: Submitting target Job Description requirements...")
        page.fill("textarea", "Looking for a Python Developer. Must have experience with FastAPI, PostgreSQL, and AWS. React and Git knowledge is desired.")
        page.click("button[type='submit']")
        
        # Wait for results to process
        page.wait_for_selector("text=Matching Results", timeout=10000)
        page.wait_for_timeout(3000)
        page.screenshot(path="uploads/screenshot_7_jobmatcher_results.png")
        print("    [OK] Saved: uploads/screenshot_7_jobmatcher_results.png")

        # Return to Dashboard
        page.click("button:has(svg.lucide-arrow-left)")
        page.wait_for_selector("text=Dashboard Overview", timeout=10000)

        # 5. Open Admin Panel
        print("[+] Step 8: Navigating to Admin Panel...")
        page.click("text=Admin Panel")
        page.wait_for_selector("text=Administrative Panel", timeout=10000)
        page.wait_for_timeout(3000)
        page.screenshot(path="uploads/screenshot_8_admin.png")
        print("    [OK] Saved: uploads/screenshot_8_admin.png")

        browser.close()
        print("="*60)
        print("  UI SCREENSHOT CAPTURE PROCESS COMPLETED SUCCESSFULLY")
        print("="*60)

if __name__ == "__main__":
    capture()

# auto_submit.py
import asyncio
from playwright.async_api import async_playwright

async def submit_to_second_site(applicant):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://secondwebsite.com/apply", timeout=60000)

        # Fill out the form fields (replace selectors with real ones)
        await page.fill("#first_name", applicant['first_name'])
        await page.fill("#last_name", applicant['last_name'])
        await page.fill("#email", applicant['email'])
        await page.fill("#phone", applicant['phone'])
        await page.fill("#country", applicant['country'])
        await page.fill("#city", applicant['city'])
        await page.fill("#address", applicant['address'])
        await page.fill("#position", applicant['position'])
        await page.fill("#additional_info", applicant['additional_info'])

        # Upload resume
        await page.set_input_files("input[type=file]", applicant['resume_path'])

        # Click submit button
        await page.click("button[type=submit]")

        # Wait for confirmation or redirect
        await page.wait_for_timeout(3000)  # wait for success message

        await browser.close()

# Helper to run easily
def run_submit(applicant):
    asyncio.run(submit_to_second_site(applicant))

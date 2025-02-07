import pandas as pd  # Add pandas for Excel export
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Specify the path to ChromeDriver
chrome_driver_path = "chromedriver.exe"

# Initialize WebDriver using the Service class
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

driver.maximize_window()

# Open the MYFutureJobs website
url = "https://candidates.myfuturejobs.gov.my/"
driver.get(url)

# Wait for the page to load completely
wait = WebDriverWait(driver, 10)

# Prepare a list to store job details
all_job_details = []

try:
    # Locate the scrollable div for the left panel
    left_scrollable_div = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "list__body"))
    )

    # Start with the first card ID
    card_index = 0

    while True:
        card_id = f"swipe-searchPageFrame-cardItem--{card_index}"  # Construct the card's data-test attribute
        try:
            # Locate the card using its unique data-test attribute
            card = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-test="{card_id}"]'))
            )

            # Scroll the card into view
            driver.execute_script("arguments[0].scrollIntoView(true);", card)
            time.sleep(1)  # Allow time for the card to scroll into view

            # Click the card
            card.click()
            time.sleep(2)  # Wait for the right panel to load

            # Locate the right panel
            right_panel = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "right-panel.search-page-02__details"))
            )

            # Extract job details
            job_details = {}
            try:
                job_details["title"] = right_panel.find_element(By.CLASS_NAME, "content").text
            except:
                job_details["title"] = "N/A"

            try:
                job_details["company"] = right_panel.find_element(By.CLASS_NAME, "vacancy-details-title-company").text
            except:
                job_details["company"] = "N/A"

            try:
                job_details["location"] = right_panel.find_element(By.CLASS_NAME, "vacancy-details-title-location").text
            except:
                job_details["location"] = "N/A"

            try:
                job_details["job details"] = right_panel.find_element(By.CLASS_NAME, "job-details").text
            except:
                job_details["job details"] = "N/A"

            try:
                job_details["vacancy description"] = right_panel.find_element(By.CLASS_NAME, "vacancy-description").text
            except:
                job_details["vacancy description"] = "N/A"

            print(f"Card {card_index} Details: {job_details}")

            # Append job details to the list
            all_job_details.append(job_details)

            # Scroll the right panel gradually to ensure all content is visible
            last_height = 0
            while True:
                driver.execute_script("arguments[0].scrollTop += 500;", right_panel)
                time.sleep(1)  # Wait for content to load

                # Check if we reached the bottom of the right panel
                new_height = driver.execute_script("return arguments[0].scrollTop;", right_panel)
                if new_height == last_height:
                    break
                last_height = new_height

            # Increment the card index to move to the next card
            card_index += 1

            # Scroll the left panel if necessary
            driver.execute_script("arguments[0].scrollTop += 500;", left_scrollable_div)
            time.sleep(2)  # Allow time for new cards to load

        except Exception as e:
            print(f"Error processing card {card_index}: {e}")
            break  # Exit if no more cards are found

except Exception as e:
    print(f"Error: {e}")

# Close the browser
driver.quit()

# Export job details to an Excel file
excel_file_path = "job_details.xlsx"
df = pd.DataFrame(all_job_details)  # Convert list of dictionaries to DataFrame
df.to_excel(excel_file_path, index=False)  # Export to Excel without including the index

print(f"Job details have been exported to {excel_file_path}.")

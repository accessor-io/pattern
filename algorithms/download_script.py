from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Path to the ChromeDriver
chrome_driver_path = '/home/dot/.cache/selenium/chromedriver/linux64/119.0.6045.105/chromedriver'  # Update this path

# Create a new directory
directory = "downloaded_pages"
if not os.path.exists(directory):
    os.makedirs(directory)

# Base URL of the website
base_url = "https://privatekeyfinder.io/btc-parsers/?page="

# Number of pages to download
num_pages = 135  # Adjust this number as needed

# Set up the WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Loop through the pages
for i in range(1, num_pages + 1):
    # Construct the URL for the current page
    url = f"{base_url}{i}"
    
    try:
        # Navigate to the page
        driver.get(url)
        
        # Get the page source
        page_source = driver.page_source
        
        # Save the page content to a file
        with open(f"{directory}/page_{i}.html", "w", encoding="utf-8") as file:
            file.write(page_source)
        print(f"Downloaded page {i}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Close the WebDriver
driver.quit()

print("Download complete.") 
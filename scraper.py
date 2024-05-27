from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait  # Import for WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  # Impor
import time

# Create a ChromeOptions instance
options = Options()

# Optional: Add any additional options you might need. For example, to run Chrome headless:
# options.add_argument('--headless')

# Initialize the Chrome WebDriver with the options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Your specific details
url = 'https://r6.tracker.network/'  # URL to visit
username_xpath = '//*[@id="hp-search"]/form/input[1]'  # XPath for the username input
continue_button_xpath = '//*[@id="hp-search"]/form/button'  # XPath for the continue button

# Visit the URL
driver.get(url)

# Find the username input element by XPath and type the username "tfue"
username_element = driver.find_element(By.XPATH, username_xpath)
username_element.send_keys('pckrnr')  # Typing "tfue" in the username field

# Find the continue button by XPath and click it
continue_button_element = driver.find_element(By.XPATH, continue_button_xpath)
continue_button_element.click()

# Optionally wait for 1 second (useful if you know the exact time needed, but not recommended for dynamic content)
time.sleep(1)

# Alternatively, wait for the KD element to be visible (recommended approach)
kd_xpath = "//div[@class='trn-defstats trn-defstats--width4']/div[div[contains(text(),'KD')]]/div[contains(@class,'trn-defstat__value')]"

# Wait up to 10 seconds for the KD element to be visible
kd_element = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, kd_xpath))
)

# Print the KD value
print("KD Ratio:", kd_element.text)

# Remember to close the browser window once you're done
# driver.quit()

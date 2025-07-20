from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

# Chrome setup
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Go to CoinGecko
    driver.get("https://www.coingecko.com/")
    
    # Wait for page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )
    
    # Click on 24h Volume header to sort by volume
    volume_header = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//th[contains(text(), '24h Volume')]"))
    )
    volume_header.click()
    
    # Wait for sorting to complete
    time.sleep(3)
    
    # Find all cryptocurrency rows
    rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'hover:tw-bg-gray-50')]")
    
    tokens = []
    
    # Extract data from first 25 rows
    for i, row in enumerate(rows[:50]):
        try:
            # Find the name and symbol container
            name_container = row.find_element(By.XPATH, ".//div[@class='tw-text-gray-700 dark:tw-text-moon-100 tw-font-semibold tw-text-sm tw-leading-5']")
            
            # Extract name (first text node)
            name_text = name_container.text.strip()
            name = name_text.split('\n')[0] if '\n' in name_text else name_text
            
            # Extract symbol from the nested div
            symbol_element = name_container.find_element(By.XPATH, ".//div[@class='tw-block 2lg:tw-inline tw-text-xs tw-leading-4 tw-text-gray-500 dark:tw-text-moon-200 tw-font-medium']")
            symbol = symbol_element.text.strip()
            
            token_data = {
                'name': name,
                'symbol': symbol
            }
            
            tokens.append(token_data)
            
        except Exception as e:
            continue
    
    # Save to JSON file
    with open('static-data/top-tokens-by-volume.json', 'w') as f:
        json.dump(tokens, f, indent=2)

except Exception as e:
    pass

finally:
    driver.quit()
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os

# Chrome setup
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Load tokens from the data file
tokens = []
data_file_path = 'static-data/top-tokens-by-volume.json'

if os.path.exists(data_file_path):
    with open(data_file_path, 'r') as f:
        token_data = json.load(f)
        tokens = [token['symbol'] for token in token_data]
else:
    # Fallback to hardcoded tokens if file doesn't exist
    tokens = ["BTC", "ETH", "XRP", "USDT", "BNB", "SOL", "USDC", "DOGE", "TRX", "ADA"]

# Initialize Binance data structure
binance_data = {
    "Binance": {}
}

# Go to Binance
driver.get("https://www.binance.com/en/fee/cryptoFee")
time.sleep(3)

# Search each token and extract data
for token in tokens:
    # Search for token
    search_box = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Search coin"]')
    search_box.click()
    search_box.send_keys(Keys.CONTROL + "a")
    search_box.send_keys(Keys.DELETE)
    search_box.send_keys(token.lower())
    time.sleep(3)
    
    # Initialize token data
    token_data = {}
    
    # Extract all rows from table
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody.bn-web-table-tbody tr[role='row']")
        
        for row in rows:
            try:
                # Get coin symbol (1st column)
                coin_symbol = row.find_element(By.CSS_SELECTOR, "td:nth-child(1)").text.strip()
                
                # Check if this is EXACTLY our token
                if coin_symbol.upper() == token.upper():
                    # Get networks (3rd column)
                    network_elements = row.find_elements(By.CSS_SELECTOR, "td:nth-child(3) div")
                    
                    # Get withdrawal fees (7th column)
                    fee_elements = row.find_elements(By.CSS_SELECTOR, "td:nth-child(7) div div")
                    
                    # Extract network and fee pairs
                    for j, network_elem in enumerate(network_elements):
                        network = network_elem.text.strip()
                        fee = fee_elements[j].text.strip() if j < len(fee_elements) else "N/A"
                        
                        if network and fee != "N/A":
                            # Clean network name - remove parentheses content
                            clean_network = network.split('(')[0].strip()
                            if '(' in network:
                                # Get the part in parentheses
                                network_code = network.split('(')[1].replace(')', '').strip()
                                clean_network = network_code
                            
                            token_data[clean_network] = fee
                        
            except Exception as e:
                continue
    
    except Exception as e:
        pass
    
    # Add token data to Binance structure
    if token_data:
        binance_data["BinanceUS"][token] = token_data

driver.quit()

# Save to JSON file
with open('static-data/binanceus-wth-fees.json', 'w') as f:
    json.dump(binance_data, f, indent=2)
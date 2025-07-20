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


# Initialize OKX data structure
okx_data = {
    "OKX": {}
}

# Go to OKX withdrawal fee page
driver.get("https://www.okx.com/en-us/fees/withdrawal-info")
time.sleep(3)

# Search each token and extract data
for token in tokens:
    print(f"\n=== {token} ===")
    
    # Find and use the search input
    search_box = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Search crypto"]')
    search_box.click()
    
    # Clear and search
    search_box.send_keys(Keys.CONTROL + "a")
    search_box.send_keys(Keys.DELETE)
    search_box.send_keys(token.upper())
    time.sleep(3)
    
    # Initialize token data
    token_data = {}
    
    # Extract withdrawal fees from table
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody.okui-table-tbody tr.okui-table-row")
        
        for row in rows:
            try:
                # Get token symbol (1st column)
                token_cell = row.find_element(By.CSS_SELECTOR, "td:first-child .index_contentItem__ELNFt")
                coin_symbol = token_cell.text.strip()
                
                # Check if this is EXACTLY our token
                if coin_symbol.upper() == token.upper():
                    # Get networks (3rd column)
                    network_elements = row.find_elements(By.CSS_SELECTOR, "td:nth-child(3) .index_contentItem__ELNFt")
                    
                    # Get withdrawal fees (5th column)
                    fee_elements = row.find_elements(By.CSS_SELECTOR, "td:nth-child(5) .index_contentItem__ELNFt")
                    
                    # Extract network and fee pairs
                    for j, network_elem in enumerate(network_elements):
                        network = network_elem.text.strip()
                        fee = fee_elements[j].text.strip() if j < len(fee_elements) else "N/A"
                        
                        if network and fee != "N/A":
                            # Clean network name for consistency
                            clean_network = network.replace("(", "").replace(")", "")
                            token_data[clean_network] = fee
                            print(f"  {clean_network}: {fee}")
                            
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"  Error: {e}")
    
    # Add token data to OKX structure
    if token_data:
        okx_data["OKX"][token] = token_data
    else:
        print(f"  No data found for {token}")

driver.quit()

# Save to JSON file
with open('static-data/okx-wth-fees.json', 'w') as f:
    json.dump(okx_data, f, indent=2)

print(f"\n✅ Data saved to static-data/okx-wth-fees.json")
print(f"Tokens processed: {len(okx_data['OKX'])}")
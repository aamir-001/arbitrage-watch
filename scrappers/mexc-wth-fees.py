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


# Initialize MEXC data structure
mexc_data = {
    "MEXC": {}
}

# Go to MEXC fee page
driver.get("https://www.mexc.com/fee")
time.sleep(3)

# Click on Deposit/Withdrawal tab
deposit_tab = driver.find_element(By.XPATH, "//div[text()='Deposit/Withdrawal']")
deposit_tab.click()
time.sleep(2)

# Search each token and extract data
for token in tokens:
    print(f"\n=== {token} ===")
    
    # Find the search input
    search_box = driver.find_element(By.CSS_SELECTOR, 'input[placeholder*="Search"]')
    search_box.click()
    
    # Clear and search
    search_box.send_keys(Keys.CONTROL + "a")
    search_box.send_keys(Keys.DELETE)
    search_box.send_keys(token.upper())
    time.sleep(3)
    
    # Initialize token data
    token_data = {}
    
    # Extract data from table
    try:
        # Find the token row
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.ant-table-row")
        
        for row in rows:
            try:
                # Get token symbol from first column
                token_cell = row.find_element(By.CSS_SELECTOR, "td:first-child span")
                coin_symbol = token_cell.text.strip()
                
                # Check if this is our token
                if coin_symbol.upper() == token.upper():
                    # Get networks (2nd column)
                    network_elements = row.find_elements(By.CSS_SELECTOR, "td:nth-child(2) .chargeContainer_colWrapper__gbZP9 span:first-child")
                    
                    # Get withdrawal fees (5th column)
                    fee_elements = row.find_elements(By.CSS_SELECTOR, "td:nth-child(5) .chargeContainer_colWrapper__gbZP9")
                    
                    # Extract network and fee pairs
                    for j, network_elem in enumerate(network_elements):
                        network = network_elem.text.strip()
                        fee = fee_elements[j].text.strip() if j < len(fee_elements) else "N/A"
                        
                        if network and fee != "N/A":
                            # Map network names to match your format
                            network_mapping = {
                                "ETH": "ERC20",
                                "BSC": "BEP20", 
                                "SOL": "SOL",
                                "ARB": "ARB",
                                "MATIC": "MATIC",
                                "AVAX_CCHAIN": "AVAX",
                                "BASE": "BASE",
                                "OP": "OP"
                            }
                            
                            clean_network = network_mapping.get(network, network)
                            token_data[clean_network] = fee
                            print(f"  {clean_network}: {fee}")
                            
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"  Error: {e}")
    
    # Add token data to MEXC structure
    if token_data:
        mexc_data["MEXC"][token] = token_data
    else:
        print(f"  No data found for {token}")

driver.quit()

# Save to JSON file
with open('static-data/mexc-wth-fees.json', 'w') as f:
    json.dump(mexc_data, f, indent=2)

print(f"\n✅ Data saved to static-data/mexc-wth-fees.json")
print(f"Tokens processed: {len(mexc_data['MEXC'])}")
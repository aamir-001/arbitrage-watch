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
# options.add_argument("--headless")  # Uncomment to run in headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Configuration
DEBUG_MODE = True  # Set to False to disable debug output

# Load tokens
tokens = []
data_file_path = 'static-data/top-tokens-by-volume.json'

if os.path.exists(data_file_path):
    with open(data_file_path, 'r') as f:
        token_data = json.load(f)
        tokens = [token['symbol'] for token in token_data]
else:
    tokens = ["BTC", "ETH", "XRP", "USDT", "BNB", "SOL", "USDC", "DOGE", "TRX", "ADA"]

# Output structure
gateio_data = {
    "Gate.io": {}
}

# Open page
driver.get("https://www.gate.io/fee")
time.sleep(3)

# Click on Deposit & Withdrawal tab
try:
    deposit_tab = driver.find_element(By.XPATH, "//div[contains(@class, 'mantine-GateTabs-tabLabel')]//h1[contains(text(), 'Deposit & Withdrawal')]")
    deposit_tab.click()
    time.sleep(2)
except:
    print("Deposit & Withdrawal tab already selected")

# Process tokens
for token in tokens:
    print(f"\n=== {token} ===")
    
    try:
        # Find search input with multiple selectors
        search_box = None
        selectors = [
            'input[data-sharkid="__0"]',
            'input[placeholder*="Please enter the cryptocurrency you want to search for"]',
            'input.mantine-GateInput-input.mantine-Input-input',
            'div.deposit-search input',
            'input.mantine-yn0jds',
            'input[type="text"]'
        ]
        
        for selector in selectors:
            try:
                search_box = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue

        if not search_box:
            print("  Search box not found")
            continue

        # Clear and search
        search_box.click()
        time.sleep(0.5)
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.DELETE)
        time.sleep(0.5)
        search_box.send_keys(token.upper())
        time.sleep(2)
        search_box.send_keys(Keys.ENTER)
        time.sleep(3)

        # Scroll to load content
        try:
            scroll_area = driver.find_element(By.CSS_SELECTOR, ".table-row-list")
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_area)
            time.sleep(2)
        except:
            pass

        token_data = {}
        
        # Find all table rows
        rows = driver.find_elements(By.CSS_SELECTOR, ".rate-table-con .table-row-list .table-row")
        print(f"  Found {len(rows)} rows")
        
        if not rows:
            # Try alternative selectors
            alternative_selectors = [
                ".table-row-list .table-row",
                ".rate-table-con .table-row",
                "[class*='table-row']"
            ]
            
            for selector in alternative_selectors:
                try:
                    rows = driver.find_elements(By.CSS_SELECTOR, selector)
                    if rows:
                        print(f"  Found {len(rows)} rows with selector: {selector}")
                        break
                except:
                    continue
        
        if not rows and DEBUG_MODE:
            # Print page source for debugging
            print("  No rows found, printing page structure...")
            try:
                table_container = driver.find_element(By.CSS_SELECTOR, ".rate-table-con")
                print("  Table container HTML:")
                print(table_container.get_attribute('outerHTML')[:1000] + "...")
            except:
                print("  Could not find table container")
        
        if not rows:
            print(f"  No table rows found for {token}")
            continue
        
        for row in rows:
            try:
                # Try multiple selectors for the token symbol cell
                first_cell = None
                selectors = [
                    ".table-cell .td-chain-first p",
                    ".table-cell:nth-child(2) .td-chain-first p",
                    ".td-chain-first p"
                ]
                
                for selector in selectors:
                    try:
                        first_cell = row.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue
                
                if not first_cell:
                    continue
                
                # Extract just the token symbol (before the span)
                full_text = first_cell.text
                try:
                    span_elem = first_cell.find_element(By.TAG_NAME, "span")
                    span_text = span_elem.text
                    symbol_text = full_text.replace(span_text, "").strip().upper()
                except:
                    # If no span found, take the first word
                    symbol_text = full_text.split()[0].upper()
                
                print(f"  Found symbol: {symbol_text}")
                
                # Check if this matches our target token
                if symbol_text == token.upper():
                    # Get all network elements from the appropriate column
                    network_elements = []
                    network_selectors = [
                        ".table-cell:nth-child(3) .td-chain-item p",
                        ".table-cell:nth-child(2) .td-chain-item p"
                    ]
                    
                    for selector in network_selectors:
                        try:
                            network_elements = row.find_elements(By.CSS_SELECTOR, selector)
                            if network_elements:
                                break
                        except:
                            continue
                    
                    # Get all withdrawal fee elements from the appropriate column
                    fee_elements = []
                    fee_selectors = [
                        ".table-cell:nth-child(5) .td-chain-item p",
                        ".table-cell:nth-child(4) .td-chain-item p"
                    ]
                    
                    for selector in fee_selectors:
                        try:
                            fee_elements = row.find_elements(By.CSS_SELECTOR, selector)
                            if fee_elements:
                                break
                        except:
                            continue
                    
                    print(f"  Found {len(network_elements)} networks and {len(fee_elements)} fees")
                    
                    # Match networks with their corresponding fees
                    for i, network_elem in enumerate(network_elements):
                        network = network_elem.text.strip()
                        if i < len(fee_elements):
                            fee = fee_elements[i].text.strip()
                            if network and fee and fee != "0":
                                token_data[network] = fee
                                print(f"    {network}: {fee}")
                    
                    # If we found our token, break the loop
                    break
                    
            except Exception as e:
                print(f"  Row processing error: {e}")
                continue

        if token_data:
            gateio_data["Gate.io"][token] = token_data
        else:
            print(f"  No withdrawal fee data found for {token}")

    except Exception as e:
        print(f"  Error processing {token}: {e}")

# Close browser
driver.quit()

# Save output
os.makedirs("static-data", exist_ok=True)
output_path = "static-data/gateio-wth-fees.json"
with open(output_path, "w") as f:
    json.dump(gateio_data, f, indent=2)

print(f"\n✅ Data saved to {output_path}")
print(f"Tokens processed: {len(gateio_data['Gate.io'])}")
print(f"Total tokens with data: {sum(1 for token_data in gateio_data['Gate.io'].values() if token_data)}")
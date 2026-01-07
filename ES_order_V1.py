from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import random
import os

# Initialize driver and wait
user_email = input("Enter email: ")
driver = webdriver.Chrome()
driver.maximize_window()
wait = WebDriverWait(driver, 20)
website_main = "https://es.ermenrich.com/"


# Choose random sku
def choose_sku():
    skus = [83836, 83820, 84547, 84545, 83089, 84558, 84638, 84087, 83842, 85574] #first 5 are under 70 EU, last 5 are 70+
    sku_num = random.randint(0,9)
    sku = skus[sku_num]
    return(sku)

def choose_address():
    # Define a list of shipping addresses
    shipping_addresses = [
    {
        'country': 'España',
        'city': 'Zaragoza',
        'address': 'Calle de Palomeque, 32',
        'phone': '+34976126690',
        'postal_code': '50004'
    },
    {
        'country': 'España',
        'city': 'Murcia', 
        'address': 'Av. Marqués de Los Vélez, 2',
        'phone': '+34968218699',
        'postal_code': '30007'
    },
    {
        'country': 'España',
        'city': 'Valencia',
        'address': 'Carrer del Poeta Monmeneu, 3',
        'phone': '+34963511358',
        'postal_code': '46009'
    }
]
    address = shipping_addresses[random.randint(0,2)] 
    return(address) #returns a dictionary


def take_screenshot(name):
    # Helper function to take screenshots for debugging
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    filename = f"screenshots/{name}_{int(time.time())}.png"
    driver.save_screenshot(filename)
    print(f"Screenshot saved as: {filename}")
    return filename

def extract_price(price_text):
    # Extract numeric price from text
    # Remove currency symbols, spaces, and other non-numeric characters except decimal point
    clean_text = re.sub(r'[^\d,]', '', price_text)
    # Replace comma with dot if needed (for European format)
    clean_text = clean_text.replace(',', '.')
    try:
        return float(clean_text)
    except ValueError:
        return None

def get_item_price_search_card():
    # Get item price from search results card
    try:
        # Look for price in product card after search
        price_element = driver.find_element(By.CSS_SELECTOR, ".product-card__price")
        return extract_price(price_element.text)
    except:
        return None

def get_item_price_basket():
    # Get item price from basket/cart page (only visible price)
    try:
        # Find ALL elements with the price class
        price_elements = driver.find_elements(By.CSS_SELECTOR, ".cart-panel__result-price")
        
        # Filter to only visible elements
        visible_prices = []
        for element in price_elements:
            if element.is_displayed():
                price = extract_price(element.text)
                if price is not None:
                    visible_prices.append(price)
        
        if visible_prices:
            # If multiple visible prices, take the first one (should be the total)
            return visible_prices[0]
        
        # Fallback: if no visible elements, try to get any
        for element in price_elements:
            price = extract_price(element.text)
            if price is not None:
                return price
                
        return None
        
    except Exception as e:
        print(f"Error getting basket price: {str(e)}")
        return None

def get_item_price_order_page():
    # Get item price from order page (before shipping)
    try:
        # Element ID like 'bx-cost-items' or similar
        price_element = driver.find_element(By.ID, 'bx-cost-items')
        return extract_price(price_element.text)
    except:
        return None

def get_shipping_price_order_page():
    # Get shipping price from order page (after country selection)
    try:
        price_element = driver.find_element(By.ID, 'bx-cost-shipping')
        shipping_text = price_element.text.strip()
        
        print(f"Shipping text found: '{shipping_text}'")
        
        # Check for free shipping
        if "envío gratuito" in shipping_text.lower():
            print("✓ Free shipping detected")
            return 0.0
        
        # Check for "Por determinar" (= to be determined)
        if "por determinar" in shipping_text.lower():
            print("✗ WARNING: Shipping price not determined yet (Por determinar)")
            print("This might mean: 1) Country not selected, 2) Delivery option not loaded, 3) System delay")
            take_screenshot("shipping_not_determined")
            return None  # Explicitly return None to indicate undetermined state
        
        # Try to extract numeric price
        price = extract_price(shipping_text)
        if price is not None:
            print(f"✓ Shipping price: {price}€")
            return price
        else:
            print(f"✗ Could not extract shipping price from text: '{shipping_text}'")
            take_screenshot("shipping_price_extraction_failed")
            return None
            
    except Exception as e:
        print(f"Error getting shipping price: {str(e)}")
        take_screenshot("shipping_price_error")
        return None

def get_total_price_order_page():
    # Get total price (item + shipping) from order page
    try:
        # Look for total price element
        price_element = driver.find_element(By.CLASS_NAME, 'cart-panel__result-price')
        return extract_price(price_element.text)
    except:
        print("✗ Could not find total price")
        return None
    
def close_cookie_popup():
    # Close the cookie consent popup if present
    try:
        accept_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".cky-btn.cky-btn-accept"))
        )
        accept_button.click()
        print("Cookie popup closed by {selector}")
        time.sleep(1)
        return True    
     
    except Exception as e:
        print(f"Error handling cookie popup: {str(e)}")
        return False

def search_for_sku(sku):
    # Search for a specific SKU on the website
    try:
        print("Navigating to main page...")
        driver.get(website_main)
        time.sleep(3)

        close_cookie_popup()
        
        print("Opening search box...")
        search_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".header__search")))
        search_box.click()
        time.sleep(1)
        
        print("Entering SKU...")
        search_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="uscar"]')))
        search_input.clear()
        search_input.send_keys(str(sku))
        
        print("Submitting search...")
        search_input.send_keys(Keys.ENTER)
        
        print("Waiting for results to load...")
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".product-card"))
            )
        except:
            time.sleep(5)
        
        print("Search completed successfully")
        return True
        
    except Exception as e:
        print(f"Search failed: {str(e)}")
        take_screenshot("search_error")
        return False

def get_offer_id_for_sku(sku):
    # Extract the offerId for the product with the given SKU
    try:
        print("Finding product offer ID...")
        
        # Find the product card that contains our SKU
        sku_element = wait.until(
            EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), 'ID {sku}')]"))
        )
        print(f"Found SKU element: {sku_element.text}")
        
        # Find the product card container
        product_card = sku_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'product-card')]")
        
        # Extract the offer ID from the data attributes
        offer_id = product_card.get_attribute('data-offer-id')
        if offer_id:
            print(f"Found offer ID {offer_id}")
            return int(offer_id)      
        
    except Exception as e:
        print(f"Failed to get offer ID: {str(e)}")
        take_screenshot("offer_id_error")
        return None

def add_to_cart_via_api(offer_id, quantity=1):
    # Add item to cart using the direct API call
    try:
        print("Adding item to cart via API...")
        
        # Execute JavaScript to make the API call
        script = f"""
            // Make the API call to add to cart
            fetch('/rest/methods/user/basket/change', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }},
                body: JSON.stringify({{offerId: {offer_id}, quantity: {quantity}}})
            }})
            .then(response => response.json())
            .then(data => {{
                console.log('API response:', data);
                // Update the UI to reflect the cart change
                if (data.result && data.result.basket) {{
                    // Update add to cart button to show counter
                    const addButtons = document.querySelectorAll('.product-card__basket');
                    addButtons.forEach(button => {{
                        if (button.closest('[data-offer-id="{offer_id}"]') || 
                            button.closest('[data-product-id="{offer_id}"]')) {{
                            button.innerHTML = '<div class="counter"><button type="button" class="counter-btn counter-minus">-</button><input type="number" value="{quantity}" min="1" max="999"><button type="button" class="counter-btn counter-plus">+</button></div>';
                        }}
                    }});
                }}
            }})
            .catch(error => {{
                console.error('API error:', error);
            }});
        """
        
        # Execute the JavaScript
        driver.execute_script(script)
        
        # Wait for the UI to update
        time.sleep(3)        
        print("API call completed successfully")
        return True
        
    except Exception as e:
        print(f"Failed to add to cart via API: {str(e)}")
        take_screenshot("api_add_error")
        return False

def navigate_to_cart_directly():
    # Navigate to the cart page directly by URL
    try:
        cart_url = "https://es.ermenrich.com/basket/"
        print(f"Navigating to cart URL: {cart_url}")
        
        driver.get(cart_url)
        time.sleep(3)
        
        # Check if we're on a cart page
        current_url = driver.current_url.lower()
        if "basket" in current_url:
            print("Successfully navigated to cart page")
            return True
        else:
            print(f"Not on cart page. Current URL: {driver.current_url}")
            return False
        
    except Exception as e:
        print(f"Failed to navigate to cart: {str(e)}")
        take_screenshot("cart_navigation_error")
        return False

def check_cart_contents(sku):
    # Check if the cart has our specific item
    print("Checking cart contents...")
    try:
        sku_element = driver.find_element(By.XPATH, f"//*[contains(text(), 'ID: {sku}')]")
        take_screenshot("cart_with_our_item")
        return True
            
    except Exception as e:
        print(f"Error checking cart contents: {str(e)}")
        take_screenshot("cart_check_error")
        return False

def select_payment_option():
    # Randomly select a payment option for orders over 70€ using element IDs
    try:
        print("Selecting payment option...")
        
        # Define payment options with their corresponding IDs (equal probability)
        payment_options = {
            "Tarjeta de crédito/débito": "ID_PAY_SYSTEM_ID_38",
            "Transferencia bancaria": "ID_PAY_SYSTEM_ID_37",
            "Bizum": "ID_PAY_SYSTEM_ID_41",
            "Pago contra reembolso": "ID_PAY_SYSTEM_ID_36",
            "Paygold": "ID_PAY_SYSTEM_ID_42",
            "PayPal": "ID_PAY_SYSTEM_ID_35"
        }

        # Randomly select any payment option
        selected_option_name = random.choice(list(payment_options.keys()))
        selected_option_id = payment_options[selected_option_name]
        
        print(f"Selected payment option: {selected_option_name} (ID: {selected_option_id})")

        # Only interact with the UI if it's not the default option
        if selected_option_name != "Tarjeta de crédito/débito":
            # Find and click the payment option using its ID
            try:
                # Find and click the label of the payment option
                payment_label = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f"label[for='{selected_option_id}']"))
                )
                print("Found payment label, attempting to click...")

                # Scroll to the label
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", payment_label)
                time.sleep(0.5)

                # Click the label
                payment_label.click()
                time.sleep(1)

                #Verify the option was selected by checking the input
                payment_input = driver.find_element(By.ID, selected_option_id)
                if payment_input.is_selected():
                    clean_option_name = selected_option_name.lower().replace(' ', '_').replace('\\', '_')
                    take_screenshot(f"selected_{clean_option_name}")
                    print(f"Successfully selected {selected_option_name} payment option")
                    return True, selected_option_name

                else:
                    print("Label click didn't change selection state")
                    # Fallback to JavaScript click if needed
                    driver.execute_script("arguments[0].click();", payment_input)
                    time.sleep(1)
                    if payment_input.is_selected():
                        print("Successfully selected using JavaScript fallback")
                        return True, selected_option_name
                    return False, selected_option_name

            except Exception as e:
                    print(f"Failed to select payment option {selected_option_name}: {str(e)}")
                    return False, selected_option_name
        else:
            print("Using default payment option (Bank transfer), no action needed")
            return True, selected_option_name

    except Exception as e:
            print(f"Error in payment selection process: {str(e)}")
            take_screenshot("payment_option_error")
            return False, "Error"

# Create a simple step counter class
class StepCounter:
    def __init__(self):
        self.step = 1
    
    def print_step(self, message):
        print(f"\n--- Step {self.step}: {message} ---")
        self.step += 1

def fill_order_form():
    try:
        ship_to = choose_address() #is a dictionary
        print(f"Chosen address in: {str(ship_to['city'])}")
        
        # Wait for the form to be present
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "bx-input-order-EMAIL"))
        )
        
        print("Form found, starting to fill fields...")
        take_screenshot("form_loaded")
        
        # Contact information
        print("Filling contact information...")
        
        # Email field
        try:
            email_field = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "bx-input-order-EMAIL"))
            )
            email_field.clear()
            email_field.send_keys(user_email)
            print("✓ Email field filled")
        except Exception as e:
            print(f"✗ Error with email field: {str(e)}")
            take_screenshot("email_field_error")
            return False
        
        # Phone field
        try:
            phone_field = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "bx-input-order-PHONE"))
            )
            phone_field.clear()
            phone_field.send_keys(ship_to['phone'])
            print("✓ Phone field filled")
        except Exception as e:
            print(f"✗ Error with phone field: {str(e)}")
            take_screenshot("phone_field_error")
            return False
        
        # Name field
        try:
            name_field = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "bx-input-order-FIO_SHIP"))
            )
            name_field.clear()
            name_field.send_keys("Alena Auto Test")
            print("✓ Name field filled")
        except Exception as e:
            print(f"✗ Error with name field: {str(e)}")
            take_screenshot("name_field_error")
            return False
        
        # Order comment
        try:
            comment_field = driver.find_element(By.ID, "bx-input-order-USER_DESCRIPTION")
            driver.execute_script('arguments[0].value = "Alena Auto Test\\nThis order was made by Alyona\'s helpful minions";', comment_field)
            print("✓ Comment field filled")
        
        except Exception as e:
            print(f"✗ Error with comment field: {str(e)}")
            take_screenshot("comment_field_error")
        
        # Shipping address
        print("Filling shipping address...")
        
        # Country field (a dropdown with typeahead)
        try:
            country_field = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "bx-input-order-COUNTRY_SHIPPING-ts-control"))
            )
            country_field.click()
            country_field.clear()
            country_field.send_keys(ship_to['country'])
            # Wait a moment for the dropdown to appear and select the first option
            time.sleep(1)
            country_field.send_keys(Keys.ENTER)
            print("✓ Country selected")
            
            # Add a small delay after country selection to allow any JavaScript to process
            time.sleep(1)
            
            # Click elsewhere to ensure the country field loses focus
            driver.find_element(By.TAG_NAME, "body").click()
            time.sleep(0.5)
            
        except Exception as e:
            print(f"✗ Error with country field: {str(e)}")
            take_screenshot("country_field_error")
            return False
        
        # City field 
        try:
            # Wait for the city field to be interactable
            city_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "bx-input-order-CITY_SHIP"))
            )
            
            # Scroll to the element to ensure it's in view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", city_field)
            time.sleep(0.5)
            
            # Click on the field to ensure focus
            city_field.click()
            time.sleep(0.5)
            
            # Clear and fill the field
            city_field.clear()
            city_field.send_keys(ship_to['city'])
            print("✓ City field filled")
            
            # Press Tab to move to next field (this might help with form validation)
            city_field.send_keys(Keys.TAB)
            time.sleep(0.5)
            
        except Exception as e:
            print(f"✗ Error with city field: {str(e)}")
            take_screenshot("city_field_error")
            return False
        
        # Address field
        try:
            address_field = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "bx-input-order-ADDRESS_SHIP"))
            )
            
            # Click to ensure focus
            address_field.click()
            time.sleep(0.5)
            
            address_field.clear()
            address_field.send_keys(ship_to['address'])
            print("✓ Address field filled")
            
            # Press Tab to move to next field
            address_field.send_keys(Keys.TAB)
            time.sleep(0.5)
            
        except Exception as e:
            print(f"✗ Error with address field: {str(e)}")
            take_screenshot("address_field_error")
            return False
        
        # Postal code field
        try:
            postal_code_field = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "bx-input-order-ZIP_SHIP"))
            )
            
            # Click to ensure focus
            postal_code_field.click()
            time.sleep(0.5)
            
            postal_code_field.clear()
            postal_code_field.send_keys(ship_to['postal_code'])
            print("✓ Postal code field filled")
            
        except Exception as e:
            print(f"✗ Error with postal code field: {str(e)}")
            take_screenshot("postal_code_field_error")
            return False
        
        # Billing address is the same as shipping (default tick remains)
        print("Billing address remains same as shipping (default)")
        
        # Check delivery options
        print("Checking delivery options...")
        try:
            # Look for the specific courier delivery option
            courier_option = driver.find_elements(By.CSS_SELECTOR, "label[for='ID_SHIPPING_METHOD_ID_17']")

            if len(courier_option) == 1:
                print("Found 1 delivery option as expected (Entrega por mensajería)")
            elif len(courier_option) > 1:
                print(f"WARNING: Found {len(courier_option)} delivery options, expected only 1 (Entrega por mensajería)")
            else:
                print("Could not find the Entrega por mensajería option")

                # Try alternative selectors if needed - CHECK IF STILL NEEDED
                alternative_options = driver.find_elements(By.XPATH, "//label[contains(text(), 'Entrega')]")
                if alternative_options:
                    print(f"Found {len(alternative_options)} alternative delivery options containing 'Entrega'")

        except Exception as e:
            print(f"Could not check delivery options: {str(e)}")
        
        take_screenshot("order_form_filled")
        print("Order form filled successfully")
        return True
        
    except Exception as e:
        print(f"Error filling order form: {str(e)}")
        take_screenshot("order_form_error")
        return False

def rename_screenshots_folder(order_number):
    # Rename screenshots folder with order number
    try:
        source = "C:/Users/your_folder/screenshots"
        dest = f"C:/Users/your_folder/{order_number}"
        
        if os.path.exists(source):
            os.rename(source, dest)
            print(f"✓ Screenshots folder renamed to: {order_number}")
        else:
            print(f"✗ Screenshots folder not found at: {source}")
            
    except OSError as error:
        print(f"✗ Could not rename folder: {error}")
        # Create a new folder with order number anyway
        try:
            dest = f"C:/Users/astavrova/Desktop/Алена (врем.)/0 - автоматизация/orders/lvh-auto-tests/monthly/{order_number}"
            os.makedirs(dest, exist_ok=True)
            print(f"✓ Created folder: {order_number}")
        except:
            pass
        
def place_order():
    # Finalize the order by clicking the checkout button on the order form
    # Final order submission with error checking
    try:
        print("Placing final order...")
        
        take_screenshot("before_final_order")
        
        # Find and click the final order submit button 
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        )
        print(f"✓ Clicking final order button: '{submit_button.text}'")
        
        # Scroll to button
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
        time.sleep(1)
        
        # Click the button
        submit_button.click()

        # IMMEDIATELY check for JavaScript/form validation errors
        time.sleep(2)  # Give time for any JS validation to run
        
        # Check for the "already exists" error specifically
        error_found = False
        error_text = ""
        
        # Try multiple ways to find error messages
        error_selectors = [
            # By specific error text (most reliable)
            (By.XPATH, "//*[contains(text(), 'existe un usuario')]"),
            
            # By CSS classes that might indicate errors
            (By.CSS_SELECTOR, ".alert-content")
        ]
        
        for by, selector in error_selectors:
            try:
                elements = driver.find_elements(by, selector)
                for elem in elements:
                    if elem.is_displayed():
                        error_text = elem.text[:100] if elem.text else "Unknown error"
                        print(f"✗ Found error: {error_text}")
                        error_found = True
                        take_screenshot(f"order_error_{by[1][:20]}")
                        break
                if error_found:
                    break
            except:
                continue
        
        if error_found:
            print("✗ Order blocked by error - NOT placed")
            return False
        
        # If no errors found, check for success
        print("No errors detected, checking for order confirmation...")
        
        # Wait a bit for potential redirect
        time.sleep(3)
        
        # Check 1: Success URL with ORDER_ID
        current_url = driver.current_url
        if "ORDER_ID=" in current_url:
            try:
                import urllib.parse
                parsed_url = urllib.parse.urlparse(current_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                order_number = query_params.get('ORDER_ID', [None])[0]
                
                if order_number:
                    print(f"✓ ORDER CONFIRMED! Order number: {order_number}")
                    take_screenshot("order_confirmation")
                    
                    # Handle payment popups if any
                    main_window = driver.current_window_handle
                    if len(driver.window_handles) > 1:
                        print("Closing payment popup tabs...")
                        for handle in driver.window_handles:
                            if handle != main_window:
                                driver.switch_to.window(handle)
                                driver.close()
                        driver.switch_to.window(main_window)
                    
                    # Rename screenshots folder
                    rename_screenshots_folder(order_number)
                    return order_number
            except Exception as e:
                print(f"✗️ Could not parse order number: {str(e)}")
                  
        # Check 2: Are we still on the order page? (form didn't submit)
        if "order" in current_url and "ORDER_ID=" not in current_url:
            # Check if submit button is still there
            try:
                still_exists = driver.find_elements(By.ID, "submit")
                if still_exists:
                    print("✗ Still on order page with submit button - order NOT placed")
                    take_screenshot("still_on_order_page")
                    return False
            except:
                pass
        
        # If we're unsure
        print("✗ Order status unclear after submission")
        print("Check email to confirm")
        take_screenshot("order_status_unclear")
        return False  # Be conservative
        
    except Exception as e:
        print(f"✗ Error in final order submission: {str(e)}")
        take_screenshot("final_order_error")
        return False

def proceed_to_checkout():
    # Click the checkout button and verify redirection Basket > Order page
    try:
        print("Looking for checkout button...")
        checkout_button = driver.find_element(By.XPATH, f"//*[contains(text(), 'Para pasar por caja')]")
        if checkout_button and checkout_button.is_displayed():
            print(f"Found checkout button")
                                
        if not checkout_button:
            raise Exception("Could not find checkout button")
        
        # Scroll to the button if needed
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", checkout_button)
        time.sleep(1)
        
        take_screenshot("before_checkout_click")
        
        # Click the button
        print("Clicking checkout button...")
        checkout_button.click()
        
        # Wait for the order page to load
        print("Waiting for order page to load...")
        WebDriverWait(driver, 15).until(
            EC.url_contains("order")
        )
        
        # Verify we're on the order page
        current_url = driver.current_url.lower()
        if "order" in current_url:
            print(f"Successfully navigated to order page: {driver.current_url}")
            take_screenshot("order_page")
            return True
        else:
            print(f"Not on order page. Current URL: {driver.current_url}")
            take_screenshot("not_on_order_page")
            return False
        
    except Exception as e:
        print(f"Failed to proceed to checkout: {str(e)}")
        take_screenshot("checkout_error")
        return False

def verify_free_shipping():
    # Verify that free shipping is applied for orders over 70€
    try:
        print("Verifying free shipping...")
        
        # Wait a moment for the page to update after address entry
        time.sleep(2)
        
        # Look for the free shipping element
        free_shipping_element = wait.until(
            EC.presence_of_element_located((By.ID, "bx-cost-shipping"))
        )
        
        # Check if the element contains "Free shipping" text
        if "Envío gratuito" in free_shipping_element.text:
            print("✓ Free shipping verified successfully!")
            return True
        else:
            print(f"✗ Free shipping not applied. Shipping cost: {free_shipping_element.text}")
            take_screenshot("shipping_cost_error")
            return False
            
    except Exception as e:
        print(f"Error verifying free shipping: {str(e)}")
        take_screenshot("free_shipping_verification_error")
        return False

def verify_shipping_cost():
    # Verify that shipping cost is correct for orders under 70€
    try:
        delivery_cost_element = driver.find_element(By.ID, 'bx-cost-shipping')
        delivery_cost_text = delivery_cost_element.text
        delivery_cost = extract_price(delivery_cost_text)
        if delivery_cost is not None:
            if delivery_cost == shipping_cost:
                print(f"✓ Delivery cost is {str(shipping_cost)}€, just as expected")
                return delivery_cost
            else:
                print("✗ Delivery cost is {sr(delivery_cost)}€, while it should be {str(shipping_cost)}€")
        else:    
            print("Could not find delivery cost on page")
            return None
        
    except Exception as e:
        print(f"Error extracting price: {str(e)}")
        return None
        
# Main execution
if __name__ == "__main__":
    try:
        # Initialize all price trackers
        price_data = {
            'search_card': None,
            'basket': None,
            'order_item': None,
            'shipping': None,
            'order_total': None
        }

        # Initialize step counter
        step_counter = StepCounter()
        print("Running ES script")
        print("---------------LOGS FOR NERDS---------------")

        delivery_option = 'Entrega por mensajería (Courier delivery)'
        sku = choose_sku()
        payment_option_for_summary = "Default"  
        order_result = None  
        shipping_verified = False
        
        print(f"Chosen SKU: {str(sku)}")
        
        step_counter.print_step("Searching for SKU")
        
        if search_for_sku(sku):
            # Get price from search card
            price_data['search_card'] = get_item_price_search_card()
            print(f"✓ Search card price: {price_data['search_card']}€")

            step_counter.print_step("Getting offer ID")
            offer_id = get_offer_id_for_sku(sku)
            
            if offer_id:
                step_counter.print_step("Adding to cart via API")
                
                if add_to_cart_via_api(offer_id, 1):
                    step_counter.print_step("Refreshing page to synchronize UI")
                    driver.refresh()
                    time.sleep(3)
                    step_counter.print_step("Navigating to cart")
                    
                    if navigate_to_cart_directly():
                        step_counter.print_step("Checking cart contents")

                        # First check if item is in cart
                        if not check_cart_contents(sku):
                            print("✗ Item was added but not found in cart")
                            # Handle error - maybe continue or exit

                        # Get price from cart
                        step_counter.print_step("Getting cart price")  
                        price_data['basket'] = get_item_price_basket()

                        if price_data['basket'] is None:
                            print("✗ Could not extract price from basket page")
                            # Continue anyway or handle as needed
                        else:
                            print(f"✓ Cart price: {price_data['basket']}€")

                        # Compare search vs basket prices
                        if price_data['search_card'] and price_data['basket']:
                            if abs(price_data['search_card'] - price_data['basket']) > 0.01:
                                print(f"✗ WARNING: Price mismatch! Search: {price_data['search_card']}€, Cart: {price_data['basket']}€")

                        # NOW PROCEED TO CHECKOUT
                        step_counter.print_step("Proceeding to checkout")
                        
                        if proceed_to_checkout():
                            # Get all prices from order page
                            step_counter.print_step("Getting order page prices")
                            price_data['order_item'] = get_item_price_order_page()
                            price_data['shipping'] = get_shipping_price_order_page()
                            price_data['order_total'] = get_total_price_order_page()
                    
                            print(f"Order page - Item: {price_data['order_item']}€, "
                                  f"Shipping: {price_data['shipping'] if price_data['shipping'] is not None else 'N/A'}€, "
                                  f"Total: {price_data['order_total']}€")
                                    
                            # Verify calculation: item + shipping = total
                            if (price_data['order_item'] is not None and 
                                price_data['shipping'] is not None and 
                                price_data['order_total'] is not None):
                                calculated_total = price_data['order_item'] + price_data['shipping']
                                if abs(calculated_total - price_data['order_total']) > 0.01:
                                    print(f"✗ WARNING: Price calculation mismatch! "
                                        f"Item({price_data['order_item']}) + Shipping({price_data['shipping']}) = {calculated_total}€ "
                                        f"but Total shows: {price_data['order_total']}€")

                            # Now check if form can be filled                                             
                            if fill_order_form():
                                # Check if order value is over 70€ to verify free shipping
                                if price_data['order_item'] and price_data['order_item'] >= 70:
                                    step_counter.print_step("Verifying free shipping")
                                    if not verify_free_shipping():
                                        print("✗ Free shipping verification failed, but continuing with order")
                                    else:
                                        shipping_verified = True
                                else:
                                    step_counter.print_step("Verifying shipping cost")
                                    # Check if shipping is 7€ for orders under 70€
                                    if price_data['shipping'] is not None:
                                        if price_data['shipping'] == 7.0:
                                            print(f"✓ Shipping cost is {price_data['shipping']}€, just as expected")
                                            shipping_verified = True
                                        else:
                                            print(f"✗ Shipping cost is {price_data['shipping']}€, expected 7€")
                                    else:
                                        print("✗ Could not verify shipping cost")

                                # All orders have same payment options
                                step_counter.print_step("Selecting payment option")
                                payment_success, chosen_payment_option = select_payment_option()

                                if not payment_success:
                                    print("✗ Payment selection failed, but continuing with order process")

                                payment_option_for_summary = chosen_payment_option
                                
                                step_counter.print_step("Placing order")
                                order_result = place_order()

                                if order_result:
                                    if isinstance(order_result, str):
                                        print(f"✓ Order successfully placed! Order number: {order_result}")
                                    else:
                                        print("✓ Order successfully placed!")
                                    print("Please check your email and 1C system for order confirmation")
                                else:
                                    print("✗ Failed to place order")
                            else:
                                print("✗ Failed to fill order form")
                        else:
                            print("\n✗ Failed to proceed to checkout")
                    else:
                        print("\n✗ Failed to navigate to cart")
                else:
                    print("\n✗ Failed to add item to cart via API")
            else:
                print("\n✗ Could not find offer ID for the product")
        else:
            print("\n✗ Failed to search for SKU")
        
        print("\nProcess completed. Browser will close in 10 seconds.")
        
        # Summary
        print("\n----------ORDER INFO----------")
        if order_result:
            print(f"Order number: {order_result}")
        else:
            print("Order number: order wasn't placed")
        print(f"Chosen SKU: {str(sku)}")
        print(f"Search card price: {price_data['search_card'] if price_data['search_card'] else 'N/A'}€")
        print(f"Basket price: {price_data['basket'] if price_data['basket'] else 'N/A'}€")
        print(f"Order item price: {price_data['order_item'] if price_data['order_item'] else 'N/A'}€")
        print(f"Shipping price: {price_data['shipping'] if price_data['shipping'] is not None else 'N/A'}€")
        print(f"Order total price: {price_data['order_total'] if price_data['order_total'] else 'N/A'}€")
        print(f"Delivery option: {delivery_option}")
        print(f"Selected payment option: {payment_option_for_summary}")
        print(f"Shipping verified: {'Yes' if shipping_verified else 'No'}")
        print("----------END----------")
        time.sleep(10)
        
    except Exception as e:
        print(f"\n✗ Script failed with error: {str(e)}")
        take_screenshot("main_script_error")          
   
    finally:
        driver.quit()





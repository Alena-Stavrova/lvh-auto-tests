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
website_main = "https://it.ermenrich.com/"

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
        'country': 'Italia',
        'city': 'Torino',
        'address': 'Via Alessandro Volta, 2/F',
        'phone': '+39011543287',
        'postal_code': '10121'
    },
    {
        'country': 'Italia',
        'city': 'Napoli', 
        'address': 'Via Nuova, 184',
        'phone': '+390815520644',
        'postal_code': '80040'
    },
    {
        'country': 'Italia',
        'city': 'Palermo',
        'address': 'Via Gaspare Palermo, 1',
        'phone': '+390916119419',
        'postal_code': '90127'
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

def get_total_price():
    # Extract the total price - Basket
    try:
        price_text = driver.find_element(By.CLASS_NAME, 'cart-panel__result-price').text
        price = extract_price(price_text)
        if price is not None:
            return price               
             
        print("Could not find total price on page")
        return None
        
    except Exception as e:
        print(f"Error extracting price: {str(e)}")
        return None

def close_cookie_popup():
    # Close the cookie consent popup if present
    try:
        accept_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".cky-btn.cky-btn-accept"))
                )
        accept_button.click()
        print("✓ Cookie popup closed")
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
        search_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="erca"]')))
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
            EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), 'SKU {sku}')]"))
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
        take_screenshot("after_api_add_to_cart")
        
        print("API call completed successfully")
        return True
        
    except Exception as e:
        print(f"Failed to add to cart via API: {str(e)}")
        take_screenshot("api_add_error")
        return False

def navigate_to_cart_directly():
    # Navigate to the cart page directly by URL
    try:
        print("Navigating to cart directly...")
        
        # Use the correct cart URL
        cart_url = "https://it.ermenrich.com/basket/"
        print(f"Navigating to cart URL: {cart_url}")
        
        driver.get(cart_url)
        time.sleep(3)
        take_screenshot("cart_page")
        
        # Check if we're on a cart page
        current_url = driver.current_url.lower()
        if "basket" in current_url:
            print("Successfully navigated to basket page")
            return True
        else:
            print(f"Not on basket page. Current URL: {driver.current_url}")
            return False
        
    except Exception as e:
        print(f"Failed to navigate to cart: {str(e)}")
        take_screenshot("cart_navigation_error")
        return False

def check_cart_contents(sku):
    # Check if the cart has our specific item
    print("Checking cart contents...")
    try:
        sku_element = driver.find_element(By.XPATH, f"//*[contains(text(), 'SKU: {sku}')]")
        print(f"Found our item in cart: {sku_element.text}")
        take_screenshot("cart_with_our_item")
        return True
            
    except Exception as e:
        print(f"Error checking cart contents: {str(e)}")
        take_screenshot("cart_check_error")
        return False

def proceed_to_checkout():
    # Click the checkout button and verify redirection Basket > Order page
    try:
        print("Looking for checkout button...")
        checkout_button = driver.find_element(By.XPATH, f"//*[contains(text(), 'Per controllare')]")
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

def select_drlivery_option():
    try:
        print("Selecting delivery option...")

        # Define delivery options with their corresponding IDs (equal probability)
        delivery_options = {
            "Consegna standard (standard courier)": "ID_SHIPPING_METHOD_ID_11",
            "Consegna espressa con corriere (express courier)": "ID_SHIPPING_METHOD_ID_10", # Add 10EU to the total
        }

        # Randomly select any delivery option
        selected_option_name = random.choice(list(delivery_options.keys()))
        selected_option_id = delivery_options[selected_option_name]

        print(f"Selected delivery option: {selected_option_name} (ID: {selected_option_id})")

        # Only interact with the UI if it's not the default option
        if selected_option_name != "Consegna standard (standard courier)":
            
            # Find and click the payment option using its ID
            try:
                # Find and click the label of the payment option
                delivery_label = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f"label[for='{selected_option_id}']"))
                )
                print("Found delivery label, attempting to click...")

                # Scroll to the label
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", delivery_label)
                time.sleep(0.5)

                # Click the label
                delivery_label.click()
                time.sleep(1)

                # Verify the option was selected by checking the input
                delivery_input = driver.find_element(By.ID, selected_option_id)
                if delivery_input.is_selected():
                    clean_option_name = selected_option_name.lower().replace(' ', '_').replace('\\', '_')
                    take_screenshot(f"selected_{clean_option_name}")
                    print(f"Successfully selected {selected_option_name} delivery option")
                    return True

                else:
                    print("Label click didn't change selection state")
                    # Fallback to JavaScript click if needed
                    driver.execute_script("arguments[0].click();", delivery_input)
                    time.sleep(1)
                    if delivery_input.is_selected():
                        print("Successfully selected using JavaScript fallback")
                        return True
                    return False

            except Exception as e:
                    print(f"Failed to select delivery option {selected_option_name}: {str(e)}")
                    return False
        else:
                print("Using default delivery option (Standard courier), no action needed")
                return True

    except Exception as e:
            print(f"Error in delivery selection process: {str(e)}")
            take_screenshot("delivery_option_error")
            return False

def select_payment_option():
    # Randomly select a payment option for orders over 70€ using element IDs
    try:
        print("Selecting payment option...")
        
        # Define payment options with their corresponding IDs (equal probability)
        payment_options = {
            "Bonifico bancario (bank transfer)": "ID_PAY_SYSTEM_ID_19",
            "In contanti alla consegna (cash on delivery)": "ID_PAY_SYSTEM_ID_17", # Add 3EU to the total
            "PayPal": "ID_PAY_SYSTEM_ID_18"
        }

        # Randomly select any payment option
        selected_option_name = random.choice(list(payment_options.keys()))
        selected_option_id = payment_options[selected_option_name]
        
        print(f"Selected payment option: {selected_option_name} (ID: {selected_option_id})")

        # Only interact with the UI if it's not the default option
        if selected_option_name != "Bonifico bancario (bank transfer)":
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

                # Verify the option was selected by checking the input
                payment_input = driver.find_element(By.ID, selected_option_id)
                if payment_input.is_selected():
                    clean_option_name = selected_option_name.lower().replace(' ', '_').replace('\\', '_')
                    take_screenshot(f"selected_{clean_option_name}")
                    print(f"Successfully selected {selected_option_name} payment option")
                    return True

                else:
                    print("Label click didn't change selection state")
                    # Fallback to JavaScript click if needed
                    driver.execute_script("arguments[0].click();", payment_input)
                    time.sleep(1)
                    if payment_input.is_selected():
                        print("Successfully selected using JavaScript fallback")
                        return True
                    return False

            except Exception as e:
                    print(f"Failed to select payment option {selected_option_name}: {str(e)}")
                    return False
        else:
                print("Using default payment option (Bank transfer), no action needed")
                return True

    except Exception as e:
            print(f"Error in payment selection process: {str(e)}")
            take_screenshot("payment_option_error")
            return False

# Create a simple step counter class
class StepCounter:
    def __init__(self):
        self.step = 1
    
    def print_step(self, message):
        print(f"\n--- Step {self.step}: {message} ---")
        self.step += 1


def fill_order_form():
    # Fill the order form
    try:

        ship_to = choose_address() #is a dictionary
        print(f"Chosen address in: {str(ship_to['country'])}")
        
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
            select_drlivery_option()

        except Exception as e:
            print(f"Could not check delivery options: {str(e)}")
        
        take_screenshot("order_form_filled")
        print("Order form filled successfully")
        return True
        
    except Exception as e:
        print(f"Error filling order form: {str(e)}")
        take_screenshot("order_form_error")
        return False

def get_order_number():
    # Extract the order number from the confirmation page
    try:
        print("Extracting order number from confirmation page...")
        
        # Wait for the order confirmation elements to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'ERM-') or contains(text(), 'T-ERM-')]"))
        )
        
        # Look for order number in various places on the page
        order_number = None
        
        # Try to find order number in headings or special elements
        try:
            order_elements = driver.find_elements(By.XPATH, "//h1[contains(text(), 'ERM-')] | //h2[contains(text(), 'ERM-')] | //strong[contains(text(), 'ERM-')] | //span[contains(text(), 'ERM-')]")
            for element in order_elements:
                text = element.text
                # Use regex to find the order number pattern
                match = re.search(r'(T-)?ERM-[A-Z]+-\d+', text)
                if match:
                    order_number = match.group()
                    break
        except:
            pass
        
        # If not found in specific elements, search the entire page - SEE IF WE NEED IT
        if not order_number:
            page_text = driver.page_source
            match = re.search(r'(T-)?ERM-[A-Z]+-\d+', page_text)
            if match:
                order_number = match.group()
        
        if order_number:
            return order_number
        else:
            return None
            
    except Exception as e:
        print(f"Error extracting order number: {str(e)}")
        take_screenshot("order_number_error")
        return None

def place_order():
    # Finalize the order by clicking the checkout button on the order form
    try:
        print("Placing order...")
        
        # Find and click the checkout button on the order form
        checkout_button = wait.until(EC.element_to_be_clickable(
            (By.ID, "submit")
        ))
        
        # Scroll to button if needed
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkout_button)
        time.sleep(1)
        
        take_screenshot("before_order_placement")
        
        # Click the button to place order
        checkout_button.click()
        
        # Wait for order confirmation
        print("Waiting for order confirmation...")
        try:
            # Wait for either order confirmation page or success message
            WebDriverWait(driver, 30).until(
                lambda d: d.find_elements(By.XPATH, "//*[contains(text(), 'correttamente')]")
            )
            
            take_screenshot("order_confirmation")
            
            # Get the order number
            order_number = get_order_number()
            source = "C:/Users/your_folder/screenshots"
            dest = f"C:/Users/your_folder/{order_number}"
            try:
                os.rename(source, dest)
            except OSError as error:
                print(error)
            
            return order_number
            
        except Exception as e:
            print(f"Order may have been placed but confirmation not detected: {str(e)}")
            take_screenshot("possible_order_confirmation")
            
            # Try to get order number anyway
            order_number = get_order_number()
            return order_number if order_number else True
            
    except Exception as e:
        print(f"Error placing order: {str(e)}")
        take_screenshot("order_placement_error")
        return False


# Main execution
if __name__ == "__main__":
    try:
        # Initialize step counter
        step_counter = StepCounter()
        print("Running IT script")
        print("----------LOGS FOR NERDS----------")
        
        sku = choose_sku()
        print(f"Chosen SKU: {str(sku)}")
        
        step_counter.print_step("Searching for SKU")
        
        if search_for_sku(sku):
            step_counter.print_step("Getting offer ID")
            offer_id = get_offer_id_for_sku(sku)
            
            if offer_id:
                step_counter.print_step("Adding to cart via API")
                
                if add_to_cart_via_api(offer_id, 1):
                    step_counter.print_step("Refreshing page to synchronize UI")
                    driver.refresh()
                    time.sleep(3)
                    take_screenshot("after_refresh")
                    step_counter.print_step("Navigating to cart")
                    
                    if navigate_to_cart_directly():
                        step_counter.print_step("Checking cart contents")
                        if check_cart_contents(sku):
                            step_counter.print_step("Getting basket total price")
                            basket_price = get_total_price()
                            
                            if basket_price is not None:
                                print(f"Basket total price: {basket_price}")
                                take_screenshot("basket_with_price")
                                
                                step_counter.print_step("Proceeding to checkout")
                                if proceed_to_checkout():
                                    step_counter.print_step("Getting order page total price")
                                    order_price = get_total_price()
                                    
                                    if order_price is not None:
                                        print(f"Order page total price: {order_price}")
                                        take_screenshot("order_with_price")
                                        
                                        # Compare prices
                                        if abs(basket_price - order_price) < 0.01:  # Account for floating point precision
                                            print("✅ SUCCESS: Prices match between basket and order pages!")
                                            print(f"✅ Total price: {order_price}")

                                            if fill_order_form():
                                                # Check if order value is over 70€ and select payment option if needed

                                                if order_price >= 70:
                                                    step_counter.print_step("Selecting payment option")
                                                    payment_success = select_payment_option()
                                                    if not payment_success:
                                                        print("⚠️ Payment selection failed, but continuing with order process")

                                                else:
                                                    print("Order value below 70€, using default payment option")

                                                step_counter.print_step("Placing order")
                                                order_result = place_order()

                                                if order_result:
                                                    if isinstance(order_result, str):
                                                        print(f"✅ Order successfully placed! Order number: {order_result}")
                                                    else:
                                                        print("✅ Order successfully placed!")
                                                    print("Please check your email and 1C system for order confirmation")                                                   

                                                else:
                                                    print("❌ Failed to place order")                                                

                                            else:
                                                print("❌ Failed to fill order form") 
                                            
                                        else:
                                            print(f"❌ WARNING: Prices don't match! Basket: {basket_price}, Order: {order_price}")
                                                                                       
                                    else:
                                        print("❌ Could not extract price from order page")
                                else:
                                    print("\n❌ Failed to proceed to checkout")
                            else:
                                print("\n❌ Could not extract price from basket page")
                        else:
                            print("\n❌ Item was added but not found in cart")
                    else:
                        print("\n❌ Failed to navigate to cart")
                else:
                    print("\n❌ Failed to add item to cart via API")
            else:
                print("\n❌ Could not find offer ID for the product")
        else:
            print("\n❌ Failed to search for SKU")
        
        print("\nProcess completed. Browser will close in 10 seconds.")
        print("----------ORDER INFO----------")
        print(f"Order number: {order_result}")
        print(f"Chosen SKU: {str(sku)}, total price: {order_price}")
        #print(f"Selected delivery option: {selected_option_name}")
        #print(f"Selected payment option: {selected_option_name}")
        print("----------END----------")
        time.sleep(10)
        
    except Exception as e:
        print(f"\n❌ Script failed with error: {str(e)}")
        take_screenshot("main_script_error")          
   
    finally:
        driver.quit()

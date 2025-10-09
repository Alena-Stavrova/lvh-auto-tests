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
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://bg.ermenrich.com/")


# Choose random sku
def choose_sku():
    #The first 5 are below 70€, the last 5 are 70€ or more
    skus = [83836, 83820, 84547, 84545, 83089, 84558, 84638, 84087, 83842, 85574]
    sku_num = random.randint(0,9)
    sku = skus[sku_num]
    return sku

def choose_address():
    # Define a list of shipping addresses
    shipping_addresses = [
    {
        'country': 'България',
        'city': 'София',
        'address': 'кв. Орландовци, ул. „Свобода“ 15',
        'phone': '+35928657275',
        'postal_code': '1225'
    },
    {
        'country': 'България',
        'city': 'Пловдив', 
        'address': 'Каменица 2Източен, бул. „Източен“ 40',
        'phone': '+35932676710',
        'postal_code': '4017'
    },
    {
        'country': 'България',
        'city': 'Варна',
        'address': 'Варна ЦентърПриморски, ул. „Генерал Столетов“ 68',
        'phone': '+35952607219',
        'postal_code': '9002'
    }]
    address_num = random.randint(0,2)
    return(shipping_addresses[address_num]) # Returns a dict


def take_screenshot(name):
    # Helper function to take screenshots for debugging
    mydir = "C:/Users/astavrova/Desktop/Алена (врем.)/разное/программизм/автоматизация_2.0/find item and add to cart/"
    if not os.path.exists(mydir + "screenshots"):
        os.makedirs(mydir + "screenshots")
    driver.save_screenshot(mydir + "screenshots" / name)

    
take_screenshot("main page.png")
    
"""
def extract_price(price_text):
    Extract numeric price from text

    
    except ValueError:
        return None

def get_total_price():
    Extract the total price - Basket
    
        
    except Exception as e:
        print(f"Error extracting price: {str(e)}")
        return None

def search_for_sku(sku):
    Search for a specific SKU on the website
    try:
        
        
    except Exception as e:
        print(f"Search failed: {str(e)}")
        take_screenshot("search_error")
        return False

def get_offer_id_for_sku(sku):
    Extract the offerId for the product with the given SKU
    try:
        
        
    except Exception as e:
        print(f"Failed to get offer ID: {str(e)}")
        take_screenshot("offer_id_error")
        return None

def add_to_cart_via_api(offer_id, quantity=1):
    Add item to cart using the direct API call
    try:
        print("Adding item to cart via API...")
        
        # Execute JavaScript to make the API call
        script = f
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
    Navigate to the cart page directly by URL
    try:
        
        
    except Exception as e:
        print(f"Failed to navigate to cart: {str(e)}")
        take_screenshot("cart_navigation_error")
        return False

def check_cart_contents(sku):
    Check if the cart has our specific item
    print("Checking cart contents...")
    try:
        
            
    except Exception as e:
        print(f"Error checking cart contents: {str(e)}")
        take_screenshot("cart_check_error")
        return False

def proceed_to_checkout():
    Click the checkout button and verify redirection to order page
    try:
        
        
    except Exception as e:
        print(f"Failed to proceed to checkout: {str(e)}")
        take_screenshot("checkout_error")
        return False


def select_payment_option():
    Randomly select a payment option for orders over 70€ using element IDs
    try:
        print("Selecting payment option...")
        
        # Define payment options with their corresponding IDs (equal probability)
        

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
    Fill the order form
    try:

        
        
    except Exception as e:
        print(f"Error filling order form: {str(e)}")
        take_screenshot("order_form_error")
        return False

def get_order_number():
    Extract the order number from the confirmation page
    try:
        print("Extracting order number from confirmation page...")
        
        # Wait for the order confirmation elements to load
        
        except:
            pass
        
        # If not found in specific elements, search the entire page - SEE IF WE NEED IT
        
            
    except Exception as e:
        print(f"Error extracting order number: {str(e)}")
        take_screenshot("order_number_error")
        return None

def place_order():
    Finalize the order by clicking the checkout button on the order form
    try:
        print("Placing order...")
        
        # Find and click the checkout button on the order form
        
            
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


def proceed_to_checkout():
    Click the checkout button and verify redirection to order page
    try:
        print("Looking for checkout button...")
        
    except Exception as e:
        print(f"Failed to proceed to checkout: {str(e)}")
        take_screenshot("checkout_error")
        return False

# Main execution
if __name__ == "__main__":
    try:
        # Initialize step counter
        
        
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
        time.sleep(10)
        
    except Exception as e:
        print(f"\n❌ Script failed with error: {str(e)}")
        take_screenshot("main_script_error")          
   
    finally:
        driver.quit()
"""

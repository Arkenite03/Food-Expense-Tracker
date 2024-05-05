import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import os

orders = []
swiggy_orders = []
count = 0

def get_swiggy(soup):

    # Take Amount of Order from this class
    # <span class="_1jGfr"> 289 </span>

    # Take Date of Order from this class
    # <div class="_2fkm7"><span>Delivered on Sat, Apr 27, 2024, 12:40 AM<span class="h-Ntp icon-tickSharp"></span></span></div>

    # Take Name of Order from this class
    # <div class="_33I3_">Chocolate Ice Cream Jar Cake x 1</div>


    # Take Name and Location of Restaurant from this class
    # <div class="_3h4gz">Cakezyy</div>
    # <div class="_2haEe">Marathahalli</div>

    # Extract order details
    
    global swiggy_orders, count
    
    order_elements = soup.find_all("div", class_="_33I3_")
    restaurant_elements = soup.find_all("div", class_="_3h4gz")
    location_elements = soup.find_all("div", class_="_2haEe")
    amount_elements = soup.find_all("span", class_="_1jGfr")
    date_elements = soup.find_all("div", class_="_2fkm7")
    
    for i in range(10 * count, len(order_elements)):
        date_text = date_elements[i].text.strip().split(": ")[-1]
        date = pd.to_datetime(date_text, format='Delivered on %a, %b %d, %Y, %I:%M %p')
        time = date.strftime('%H:%M')
        order = {
            "name": order_elements[i].text.strip(),
            "restaurant": restaurant_elements[i].text.strip(),
            "location": location_elements[i].text.strip(),
            "amount": amount_elements[i].text.strip(),
            "date": date.strftime('%Y-%m-%d'),
            "time": time
        }
        swiggy_orders.append(order)
    
    count += 1
    

def get_zomato2(soup):
    
# <div class="sc-kqEXUp jJNbJu">
#     <div class="sc-gneEKw hxhsEY">
#         <p class="sc-bXopBW hVyhyV">Order Number</p>
#         <p class="sc-hhaNoI ejeifz">5774885092</p>
#     </div>
#     <div class="sc-gneEKw hxhsEY">
#         <p class="sc-bXopBW hVyhyV">Total Amount</p>
#         <p class="sc-hhaNoI ejeifz">₹152.22</p>
#     </div>
#     <div class="sc-gneEKw hxhsEY">
#         <p class="sc-bXopBW hVyhyV">Items</p>
#         <p class="sc-hhaNoI ejeifz">1 x Chilli Potato</p>
#     </div>
#     <div class="sc-gneEKw hxhsEY">
#         <p class="sc-bXopBW hVyhyV">Ordered on</p>
#         <p class="sc-hhaNoI ejeifz">April 28, 2024 at 04:48 PM</p>
#     </div>
# </div>


    # Instead of searching for the class name, search for the next p tag negihbor of 
    #     1. p tag with text "Order Number"
    #     2. p tag with text "Total Amount"
    #     3. p tag with text "Items"
    #     4. p tag with text "Ordered on" 
    #        there will be multiple p tags with the same text, so club 1st occurance of each type together and store
    #        ex. 1st occurance of "Order Number" with 1st occurance of "Total Amount" and so on

    global orders
    
    order_number_elements = soup.find_all("p", text="Order Number")
    order_number_values = [order_number_element.find_next("p").text for order_number_element in order_number_elements]
    # print("order_number_values", order_number_values)
    
    amount_elements = soup.find_all("p", text="Total Amount")
    amount_values = [amount_element.find_next("p").text for amount_element in amount_elements]
    # print("amount_values", amount_values)
    
    item_elements = soup.find_all("p", text="Items")
    item_values = [item_element.find_next("p").text for item_element in item_elements]
    # print("item_values", item_values)
    
    date_elements = soup.find_all("p", text="Ordered on")
    date_values = [date_element.find_next("p").text for date_element in date_elements]
    # print("date_values", date_values)
    
    # # Create a list of dictionaries for each order
    for i in range(len(order_number_values)):
        order = {
            "order_number": order_number_values[i],
            "amount": amount_values[i],
            "item": item_values[i],
            "date": date_values[i]
        }
        orders.append(order)


def find_show_more_button(driver):
    
    # Outer HTML - <div class="_3eCKY">Show More Orders</div>

    global swiggy_orders, count
    try:
        show_more_button = driver.find_element(By.XPATH, '//div[text()="Show More Orders"]')
        print("show_more_button", show_more_button)
        print("show_more_button.text", show_more_button.text)
        if show_more_button and show_more_button.text == 'SHOW MORE ORDERS':
            show_more_button.click()
            time.sleep(5)
            return True
        else:
            print("Show more button not found.")
            return False

        
    except NoSuchElementException:
        print("Show more button not found.")
        return False
    
    
def find_and_click_next_button(driver, soup):
    
    global orders
    
    next_button = soup.find(lambda tag: (
        tag.name == 'a' and
        tag.find('svg') and
        tag.find('title') and
        tag.find('title').text == 'chevron-right'
    ))
    
    if next_button:
        print(next_button)
        # Extract the attributes of the BeautifulSoup element
        href = next_button.get('href', '')  # Obtain the href attribute
        class_list = next_button.get('class', [])  # Obtain the class attribute as a list

        # Construct an XPath expression using the attributes
        # Normalize space in the class attribute to account for possible variations in class order
        class_string = ' '.join(class_list)
        xpath_expression = f'//a[@href="{href}" and normalize-space(@class)="{class_string}"]'

       # Find the element using Selenium and click it
        selenium_element = driver.find_element(By.XPATH, xpath_expression)
        selenium_element.click()
        
        time.sleep(5)  # Allow time for the
        return True
    
    else:
        print("Next button not found.")
        return False
   

def zomato_expense_tracker(driver):
    
    global orders
    
    # URL of Swiggy account orders page
    zomato_orders_url = "https://www.zomato.com/users/vishwa-sharma-37028572/ordering"

    # driver.get(zomato_orders_url)
    # time.sleep(35)  # Allow time for the page to load

    driver.get(zomato_orders_url)
    time.sleep(3)  # Allow time for the page to load
    # Scrape order history

    while True:
        # Process the current page
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        get_zomato2(soup)

        if not find_and_click_next_button(driver, soup):
            break


    df = pd.DataFrame(orders)
    # convert amount string to float

    df['amount'] = df['amount'].str.replace('₹', '')
    df['amount'] = df['amount'].str.replace(',', '')
    df['amount'] = df['amount'].astype(float)

    # 1. total amount till now
    # 2. monthly total amount
    # 3. monthly total orders

    # 1. total amount till now
    total_amount = df["amount"].sum()
    print("Total Amount: ", total_amount)

    # 2. monthly total amount

    # Extract the month and year from the date
    # format - May 04, 2024 at 05:13 PM
    df['date'] = pd.to_datetime(df['date'], format='%B %d, %Y at %I:%M %p')
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year

    # Calculate the monthly total amount
    monthly_total_amount = df.groupby(['year', 'month'])['amount'].sum()

    print(monthly_total_amount)

    # 3. monthly total orders

    monthly_total_orders = df.groupby(['year', 'month']).size()

    print(monthly_total_orders)
    
    
    # Delete the files if they already exist
    if os.path.exists('/Users/vishwsh2/Projects/Food Expense tracker/zomato_orders.xlsx'):
        os.remove('/Users/vishwsh2/Projects/Food Expense tracker/zomato_orders.xlsx')
    if os.path.exists('/Users/vishwsh2/Projects/Food Expense tracker/zomato_monthly_total_amount.xlsx'):
        os.remove('/Users/vishwsh2/Projects/Food Expense tracker/zomato_monthly_total_amount.xlsx')
    if os.path.exists('/Users/vishwsh2/Projects/Food Expense tracker/zomato_monthly_total_orders.xlsx'):
        os.remove('/Users/vishwsh2/Projects/Food Expense tracker/zomato_monthly_total_orders.xlsx')

    df.to_excel('/Users/vishwsh2/Projects/Food Expense tracker/zomato_orders.xlsx', index=False)
    monthly_total_amount.to_excel('/Users/vishwsh2/Projects/Food Expense tracker/zomato_monthly_total_amount.xlsx', index=True)
    monthly_total_orders.to_excel('/Users/vishwsh2/Projects/Food Expense tracker/zomato_monthly_total_orders.xlsx', index=True)


def swiggy_expense_tracker(driver):
    
    global swiggy_orders, count
    swiggy_orders_url = "https://www.swiggy.com/my-account/orders"
    # driver.get(swiggy_orders_url)
    # time.sleep(35)  # Allow time for the page to load

    driver.get(swiggy_orders_url)
    time.sleep(5)  # Allow time for the page to load
    
    while True:
        # Process the current page
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        get_swiggy(soup)
        
        if not find_show_more_button(driver):
            break
        
    df = pd.DataFrame(swiggy_orders)
    print(df)
    
    # 1. total amount till now
    # 2. monthly total amount
    # 3. monthly total orders
    
    # 1. total amount till now
    
    # convert amount string to float
    df['amount'] = df['amount'].astype(float)
    total_amount = df["amount"].sum()
    print("Total Amount: ", total_amount)
    
    # 2. monthly total amount
    
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    
    
    # Delete the file if it already exists
    if os.path.exists('/Users/vishwsh2/Projects/Food Expense tracker/swiggy_orders.xlsx'):
        os.remove('/Users/vishwsh2/Projects/Food Expense tracker/swiggy_orders.xlsx')
    if os.path.exists('/Users/vishwsh2/Projects/Food Expense tracker/swiggy_monthly_total_amount.xlsx'):
        os.remove('/Users/vishwsh2/Projects/Food Expense tracker/swiggy_monthly_total_amount.xlsx')
    if os.path.exists('/Users/vishwsh2/Projects/Food Expense tracker/swiggy_monthly_total_orders.xlsx'):
        os.remove('/Users/vishwsh2/Projects/Food Expense tracker/swiggy_monthly_total_orders.xlsx')
    
    df.to_excel('/Users/vishwsh2/Projects/Food Expense tracker/swiggy_orders.xlsx', index=False)
    monthly_total_amount = df.groupby(['year', 'month'])['amount'].sum()
    monthly_total_amount.to_excel('/Users/vishwsh2/Projects/Food Expense tracker/swiggy_monthly_total_amount.xlsx')
    print(type(monthly_total_amount))
    
    # 3. monthly total orders
    
    monthly_total_orders = df.groupby(['year', 'month']).size()
    monthly_total_orders.to_excel('/Users/vishwsh2/Projects/Food Expense tracker/swiggy_monthly_total_orders.xlsx')
    print(monthly_total_orders)
    

if __name__ == "__main__":
    # Configure Selenium and the Chrome WebDriver
    options = Options()
    options.add_argument('--user-data-dir=/Users/vishwsh2/Library/Application Support/Google/Chrome/')
    options.add_argument('--profile-directory=Default')
    # options.add_argument('--headless') 
    options.add_argument('--no-sandbox')

    # The WebDriver
    service=ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(options=options)

    swiggy_expense_tracker(driver)
    zomato_expense_tracker(driver)

    # Close the browser
    driver.quit()
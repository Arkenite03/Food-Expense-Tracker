# Food Expense Tracker

This script is used to track food expenses from Swiggy and Zomato orders. It uses Selenium and BeautifulSoup libraries to scrape order details from the respective websites and saves the data in Excel files.

## Prerequisites

- Python 3.x
- Chrome browser
- Chrome WebDriver

## Installation

1. Clone the repository:

    ```shell
    git clone https://github.com/your-username/food-expense-tracker.git
    ```

2. Install the required Python packages:

    ```shell
    pip install -r requirements.txt
    ```

3. Download and install the Chrome WebDriver from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads).

4. Update the paths in the script:

    - Update the `zomato_orders_url` and `swiggy_orders_url` variables with your respective order history URLs.
    - Update the file paths for saving the Excel files in the `zomato_expense_tracker` and `swiggy_expense_tracker` functions.

## Usage

1. Run the script:

    ```shell
    python main.py
    ```

2. The script will open a Chrome browser window and start scraping the order details.

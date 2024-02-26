from playwright.sync_api import sync_playwright
import re
import pandas as pd
import datetime
import os
import warnings

def nepali_to_english_number(nepali_number):
    # Define mapping for Nepali numbers to English numbers
    nepali_digits = "०१२३४५६७८९"
    english_digits = "0123456789"
    nepali_to_english_map = str.maketrans(nepali_digits, english_digits)
    
    # Convert the Nepali number to English
    english_number = nepali_number.translate(nepali_to_english_map)
    
    return english_number


def main():
    # Suppress future deprecation warnings
    warnings.filterwarnings("ignore")

        # Get today's date
    today_date = datetime.date.today().strftime("%Y-%m-%d")
    df_min = pd.DataFrame(index=[today_date])
    df_max = pd.DataFrame(index=[today_date])
    df_avg = pd.DataFrame(index=[today_date])


    vegetable_names = []
    english_names = []
    nepali_names = []
    print("Accessing website in English...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://kalimatimarket.gov.np/')

        
        # Locate the image button using XPath
        image_button = page.locator('//div[3]/div/div/nav/ul/li[7]/a/img')
        image_button2 = page.locator('//div[3]/div/div/nav/ul/li[7]/ul/div/a')
        
        # Click the located image button
        image_button.click()
        image_button2.click()
        names = page.query_selector_all('//*[@id="commodityDailyPrice"]/tbody/tr')
        full_list = ''

        print("Retreiving data...")
        # Loop through the selected elements and collect their text
        for vegetable in names:
            name = vegetable.inner_text()
            full_list+= name + '\n'

        print("Organizing data...")    
        # Split the text into lines
        lines = full_list.strip().split('\n')

        # Initialize a list to store the results
        result_list = []

        # Define a regular expression pattern to extract the required information
        pattern = r'^(.*?)\s*Rs\s*(\d+)\s*Rs\s*(\d+)\s*Rs\s*(\d+\.\d+)'

        # Loop through each line and extract the information
        for line in lines:
            match = re.match(pattern, line)
            if match:
                name = match.group(1).strip()
                price1 = match.group(2).strip()
                price2 = match.group(3).strip()
                price3 = match.group(4).strip()
                result_list.append((name, price1, price2, price3))

        # Print the results
        for item in result_list:
            vegetable_names.append([item[0], item[1], item[2], item[3]])
            english_names.append(item[0])
            # print(f"{item[0]}, {item[1]}, {item[2]}, {item[3]}")

        browser.close()


    print("Accessing website in Nepali...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://kalimatimarket.gov.np/')
        names = page.query_selector_all('//*[@id="commodityDailyPrice"]/tbody/tr')
        full_list = ''

        print("Retreiving data...")
        # Loop through the selected elements and collect their text
        for vegetable in names:
            name = vegetable.inner_text()
            full_list+= name + '\n'
        # print(full_list)

        print("Organizing data...")    
        # Split the text into lines
        lines = full_list.strip().split('\n')

        # Initialize a list to store the results
        result_list = []

        # Define a regular expression pattern to extract the required information
        pattern = r'^(.*?)\s*रू\s*(\d+)\s*रू\s*(\d+)\s*रू\s*(\d+\.\d+)'

        # Loop through each line and extract the information
        for line in lines:
            match = re.match(pattern, line)
            if match:
                name = match.group(1).strip()
                price1 = match.group(2).strip()
                price2 = match.group(3).strip()
                price3 = match.group(4).strip()
                result_list.append((name, price1, price2, price3))

        # Print the results
        for item in result_list:
            nepali_names.append(item[0])
            # print(f"{item[0]}, {item[1]}, {item[2]}, {item[3]}")

        browser.close()
    print("preparing translation file...", len(english_names), len(nepali_names))

    # preparing language file
    max_length = max(len(english_names), len(nepali_names))
    if len(english_names) < max_length: # Pad the shorter list with None values to match the length of the longer list
        english_names += [None] * (max_length - len(english_names))
    if len(nepali_names) < max_length:
        nepali_names += [None] * (max_length - len(nepali_names))
    lang_df = pd.DataFrame({'English': english_names, 'Nepali': nepali_names})

    print("Preparing csv files...")
    for vegetable in vegetable_names:
        df_min.at[today_date, vegetable[0]] = vegetable[1]  # Update the price (use your actual price data)
        df_max.at[today_date, vegetable[0]] = vegetable[2]  # Update the price (use your actual price data)
        df_avg.at[today_date, vegetable[0]] = vegetable[3]  # Update the price (use your actual price data)


    min_location = '/Users/birajaryal/programming_gita/data_science/Min_vegetable_prices.csv'
    max_location = '/Users/birajaryal/programming_gita/data_science/Max_vegetable_prices.csv'
    avg_location = '/Users/birajaryal/programming_gita/data_science/Avg_vegetable_prices.csv'
    lang_location = '/Users/birajaryal/programming_gita/data_science/vegetableLanguage.csv'

    # saving data for the first time
    if not (os.path.isfile(min_location) and os.path.isfile(max_location) and os.path.isfile(avg_location)):
        print("Original prices files not found...")
        df_min.to_csv("Min_vegetable_prices.csv")  # Save to a CSV file
        df_max.to_csv("Max_vegetable_prices.csv")  # Save to a CSV file
        df_avg.to_csv("Avg_vegetable_prices.csv")  # Save to a CSV file

    # updating data
    else:
        print("Original prices files found...")
        old_df_min = pd.read_csv("Min_vegetable_prices.csv", index_col=0)
        old_df_max = pd.read_csv("Max_vegetable_prices.csv", index_col=0)
        old_df_avg = pd.read_csv("Avg_vegetable_prices.csv", index_col=0)
        result_df_min = pd.concat([old_df_min, df_min])
        result_df_max = pd.concat([old_df_max, df_max])
        result_df_avg = pd.concat([old_df_avg, df_avg])

        result_df_min.to_csv("Min_vegetable_prices.csv")
        result_df_max.to_csv("Max_vegetable_prices.csv")
        result_df_avg.to_csv("Avg_vegetable_prices.csv")


    if not os.path.isfile(lang_location):
        print("original lang file not found...")
        lang_df.to_csv("vegetableLanguage.csv")

    else: 
        print("original lang file found...")
        old_lang_df = pd.read_csv("vegetableLanguage.csv", index_col=0)
        result_df = pd.concat([old_lang_df, lang_df], ignore_index=True)
        result_df['Nepali'] = result_df.groupby('English')['Nepali'].transform('first') # Group the DataFrame by 'English' and fill each group with the non-null 'Nepali' value
        result_df = result_df.drop_duplicates(keep='first')
        result_df.to_csv("vegetableLanguage.csv")

    # Saving today's data
    print("Saving today's data...")
    lang_df = pd.read_csv("vegetableLanguage.csv", index_col=0)
    min_df_transposed = df_min.T
    max_df_transposed = df_max.T
    avg_df_transposed = df_avg.T

    lang_df.set_index('English', inplace=True)
    lang_df_reordered = lang_df.loc[min_df_transposed.index]
    combined_df = pd.concat([lang_df_reordered, min_df_transposed, max_df_transposed, avg_df_transposed], axis=1)
    combined_df.columns = ['Nepali', 'Min Price', 'Max Price', 'Avg Price']
    combined_df.to_csv(f"daily_prices/{today_date}.csv")
    print("All tasks completed.")

    

if __name__ == '__main__':
    main()
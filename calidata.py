# combined_script.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import openai  # Assuming you use OpenAI API
from apscheduler.schedulers.blocking import BlockingScheduler

# Set your OpenAI API key
openai.api_key = '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'

# Function to generate queries using OpenAI API
def generate_query(prompt):
    response = openai.Completion.create(
        engine="davinci",  # Replace with a supported engine
        prompt=prompt,
        max_tokens=150  # Adjust as needed
    )
    return response.choices[0].text.strip()


# Function to scrape data from a website
def scrape_website(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        # Send an HTTP request
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract relevant information based on the website structure
        # Modify this based on the actual HTML structure of the website
        project_names = [project.text for project in soup.select('.project-name')]
        project_dates = [date.text for date in soup.select('.project-date')]

        return project_names, project_dates

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
        print(f"URL: {url}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
        print(f"URL: {url}")

    return None

# Function for standardization
def standardize_data(project_names, project_dates):
    # Perform standardization as needed
    standardized_project_names = [name.upper() for name in project_names]
    standardized_project_dates = [date.replace('-', '/') for date in project_dates]

    return standardized_project_names, standardized_project_dates

# Main function for automation
def main():
    # List of real websites to scrape
    websites = [
        'http://books.toscrape.com',
        'http://quotes.toscrape.com',
        # Add more URLs if needed
    ]

    # Loop through the websites, scrape data, and concatenate into a single DataFrame
    data_frames = []
    for website in websites:
        prompt = f"Construction projects in California on {website}"
        query = generate_query(prompt)
        print(f"Generated query: {query}")

        scraped_data = scrape_website(website)
        
        if scraped_data is not None:
            project_names, project_dates = scraped_data
            standardized_names, standardized_dates = standardize_data(project_names, project_dates)

            # Create a DataFrame for the extracted data
            df = pd.DataFrame({'Project Name': standardized_names, 'Project Date': standardized_dates})
            data_frames.append(df)

    # Concatenate all DataFrames into a single DataFrame
    if data_frames:
        final_df = pd.concat(data_frames, ignore_index=True)

        # Check for missing values in the 'Project Name' column
        if final_df['Project Name'].isnull().any():
            print("Warning: There are missing values in the 'Project Name' column.")

        # Convert 'Project Name' column to string type
        final_df['Project Name'] = final_df['Project Name'].astype(str)

        # Save the standardized data to a CSV file
        final_df.to_csv('standardized_data.csv', index=False)
        print("Data updated successfully.")
    else:
        print("No data to concatenate.")

# Schedule the script to run every day at midnight
#scheduler = BlockingScheduler()
#scheduler.add_job(main, 'cron', hour=0, minute=0)
#scheduler.start()
#main()
        
main()



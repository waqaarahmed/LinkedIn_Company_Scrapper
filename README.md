# LinkedIn Company Follower Scraper

This project is a Python-based web scraper that extracts information about companies followed by a LinkedIn user.

## Prerequisites

- Python 3.7 or higher
- Chrome browser
- ChromeDriver (compatible with your Chrome version)

## Setup

1. Clone this repository:   ```
   git clone https://github.com/your-username/linkedin-company-scraper.git
   cd linkedin-company-scraper   ```

2. Create a virtual environment (optional but recommended):   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`   ```

3. Install the required packages:   ```
   pip install -r requirements.txt   ```

4. Update the `config.py` file with your LinkedIn credentials and the profile URL you want to scrape:   ```python
   EMAIL = "your_email@example.com"
   PASSWORD = "your_password"
   PROFILE_URL = "https://www.linkedin.com/in/your-profile-url/"   ```

## Usage

To run the scraper:

1. Make sure you're in the project directory and your virtual environment is activated (if you're using one).

2. Run the script:   ```
   python linkedin_api.py   ```

3. The script will log in to LinkedIn, navigate to the specified profile's interests page, and scrape information about followed companies.

4. The results will be saved in the `output` directory as both CSV and JSON files.

## Notes

- The script uses Selenium WebDriver to automate browser interactions. Make sure you have the correct ChromeDriver version installed and in your system PATH.
- LinkedIn's page structure may change over time. If the scraper stops working, you may need to update the CSS selectors in the `get_followed_companies` method.
- Be mindful of LinkedIn's terms of service and scraping policies. Excessive scraping may lead to account restrictions.

## Troubleshooting

- If you encounter any issues, check the `linkedin_scraping.log` file for error messages.
- Make sure your LinkedIn credentials in `config.py` are correct.
- If the script fails to find elements, try running it without the headless mode (comment out the headless option in the `setup_driver` method).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

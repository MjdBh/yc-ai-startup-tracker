# Y Combinator AI Startup Tracker

Automatically track AI startups introduced by Y Combinator on LinkedIn. This tool scrapes LinkedIn daily to find the latest AI startups backed by YC and updates this README with the findings.

## How It Works

1. A Python script uses Selenium to scrape LinkedIn for YC AI startups
2. GitHub Actions runs this script daily at 6:00 UTC
3. Results are automatically committed to this repository
4. The README is updated with the latest findings

## Latest AI Startups

This section will be automatically populated once the scraper runs for the first time.

## Setup Instructions

### 1. Fork this repository

Click the "Fork" button at the top right of this repository to create your own copy.

### 2. Configure LinkedIn credentials

To use this with your LinkedIn account, you need to set up two repository secrets:

1. Go to your forked repository
2. Navigate to "Settings" > "Secrets and variables" > "Actions"
3. Add the following secrets:
   - `LINKEDIN_USERNAME`: Your LinkedIn username/email
   - `LINKEDIN_PASSWORD`: Your LinkedIn password

### 3. Run the workflow manually (optional)

1. Go to the "Actions" tab
2. Select the "Daily YC AI Startup Scan" workflow
3. Click "Run workflow"

The workflow will also run automatically every day at 6:00 UTC.

## Customization

You can customize the script to search for different keywords or modify the output format:

1. Edit `scraper.py` to change the search criteria or output format
2. Modify `.github/workflows/daily-scan.yml` to change the schedule

## Running Locally

To run the script locally:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/yc-ai-startup-tracker.git
cd yc-ai-startup-tracker

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export LINKEDIN_USERNAME="your_linkedin_email"
export LINKEDIN_PASSWORD="your_linkedin_password"

# Run the script
python scraper.py
```

## Important Notes

- This tool is for educational purposes only
- Be respectful of LinkedIn's terms of service and rate limits
- Consider using a secondary LinkedIn account for this automation
- LinkedIn may block your account if they detect automated scraping

## Technical Implementation

- **Python**: Core scripting language
- **Selenium**: Web automation for LinkedIn interaction
- **GitHub Actions**: Scheduled automation
- **BeautifulSoup**: HTML parsing (auxiliary)

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

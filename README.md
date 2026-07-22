# Google Auto Form Filler

A Python + Selenium automation script that generates realistic Nepali/South 
Asian user profiles and automatically fills multi-page Google Forms.

## Overview

Built to automate survey data collection for a marketing research project. 
The script generates randomised but realistic demographic profiles and 
completes a Likert scale survey across seven marketing dimensions — all 
without manual input.

## Features

- Generates randomised Nepali/South Asian profiles (name, age, gender, 
  education, occupation, income, location)
- Automatically fills multi-page Google Forms with Likert scale grids
- Handles 7 marketing dimensions: Customer Acquisition, Social Media 
  Marketing, SEO, Content Marketing, Online Advertising, Email Marketing, 
  and Influencer Marketing
- Scores range 3–5 with human-like randomised delays between actions
- JavaScript-based click fallbacks for dynamic elements
- Handles stale DOM elements and dynamic page rendering automatically
- All submissions logged to `submissions_log.txt`

## Tech Stack

- Python
- Selenium WebDriver
- webdriver-manager (auto ChromeDriver management)
- Chrome

## Files

| File | Description |
|---|---|
| `fill_form.py` | Standard version with normal pacing |
| `fill_form_Fast.py` | Faster version for quicker bulk submissions |
| `submissions_log.txt` | Structured log of all completed submissions |
| `nav_snippets.txt` | Navigation helper snippets |

## Setup

```bash
git clone https://github.com/Prasidda14/Google-Auto-Form-Filler
cd Google-Auto-Form-Filler
pip install -r requirements.txt

# Update the Google Form URL in fill_form.py
# Then run:
python fill_form.py
```

## Note

This tool was built for legitimate research data collection. Always ensure 
you have permission before automating form submissions.

## Author

**Prasidda Khadka** · [LinkedIn](https://www.linkedin.com/in/prasidda-khadka/) · [GitHub](https://github.com/Prasidda14)

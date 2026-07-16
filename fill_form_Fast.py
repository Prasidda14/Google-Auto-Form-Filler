#!/usr/bin/env python3
"""
Faster might get flagged as a bot may trigger rate limits, CAPTCHAs, or other anti-abuse protections..
Automatically fill a two-page Google Form with randomized realistic data.
Run: python fill_form.py          (default: 300 submissions)
     python fill_form.py 50       (custom count)
"""

from __future__ import annotations

import random
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Dependency bootstrap
# ---------------------------------------------------------------------------

REQUIRED_PACKAGES = ("selenium", "webdriver-manager")


def ensure_dependencies() -> None:
    for package in REQUIRED_PACKAGES:
        module = package.replace("-", "_")
        try:
            __import__(module)
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )


ensure_dependencies()

from selenium import webdriver  # noqa: E402
from selenium.common.exceptions import (  # noqa: E402
    ElementClickInterceptedException,
    NoSuchElementException,
    InvalidSessionIdException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options  # noqa: E402
from selenium.webdriver.chrome.service import Service  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402
from webdriver_manager.chrome import ChromeDriverManager  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FORM_URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSeQLI6F2lofB4oNdK4x15Sji9Wc340Whret-d4jO8PSGjtnmw/viewform"
)

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE = SCRIPT_DIR / "submissions_log.txt"

FIRST_NAMES = [
    "Aarav", "Priya", "Suman", "Anita", "Rohan", "Kavya", "Niraj", "Sita",
    "Bikash", "Meera", "Arjun", "Pooja", "Dipesh", "Anjali", "Rajesh", "Sunita",
    "Kiran", "Sabina", "Prakash", "Rekha", "Gaurav", "Nisha", "Suresh", "Maya",
    "Bibek", "Ashmita", "Sandesh", "Ritu", "Manish", "Puja", "Amit", "Shristi",
]

LAST_NAMES = [
    "Sharma", "Thapa", "Gurung", "Rai", "Tamang", "Karki", "Maharjan", "Shrestha",
    "Adhikari", "Bhandari", "Poudel", "Khadka", "Basnet", "Lama", "Magar", "Chhetri",
    "Bhattarai", "Joshi", "Pandey", "Acharya", "Nepal", "Dahal", "Koirala", "Malla",
]

AGE_OPTIONS = ["18–25", "26–35", "36–45", "46 and above"]
GENDER_OPTIONS = ["Male", "Female"]
EDUCATION_OPTIONS = ["Secondary", "Bachelor's", "Master's and above"]
OCCUPATION_OPTIONS = ["Student", "Business Owner", "Employee", "Others"]
INCOME_OPTIONS = [
    "Below NPR 20,000",
    "NPR 20,000–50,000",
    "NPR 50,000–100,000",
    "Above NPR 100,000",
]
LOCATION_OPTIONS = ["Urban", "Semi-Urban", "Rural"]

SECTION_NAMES = [
    "CUSTOMER ACQUISITION (Instance 1)",
    "CUSTOMER ACQUISITION (Instance 2)",
    "SOCIAL MEDIA MARKETING",
    "SEO",
    "CONTENT MARKETING",
    "ONLINE ADVERTISING",
    "EMAIL MARKETING",
    "INFLUENCER MARKETING",
]

CA_LOG_LABELS = [
    "Q1 - Digital platform discovery",
    "Q2 - Digital marketing influence",
    "Q3 - Preference for online presence",
    "Q4 - Online promotions booking likelihood",
    "Q5 - Trust in digital marketing companies",
]

SMM_LOG_LABELS = [
    "Q1 - Discovery via social media",
    "Q2 - Influence of photos/videos",
    "Q3 - Reviews/comments trust",
    "Q4 - Social media ads attraction",
    "Q5 - Preference for active social media companies",
]

SEO_LOG_LABELS = [
    "Q1 - Using Google to find services",
    "Q2 - First-page trustworthiness",
    "Q3 - Higher-ranked sites influence",
    "Q4 - Likelihood to choose visible services",
    "Q5 - Comparing via search results",
]

CONTENT_LOG_LABELS = [
    "Q1 - Blogs/articles understanding",
    "Q2 - Portfolios influence",
    "Q3 - Informative content trust",
    "Q4 - Comparing via online content",
    "Q5 - Creative content attraction",
]

ADS_LOG_LABELS = [
    "Q1 - Online ads attention",
    "Q2 - Clicking event ads",
    "Q3 - Paid ads booking influence",
    "Q4 - Ad awareness",
    "Q5 - Usefulness of online ads",
]

EMAIL_LOG_LABELS = [
    "Q1 - Promotional emails inform",
    "Q2 - Email offers influence",
    "Q3 - Personalized emails interest",
    "Q4 - Encourage booking",
    "Q5 - Builds trust",
]

INFLUENCER_LOG_LABELS = [
    "Q1 - Influencers help discover",
    "Q2 - Trust in influencer recommendations",
    "Q3 - Influencer promotions interest",
    "Q4 - Influencers affect booking",
    "Q5 - Preference for endorsed services",
]

SECTION_LOG_LABELS = [
    CA_LOG_LABELS,
    CA_LOG_LABELS,
    SMM_LOG_LABELS,
    SEO_LOG_LABELS,
    CONTENT_LOG_LABELS,
    ADS_LOG_LABELS,
    EMAIL_LOG_LABELS,
    INFLUENCER_LOG_LABELS,
]

EXPECTED_GRID_COUNT = 8
ROWS_PER_GRID = 5
DEFAULT_SUBMISSION_COUNT = 30  #Number of submissions to be filled.
SHORT_WAIT = 6  
MEDIUM_WAIT = 15
LONG_WAIT = 25
MAX_CLICK_RETRIES = 3

# Reused locators to avoid repeated tuple creation/lookups.
FORM_LOCATOR = (By.CSS_SELECTOR, "form")
NAME_INPUT_LOCATOR = (By.CSS_SELECTOR, "input.whsOnd")
RADIOGROUP_LOCATOR = (By.CSS_SELECTOR, '[role="radiogroup"]')
RADIO_LOCATOR = (By.CSS_SELECTOR, '[role="radio"]')
NEXT_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'div[jsname="OCpkoe"]')
SUBMIT_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'div[jsname="M2UYVd"]')
CONFIRMATION_LOCATOR = (
    By.CSS_SELECTOR,
    ".freebirdFormviewerViewResponseConfirmationMessage, .HB1eCd-UMrnmb .TkVRWc",
)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class FormData:
    name: str
    age: str
    gender: str
    education: str
    occupation: str
    monthly_income: str
    location: str
    # 8 sections × 5 rows
    grid_ratings: list[list[int]] = field(default_factory=list)


def generate_form_data() -> FormData:
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    grids = [
        [random.randint(3, 5) for _ in range(ROWS_PER_GRID)]
        for _ in range(EXPECTED_GRID_COUNT)
    ]
    return FormData(
        name=f"{first} {last}",
        age=random.choice(AGE_OPTIONS),
        gender=random.choice(GENDER_OPTIONS),
        education=random.choice(EDUCATION_OPTIONS),
        occupation=random.choice(OCCUPATION_OPTIONS),
        monthly_income=random.choice(INCOME_OPTIONS),
        location=random.choice(LOCATION_OPTIONS),
        grid_ratings=grids,
    )


def print_summary_compact(data: FormData, index: int, total: int) -> None:
    print(
        f"[{index}/{total}] {data.name} | {data.age} | {data.gender} | "
        f"{data.education} | {data.occupation} | {data.monthly_income} | {data.location}"
    )


def print_summary(data: FormData) -> None:
    print("\n" + "=" * 60)
    print("GENERATED VALUES (pre-fill)")
    print("=" * 60)
    print(f"  NAME:             {data.name}")
    print(f"  AGE:              {data.age}")
    print(f"  GENDER:           {data.gender}")
    print(f"  EDUCATION LEVEL:  {data.education}")
    print(f"  OCCUPATION:       {data.occupation}")
    print(f"  MONTHLY INCOME:   {data.monthly_income}")
    print(f"  LOCATION:         {data.location}")
    print("\n  PAGE 2 RATINGS (3–5 per row):")
    for idx, (section, ratings) in enumerate(zip(SECTION_NAMES, data.grid_ratings)):
        print(f"\n  [{idx + 1}] {section}")
        for row_i, score in enumerate(ratings, start=1):
            print(f"      Row {row_i}: {score}")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Selenium helpers
# ---------------------------------------------------------------------------


def create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def safe_click(driver: webdriver.Chrome, element, max_retries: int = 3) -> None:
    last_error: Exception | None = None
    for _ in range(max_retries):
        try:
            # Only scroll when element is outside viewport.
            in_viewport = driver.execute_script(
                """
                const r = arguments[0].getBoundingClientRect();
                return r.top >= 0 && r.bottom <= (window.innerHeight || document.documentElement.clientHeight);
                """,
                element
            )
            if not in_viewport:
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
                    element,
                )

            # Click immediately once interactable.
            element.click()
            return
        except (StaleElementReferenceException, ElementClickInterceptedException) as exc:
            last_error = exc
            try:
                driver.execute_script("arguments[0].click();", element)
                return
            except (StaleElementReferenceException, ElementClickInterceptedException) as exc:
                last_error = exc
    if last_error:
        raise last_error


def find_radios_in_group(group) -> list:
    return group.find_elements(*RADIO_LOCATOR)


def click_radio_by_index(driver: webdriver.Chrome, radiogroup, index: int) -> None:
    for _ in range(MAX_CLICK_RETRIES):
        try:
            radios = find_radios_in_group(radiogroup)
            if index < 0 or index >= len(radios):
                raise IndexError(
                    f"Radio index {index} out of range (count={len(radios)})"
                )
            safe_click(driver, radios[index])
            return
        except StaleElementReferenceException:
            continue
    raise StaleElementReferenceException("Could not click radio by index")


def ensure_page2_rows_loaded(driver: webdriver.Chrome, expected_rows: int) -> None:
    """
    Fast path: do not scroll if all rows are already in DOM.
    Fallback: one shot scroll to bottom and wait for expected radiogroups.
    """
    groups = driver.find_elements(*RADIOGROUP_LOCATOR)
    if len(groups) >= expected_rows:
        return

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    WebDriverWait(driver, SHORT_WAIT).until(
        lambda d: len(d.find_elements(*RADIOGROUP_LOCATOR)) >= expected_rows
    )
    driver.execute_script("window.scrollTo(0, 0);")


def click_navigation_next(driver: webdriver.Chrome) -> None:
    """Next button (locale-independent jsname)."""
    wait = WebDriverWait(driver, MEDIUM_WAIT)
    btn = wait.until(EC.element_to_be_clickable(NEXT_BUTTON_LOCATOR))
    safe_click(driver, btn)
    # Wait until submit button from page 2 appears (transition complete).
    WebDriverWait(driver, LONG_WAIT).until(
        EC.presence_of_element_located(SUBMIT_BUTTON_LOCATOR)
    )


def click_navigation_submit(driver: webdriver.Chrome) -> None:
    """Submit button (locale-independent jsname)."""
    wait = WebDriverWait(driver, MEDIUM_WAIT)
    btn = wait.until(EC.element_to_be_clickable(SUBMIT_BUTTON_LOCATOR))
    safe_click(driver, btn)


def get_page1_radiogroups(driver: webdriver.Chrome) -> list:
    """Return radiogroups on page 1 in DOM order (Age through Location)."""
    wait = WebDriverWait(driver, LONG_WAIT)
    wait.until(EC.presence_of_element_located(RADIOGROUP_LOCATOR))
    groups = driver.find_elements(*RADIOGROUP_LOCATOR)
    # Page 1 has exactly 6 radiogroups before Next
    if len(groups) < 6:
        raise RuntimeError(f"Expected at least 6 radiogroups on page 1, found {len(groups)}")
    return groups[:6]


def fill_page1(driver: webdriver.Chrome, data: FormData) -> None:
    wait = WebDriverWait(driver, LONG_WAIT)
    wait.until(EC.presence_of_element_located(FORM_LOCATOR))

    # Name — short answer text field
    name_input = wait.until(EC.element_to_be_clickable(NAME_INPUT_LOCATOR))
    name_input.clear()
    name_input.send_keys(data.name)

    groups = get_page1_radiogroups(driver)
    page1_choices = [
        data.age,
        data.gender,
        data.education,
        data.occupation,
        data.monthly_income,
        data.location,
    ]
    page1_option_lists = [
        AGE_OPTIONS,
        GENDER_OPTIONS,
        EDUCATION_OPTIONS,
        OCCUPATION_OPTIONS,
        INCOME_OPTIONS,
        LOCATION_OPTIONS,
    ]

    for group, choice, options in zip(groups, page1_choices, page1_option_lists):
        idx = options.index(choice)
        click_radio_by_index(driver, group, idx)

    click_navigation_next(driver)


def find_likert_grids(driver: webdriver.Chrome) -> list[list[list]]:
    """
    Page 2 uses 40 radiogroups (8 sections × 5 rows), each with 5 scale radios.
    Returns grids in DOM order; each grid is 5 rows of 5 radio elements.
    """
    wait = WebDriverWait(driver, LONG_WAIT)
    wait.until(EC.presence_of_element_located(SUBMIT_BUTTON_LOCATOR))

    expected_rows = EXPECTED_GRID_COUNT * ROWS_PER_GRID
    ensure_page2_rows_loaded(driver, expected_rows)
    radiogroups = driver.find_elements(*RADIOGROUP_LOCATOR)
    visible = [rg for rg in radiogroups if rg.is_displayed()]
    if visible:
        radiogroups = visible

    if len(radiogroups) < expected_rows:
        raise RuntimeError(
            f"Expected {expected_rows} radiogroups on page 2, found {len(radiogroups)}"
        )

    radiogroups = radiogroups[:expected_rows]
    grids: list[list[list]] = []
    for section_start in range(0, expected_rows, ROWS_PER_GRID):
        section_rows: list[list] = []
        for rg in radiogroups[section_start : section_start + ROWS_PER_GRID]:
            radios = rg.find_elements(By.CSS_SELECTOR, '[role="radio"]')
            if len(radios) < 5:
                raise RuntimeError(
                    f"Row has {len(radios)} radios, expected at least 5"
                )
            section_rows.append(radios[:5])
        grids.append(section_rows)

    return grids


def fill_page2(driver: webdriver.Chrome, data: FormData) -> None:
    wait = WebDriverWait(driver, LONG_WAIT)
    wait.until(EC.presence_of_element_located(FORM_LOCATOR))

    grids = find_likert_grids(driver)

    for section_idx, (grid_rows, section_scores) in enumerate(
        zip(grids, data.grid_ratings)
    ):
        for row_idx, (row_radios, score) in enumerate(
            zip(grid_rows, section_scores)
        ):
            col_index = score - 1  # scores 3–5 → columns 2–4
            for _ in range(MAX_CLICK_RETRIES):
                try:
                    if col_index < len(row_radios):
                        safe_click(driver, row_radios[col_index])
                    else:
                        raise IndexError(
                            f"Column {col_index} missing in row {row_idx + 1}"
                        )
                    break
                except StaleElementReferenceException:
                    # Re-fetch once stale to keep reliability with dynamic DOM updates.
                    grids = find_likert_grids(driver)
                    row_radios = grids[section_idx][row_idx]

    click_navigation_submit(driver)


def wait_for_confirmation(driver: webdriver.Chrome, timeout: int = 30) -> bool:
    wait = WebDriverWait(driver, timeout)
    try:
        # Wait-driven confirmation check avoids polling sleeps.
        wait.until(
            lambda d: (
                "formresponse" in d.current_url.lower()
                or len(d.find_elements(*CONFIRMATION_LOCATOR)) > 0
                or "response has been recorded" in d.find_element(By.TAG_NAME, "body").text.lower()
                or "thank you" in d.find_element(By.TAG_NAME, "body").text.lower()
            )
        )
        return True
    except TimeoutException:
        return False


def next_submission_number() -> int:
    if not LOG_FILE.exists():
        return 1
    content = LOG_FILE.read_text(encoding="utf-8")
    return content.count("SUBMISSION #") + 1


def append_submission_log(data: FormData, submission_num: int) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = [
        "==================================================",
        f"SUBMISSION #{submission_num} — {timestamp}",
        "==================================================",
        f"NAME: {data.name}",
        f"AGE: {data.age}",
        f"GENDER: {data.gender}",
        f"EDUCATION LEVEL: {data.education}",
        f"OCCUPATION: {data.occupation}",
        f"MONTHLY INCOME: {data.monthly_income}",
        f"LOCATION: {data.location}",
        "",
        "--- PAGE 2 RATINGS ---",
    ]

    section_titles = [
        "CUSTOMER ACQUISITION (Instance 1):",
        "CUSTOMER ACQUISITION (Instance 2):",
        "SOCIAL MEDIA MARKETING:",
        "SEO:",
        "CONTENT MARKETING:",
        "ONLINE ADVERTISING:",
        "EMAIL MARKETING:",
        "INFLUENCER MARKETING:",
    ]

    for title, labels, scores in zip(
        section_titles, SECTION_LOG_LABELS, data.grid_ratings
    ):
        lines.append(title)
        for label, score in zip(labels, scores):
            lines.append(f"  {label}: {score}")
        lines.append("")

    lines.append("==================================================")
    lines.append("")

    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def return_to_form(driver: webdriver.Chrome) -> None:
    """Load a fresh form for the next submission."""
    driver.get(FORM_URL)
    # Wait for both form shell and first input to be interactable for stable start.
    WebDriverWait(driver, LONG_WAIT).until(
        EC.presence_of_element_located(FORM_LOCATOR)
    )
    WebDriverWait(driver, LONG_WAIT).until(
        EC.element_to_be_clickable(NAME_INPUT_LOCATOR)
    )


def run_single_submission(
    driver: webdriver.Chrome, data: FormData, index: int, total: int
) -> bool:
    """Fill and submit one response. Returns True if confirmation detected."""
    print_summary_compact(data, index, total)
    fill_page1(driver, data)
    fill_page2(driver, data)
    return wait_for_confirmation(driver)


def parse_submission_count() -> int:
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
            if count < 1:
                raise ValueError
            return count
        except ValueError:
            print(f"Invalid count {sys.argv[1]!r}; using default {DEFAULT_SUBMISSION_COUNT}")
    return DEFAULT_SUBMISSION_COUNT


def main() -> int:
    # UTF-8 console output on Windows
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    total = parse_submission_count()
    print(f"\nStarting {total} submission(s) → {LOG_FILE}\n")

    driver = create_driver()
    succeeded = 0
    failed = 0

    try:
        print("Opening form...")
        return_to_form(driver)

        for i in range(1, total + 1):
            data = generate_form_data()
            try:
                if run_single_submission(driver, data, i, total):
                    num = next_submission_number()
                    append_submission_log(data, num)
                    succeeded += 1
                    print(f"  ✓ Logged as SUBMISSION #{num}")
                else:
                    failed += 1
                    print("  ✗ Confirmation not detected — not logged")
            except (
                TimeoutException,
                RuntimeError,
                NoSuchElementException,
                InvalidSessionIdException,
                WebDriverException,
            ) as exc:
                failed += 1
                print(f"  ✗ Error: {exc}")
                # If Chrome/Driver disconnects, restart the session and continue.
                msg = str(exc).lower()
                if isinstance(exc, InvalidSessionIdException) or "invalid session id" in msg or "disconnected" in msg:
                    print("  Restarting browser session after disconnect...")
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    driver = create_driver()
                    return_to_form(driver)

            if i < total:
                try:
                    return_to_form(driver)
                except TimeoutException:
                    print("  Reloading form after timeout...")
                    return_to_form(driver)

        print("\n" + "=" * 60)
        print(f"FINISHED: {succeeded}/{total} succeeded, {failed} failed")
        print(f"Log file: {LOG_FILE}")
        print("=" * 60)
        return 0 if failed == 0 else 1

    finally:
        print("Closing browser...")
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())

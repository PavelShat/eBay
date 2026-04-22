# eBay E2E Testing Framework

A robust automated testing framework for eBay built with Python and Playwright. This project follows the Page Object Model (POM) and Object-Oriented Programming (OOP) principles to ensure maintainability and scalability.

## 🏗 Architecture

The framework is structured as follows:
- **Pages**: Implements the Page Object Model. Each page class (e.g., `HomePage`, `SearchResultsPage`) inherits from `BasePage` and encapsulates page-specific locators and actions.
- **Tests**: Contains the test cases (using `pytest`) that orchestrate the page objects to perform end-to-end scenarios.
- **Data**: Externalized test data in JSON format (`data/test_data.json`) for data-driven testing.
- **Configuration**: Centralized configuration in `pytest.ini` and `conftest.py` for fixtures and environment settings.
- **Reporting**: Integrated with Allure for detailed, visual test execution reports.

## 🚀 How to Run

### Prerequisites
1.  **Python 3.8+** installed.
2.  **Allure Commandline** installed on your system (for viewing reports).

### Setup
1.  Clone the repository and navigate to the root directory.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Install Playwright browsers:
    ```bash
    playwright install
    ```

### Running Tests
To execute all tests and generate Allure results:
```bash
pytest
```
*Note: Default options in `pytest.ini` are configured to run in headed mode and save results to `allure-results/`.*

## 📊 Results & Reporting

The framework generates Allure results in the `allure-results` directory. To generate and view the interactive report:

```bash
allure serve allure-results
```

This will open a local server and launch the report in your default browser, showing:
- Step-by-step execution details.
- Screenshots on failure and during critical verifications.
- Playwright Traces for deep-dive debugging.

## ⚠️ Limitations & Assumptions

- **Login / Guest Flow**: eBay frequently triggers Captchas or security checks during automated login. The `LoginPage` is designed to attempt login but will log a warning and continue as a **Guest** if the flow is interrupted.
- **Currency Handling**: The framework extracts numeric values from price strings using regex. While it assumes **USD ($)** for logging purposes, it will work with other currencies as long as they follow standard decimal formatting.
- **Dynamic Selectors**: eBay uses highly dynamic IDs and classes. The framework utilizes a multi-strategy locator approach (CSS, text, and role-based) to maximize stability.
- **Anti-Bot Measures**: Running tests too frequently or at high speeds may trigger eBay's anti-bot protections.

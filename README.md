# eBay E2E Testing Framework

A robust automated testing framework for eBay built with Python and Playwright. This project follows the Page Object Model (POM) and Object-Oriented Programming (OOP) principles to ensure maintainability and scalability.

## 🏗 Architecture

The framework is structured as follows:
- **Pages**: Implements the Page Object Model. Each page class (e.g., `HomePage`, `SearchResultsPage`) inherits from `BasePage` and encapsulates page-specific locators and actions.
- **Tests**: Contains the test cases (using `pytest`) that orchestrate the page objects to perform end-to-end scenarios.
- **Data**: Externalized test data in JSON format (`data/test_data.json`) for data-driven testing.
- **Configuration**: Centralized configuration in `pytest.ini` and `conftest.py` for fixtures and environment settings.
- **Reporting**: Generates standard JUnit XML reports for easy integration with CI/CD tools.

## 🚀 How to Run

### Prerequisites
1.  **Python 3.8+** installed.
2.  **Virtual Environment** created and activated (recommended).

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
To execute all tests and generate the report:
```bash
pytest
```
*Note: Default options in `pytest.ini` are configured to run in headed mode and save results to `reports/report.xml`.*

## 📊 Results & Reporting

The framework generates a standard JUnit XML report at `reports/report.xml`. This file can be parsed by:
- Jenkins (JUnit Plugin)
- GitHub Actions
- Azure DevOps
- Most other CI/CD platforms

To view the raw results, you can open the `reports/report.xml` file in any text editor or XML viewer.

## ⚠️ Limitations & Assumptions

- **Login / Guest Flow**: eBay frequently triggers Captchas or security checks during automated login. The `LoginPage` is designed to attempt login but will fallback to **Guest** if the flow is interrupted.
- **Currency Handling**: The framework extracts numeric values from price strings. It assumes decimal formatting consistent with USD.
- **Dynamic Selectors**: Uses a multi-strategy locator approach to handle eBay's dynamic UI.
- **Anti-Bot Measures**: Running tests at high frequency may trigger protections.

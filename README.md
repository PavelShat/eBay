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

Reporting with ReportPortal (Docker)
This framework is integrated with ReportPortal for advanced test analytics. To see the results in a dashboard, follow these steps:
1. Deploy ReportPortal Server
You must have Docker Desktop installed.
Create a folder (e.g., C:\ReportPortal) and download the configuration:

Bash
git clone https://github.com/reportportal/deployment.git .
Crucial: Before starting, open Docker Desktop Settings -> Resources and set Memory to at least 6GB (8GB recommended).

Start the containers:

Bash
docker-compose -p reportportal up -d
Access the UI at http://localhost:8080 (Default: superadmin / erebus).

2. Configure the Integration
Update your pytest.ini with your personal credentials:

Go to User Profile -> API Keys in ReportPortal.

Generate a new UUID token (Value).

Fill in the details in pytest.ini:

Ini, TOML
[pytest]
# Add --reportportal to auto-send results
addopts = --reportportal --headed
rp_api_key = <YOUR_UUID_TOKEN>
rp_endpoint = http://localhost:8080
rp_project = superadmin_personal
rp_launch = eBay_E2E_Tests
rp_verify_ssl = False

3. Run with Reporting
Make sure the plugin is installed in your virtual environment:

Bash
pip install pytest-reportportal
Execute tests:

Bash
pytest (python -m pytest)
The results will automatically appear in the Launches tab of your ReportPortal project.

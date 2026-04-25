import pytest
import json
import os
import logging

# Configure logging for ReportPortal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(params=json.load(open(os.path.join(os.path.dirname(__file__), "data", "test_data.json"))))
def data(request):
    return request.param

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "ignore_https_errors": True,
        "java_script_enabled": True,
    }

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "args": ["--incognito", "--disable-blink-features=AutomationControlled"]
    }

# Session-scoped page to keep the browser open and logged in across tests
@pytest.fixture(scope="session")
def context(browser, browser_context_args):
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()

@pytest.fixture(scope="session")
def page(context):
    # This page will be shared by all tests in the session
    page = context.new_page()
    yield page
    page.close()

@pytest.fixture(autouse=True)
def failure_screenshot(request, page):
    yield
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.failed:
        try:
            # ReportPortal will capture this log message
            logger.error(f"TEST FAILED: {request.node.nodeid}")
            logger.info(f"URL at failure: {page.url}")
            # Optional: Capture screenshot to local folder for debugging if needed
            # screenshot_path = f"failure_{request.node.name}.png"
            # page.screenshot(path=screenshot_path)
        except Exception as e:
            logger.error(f"Error during failure reporting: {e}")

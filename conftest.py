import pytest
import json
import os
import logging
from datetime import datetime

# Configure logging
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

@pytest.fixture(scope="session")
def context(browser, browser_context_args):
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()

@pytest.fixture(scope="session")
def page(context):
    page = context.new_page()
    yield page
    page.close()

@pytest.fixture(autouse=True)
def rp_logger(request):
    """
    Fixture to provide a logger that can attach files to ReportPortal.
    """
    import logging
    logger = logging.getLogger("reportportal_client")
    return logger

@pytest.fixture(autouse=True)
def failure_screenshot(request, page):
    yield
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.failed:
        try:
            screenshot_bytes = page.screenshot()
            # Log to standard logger
            logger.error(f"TEST FAILED: {request.node.nodeid}")
            logger.info(f"URL at failure: {page.url}")
            
            # Attach to ReportPortal if available
            try:
                from reportportal_client import RPLogger
                rp_logger = logging.getLogger("reportportal_client")
                if isinstance(rp_logger, RPLogger):
                    rp_logger.info(
                        "FAILURE SCREENSHOT",
                        attachment={
                            "name": "failure_screenshot.png",
                            "data": screenshot_bytes,
                            "mime": "image/png",
                        },
                    )
            except ImportError:
                pass
                
            # Save locally as fallback
            os.makedirs("reports", exist_ok=True)
            screenshot_path = f"reports/failure_{request.node.name}.png"
            page.screenshot(path=screenshot_path)
        except Exception as e:
            logger.error(f"Error during failure reporting: {e}")

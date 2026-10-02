import json
import os
import platform
from collections.abc import Generator
from pathlib import Path
from urllib.parse import urlsplit

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver

from automation.pages.ads_page import AdsPage
from automation.pages.calendar_page import CalendarPage
from automation.pages.form_fields_page import FormFieldsPage
from automation.pages.modals_page import ModalsPage

DRIVER_KEY = pytest.StashKey[WebDriver]()


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("ui", "Selenium UI configuration")
    group.addoption("--browser", choices=("chrome", "firefox", "all"), default="all")
    group.addoption("--headless", action="store_true", help="Run without a browser window")
    group.addoption("--base-url", default="https://practice-automation.com")
    group.addoption("--timeout", type=float, default=15, help="Explicit wait timeout in seconds")
    group.addoption("--page-load-timeout", type=float, default=60)


def pytest_configure(config: pytest.Config) -> None:
    for option in ("--timeout", "--page-load-timeout"):
        if config.getoption(option) <= 0:
            raise pytest.UsageError(f"{option} must be greater than zero")
    parsed = urlsplit(config.getoption("--base-url"))
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise pytest.UsageError("--base-url must be an absolute HTTP(S) URL")
    if parsed.query or parsed.fragment:
        raise pytest.UsageError("--base-url must not contain a query string or fragment")
    # Driver discovery is part of Selenium; no webdriver-manager dependency is needed.
    os.environ.setdefault("SE_AVOID_STATS", "true")
    report_dir = config.getoption("allure_report_dir")
    if report_dir and not config.option.collectonly:
        destination = Path(report_dir)
        destination.mkdir(parents=True, exist_ok=True)
        environment = {
            "OS": platform.platform(),
            "Python": platform.python_version(),
            "Browsers": config.getoption("--browser"),
            "Headless": str(config.getoption("--headless")),
            "Base.URL": config.getoption("--base-url"),
            "Wait.Seconds": str(config.getoption("--timeout")),
        }
        (destination / "environment.properties").write_text(
            "\n".join(f"{key}={value}" for key, value in environment.items()) + "\n",
            encoding="utf-8",
        )
        (destination / "categories.json").write_text(
            json.dumps(
                [
                    {"name": "Assertion / product behavior", "matchedStatuses": ["failed"]},
                    {"name": "WebDriver / environment / timeout", "matchedStatuses": ["broken"]},
                ]
            ),
            encoding="utf-8",
        )


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "browser_name" in metafunc.fixturenames:
        selected = metafunc.config.getoption("--browser")
        names = ["chrome", "firefox"] if selected == "all" else [selected]
        metafunc.parametrize("browser_name", names, scope="session")


@pytest.fixture
def driver(request: pytest.FixtureRequest, browser_name: str) -> Generator[WebDriver]:
    allure.dynamic.parameter("browser", browser_name)
    headless = request.config.getoption("--headless")
    with allure.step(f"Запустить {browser_name}; headless={headless}"):
        if browser_name == "chrome":
            options = webdriver.ChromeOptions()
            options.page_load_strategy = "normal"
            options.add_argument("--lang=en-US")
            if headless:
                options.add_argument("--headless=new")
            if binary := os.getenv("CHROME_BINARY"):
                options.binary_location = binary
            service = ChromeService(executable_path=os.getenv("CHROMEDRIVER_PATH"))
            instance = webdriver.Chrome(options=options, service=service)
        else:
            options = webdriver.FirefoxOptions()
            options.page_load_strategy = "normal"
            options.set_preference("intl.accept_languages", "en-US,en")
            if headless:
                options.add_argument("-headless")
            if binary := os.getenv("FIREFOX_BINARY"):
                options.binary_location = binary
            service = FirefoxService(executable_path=os.getenv("GECKODRIVER_PATH"))
            instance = webdriver.Firefox(options=options, service=service)
    # Stash immediately: setup failures in page fixtures must also get screenshots.
    request.node.stash[DRIVER_KEY] = instance
    try:
        instance.implicitly_wait(0)
        instance.set_page_load_timeout(request.config.getoption("--page-load-timeout"))
        instance.set_script_timeout(request.config.getoption("--timeout"))
        instance.set_window_size(1440, 1000)
        allure.attach(
            json.dumps(instance.capabilities, ensure_ascii=False, indent=2),
            "Browser capabilities",
            allure.attachment_type.JSON,
        )
        yield instance
    finally:
        with allure.step("Завершить браузерную сессию"):
            instance.quit()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if not report.failed:
        return
    allure.attach(str(report.longrepr), f"Failure ({report.when})", allure.attachment_type.TEXT)
    instance = item.stash.get(DRIVER_KEY, None)
    if instance is None:
        allure.attach(
            "WebDriver не создал сессию. Скриншот недоступен; см. Failure и environment.",
            "Diagnostics",
            allure.attachment_type.TEXT,
        )
        return
    # Diagnostic collection must never replace the original test failure.
    for name, operation, attachment_type in (
        ("Screenshot", instance.get_screenshot_as_png, allure.attachment_type.PNG),
        ("Page HTML", lambda: instance.page_source, allure.attachment_type.HTML),
        ("Current URL", lambda: instance.current_url, allure.attachment_type.TEXT),
    ):
        try:
            allure.attach(operation(), f"{name} ({report.when})", attachment_type)
        except Exception as error:
            allure.attach(
                f"{type(error).__name__}: {error}",
                f"{name} unavailable",
                allure.attachment_type.TEXT,
            )


def _page(page_type, driver, request):
    return page_type(
        driver, request.config.getoption("--base-url"), request.config.getoption("--timeout")
    ).open()


@pytest.fixture
def calendar_page(driver: WebDriver, request: pytest.FixtureRequest) -> CalendarPage:
    return _page(CalendarPage, driver, request)


@pytest.fixture
def modals_page(driver: WebDriver, request: pytest.FixtureRequest) -> ModalsPage:
    return _page(ModalsPage, driver, request)


@pytest.fixture
def ads_page(driver: WebDriver, request: pytest.FixtureRequest) -> AdsPage:
    return _page(AdsPage, driver, request)


@pytest.fixture
def form_fields_page(driver: WebDriver, request: pytest.FixtureRequest) -> FormFieldsPage:
    return _page(FormFieldsPage, driver, request)

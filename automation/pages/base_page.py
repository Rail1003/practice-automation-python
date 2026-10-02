from typing import Self
from urllib.parse import urljoin, urlsplit

import allure
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

Locator = tuple[str, str]


class BasePage:
    path = "/"
    heading = "Welcome to your software automation practice website!"
    TITLE = (By.CSS_SELECTOR, "h1")

    def __init__(self, driver: WebDriver, base_url: str, timeout: float = 15):
        self.driver = driver
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout, poll_frequency=0.2)

    def open(self) -> Self:
        with allure.step(f"Открыть страницу {self.path}"):
            self.driver.get(urljoin(self.base_url, self.path.lstrip("/")))
            self.wait.until(ec.text_to_be_present_in_element(self.TITLE, self.heading))
        return self

    def visible(self, locator: Locator) -> WebElement:
        return self.wait.until(ec.visibility_of_element_located(locator))

    def clickable(self, locator: Locator) -> WebElement:
        return self.wait.until(ec.element_to_be_clickable(locator))

    def click(self, locator: Locator) -> None:
        self.clickable(locator).click()

    def fill(self, locator: Locator, text: str) -> None:
        element = self.clickable(locator)
        # Real keyboard input also notifies the site's reactive form validation.
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.BACKSPACE)
        if text:
            element.send_keys(text)

    def value(self, locator: Locator) -> str:
        return self.visible(locator).get_property("value")

    def is_visible(self, locator: Locator) -> bool:
        try:
            return any(e.is_displayed() for e in self.driver.find_elements(*locator))
        except StaleElementReferenceException:
            return False

    @allure.step("Дождаться закрытия элемента")
    def wait_hidden(self, locator: Locator) -> None:
        self.wait.until(ec.invisibility_of_element_located(locator))

    @allure.step("Проверить отсутствие элемента в течение {seconds} секунд")
    def ensure_hidden_for(self, locator: Locator, seconds: float) -> None:
        try:
            WebDriverWait(self.driver, seconds, poll_frequency=0.1).until(
                lambda _: self.is_visible(locator)
            )
        except TimeoutException:
            return
        raise AssertionError(f"Элемент появился, хотя должен оставаться скрытым: {locator}")

    @allure.step("Проверить, что элемент остаётся открытым {seconds} секунд")
    def ensure_visible_for(self, locator: Locator, seconds: float = 1) -> None:
        try:
            WebDriverWait(self.driver, seconds, poll_frequency=0.1).until(
                lambda _: not self.is_visible(locator)
            )
        except TimeoutException:
            return
        raise AssertionError(f"Элемент неожиданно закрылся: {locator}")

    @allure.step("Нажать Escape")
    def press_escape(self) -> None:
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

    @allure.step("Перейти на главную страницу через Home")
    def go_home(self) -> None:
        # Scope to the breadcrumb; do not click the footer's external links.
        self.click((By.XPATH, "//a[normalize-space()='Home']"))
        expected_path = urlsplit(self.base_url).path.rstrip("/") or "/"
        self.wait.until(
            lambda d: (urlsplit(d.current_url).path.rstrip("/") or "/") == expected_path
        )

    @allure.step("Проверить подтверждение отправки и отправленные значения")
    def success_summary(self, scope: str, values: tuple[str, ...]) -> str:
        locator = (By.CSS_SELECTOR, f"{scope} .contact-form-submission.submission-success")

        def populated_summary(_):
            summary = self.visible(locator).text
            normalized = " ".join(summary.split())
            if "Thank you for your response." in summary and all(
                " ".join(value.split()) in normalized for value in values
            ):
                return summary
            return False

        summary = self.wait.until(populated_summary)
        normalized = " ".join(summary.split())
        for value in values:
            assert " ".join(value.split()) in normalized, (value, summary)
        return summary

    def click_backdrop(self, overlay: Locator) -> None:
        element = self.visible(overlay)
        # The corner of the full-screen overlay is outside its centered dialog.
        ActionChains(self.driver).move_to_element_with_offset(
            element, -element.size["width"] / 2 + 8, -element.size["height"] / 2 + 8
        ).click().perform()

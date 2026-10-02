import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from automation.pages.base_page import BasePage, Locator


class ModalsPage(BasePage):
    path = "/modals/"
    heading = "Modals"
    SIMPLE_TRIGGER = (By.ID, "simpleModal")
    FORM_TRIGGER = (By.ID, "formModal")
    SIMPLE = (By.ID, "pum-1318")
    FORM = (By.ID, "pum-674")
    SIMPLE_TITLE = (By.ID, "pum_popup_title_1318")
    SIMPLE_CONTENT = (By.CSS_SELECTOR, "#pum-1318 .pum-content")
    FORM_TITLE = (By.ID, "pum_popup_title_674")
    SIMPLE_CLOSE = (By.CSS_SELECTOR, "#pum-1318 .pum-close")
    FORM_CLOSE = (By.CSS_SELECTOR, "#pum-674 .pum-close")
    NAME = (By.CSS_SELECTOR, "#pum-674 input.name")
    EMAIL = (By.CSS_SELECTOR, "#pum-674 input.email")
    MESSAGE = (By.CSS_SELECTOR, "#pum-674 textarea.grunion-field")
    SUBMIT = (By.CSS_SELECTOR, "#pum-674 button[type='submit']")
    SUCCESS = (By.CSS_SELECTOR, "#pum-674 .contact-form-submission.submission-success")

    @allure.step("Открыть простое модальное окно")
    def open_simple(self) -> None:
        self.click(self.SIMPLE_TRIGGER)
        self.visible(self.SIMPLE)
        self.visible(self.SIMPLE_CLOSE)

    @allure.step("Открыть модальное окно с формой")
    def open_form(self) -> None:
        self.click(self.FORM_TRIGGER)
        self.visible(self.NAME)
        self.visible(self.FORM_CLOSE)

    @allure.step("Закрыть простое модальное окно крестиком")
    def close_simple(self) -> None:
        self.click(self.SIMPLE_CLOSE)
        self.wait_hidden(self.SIMPLE)

    @allure.step("Закрыть окно с формой крестиком")
    def close_form(self) -> None:
        self.click(self.FORM_CLOSE)
        self.wait_hidden(self.FORM)

    @allure.step("Заполнить форму: имя={name}, email={email}")
    def fill_form(self, name: str, email: str = "", message: str = "") -> None:
        self.fill(self.NAME, name)
        self.fill(self.EMAIL, email)
        self.fill(self.MESSAGE, message)
        self.visible(self.MESSAGE).send_keys(Keys.TAB)

    @allure.step("Отправить модальную форму")
    def submit(self) -> None:
        self.click(self.SUBMIT)

    @allure.step("Проверить ошибку поля {field}")
    def assert_field_invalid(self, field: Locator, expected_value: str) -> None:
        # WordPress uses novalidate, so native browser tooltips are not an oracle.
        self.wait.until(lambda _: self.visible(field).get_attribute("aria-invalid") == "true")
        assert self.value(field) == expected_value
        assert self.is_visible(self.FORM)
        assert not self.is_visible(self.SUCCESS)

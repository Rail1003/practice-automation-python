import allure
from selenium.webdriver.common.by import By

from automation.pages.base_page import BasePage


class FormFieldsPage(BasePage):
    path = "/form-fields/"
    heading = "Form Fields"
    TOOLS = (By.CSS_SELECTOR, "#feedbackForm ul li")
    MESSAGE = (By.ID, "message")

    @allure.step("Прочитать список Automation Tools средствами Selenium")
    def automation_tools(self) -> list[str]:
        elements = self.wait.until(lambda d: d.find_elements(*self.TOOLS))
        names = [element.text.strip() for element in elements]
        assert names and all(names), f"Список содержит пустые названия: {names}"
        allure.attach("\n".join(names), "Automation Tools", allure.attachment_type.TEXT)
        return names

    @allure.step("Заполнить Message списком инструментов через запятую")
    def fill_message(self, tools: list[str]) -> str:
        text = ", ".join(tools)
        self.fill(self.MESSAGE, text)
        return text

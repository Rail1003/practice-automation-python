import allure
import pytest

from automation.pages.form_fields_page import FormFieldsPage


@pytest.mark.form_fields
@pytest.mark.positive
@allure.epic("UI Automation")
@allure.feature("Form Fields")
@allure.title("FORM-P01 — Заполнение Message списком Automation Tools через Selenium")
def test_message_from_automation_tools(form_fields_page: FormFieldsPage):
    tools = form_fields_page.automation_tools()
    expected = form_fields_page.fill_message(tools)
    with allure.step("Проверить Message, порядок и полноту списка"):
        actual = form_fields_page.value(form_fields_page.MESSAGE)
        assert actual == expected
        assert actual.split(", ") == tools
        assert len(tools) == len(set(tools)), f"В Automation Tools есть дубликаты: {tools}"
        allure.attach(actual, "Message", allure.attachment_type.TEXT)

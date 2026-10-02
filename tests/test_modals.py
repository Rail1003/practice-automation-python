import allure
import pytest

from automation.pages.modals_page import ModalsPage

pytestmark = [pytest.mark.modals, allure.epic("UI Automation"), allure.feature("Modals")]


@pytest.mark.positive
@allure.title("MOD-P01 — Открытие простого окна и проверка содержимого")
def test_simple_modal_contents(modals_page: ModalsPage):
    modals_page.open_simple()
    assert modals_page.visible(modals_page.SIMPLE_TITLE).text == "Simple Modal"
    assert modals_page.visible(modals_page.SIMPLE_CONTENT).text == "Hi, I’m a simple modal."
    assert not modals_page.is_visible(modals_page.FORM)


@pytest.mark.positive
@allure.title("MOD-P02 — Закрытие простого окна крестиком")
def test_close_simple_modal(modals_page: ModalsPage):
    modals_page.open_simple()
    modals_page.close_simple()
    assert not modals_page.is_visible(modals_page.SIMPLE)
    assert modals_page.clickable(modals_page.FORM_TRIGGER).is_enabled()


@pytest.mark.positive
@allure.title("MOD-P03 — Повторное открытие простого окна")
def test_reopen_simple_modal(modals_page: ModalsPage):
    modals_page.open_simple()
    modals_page.close_simple()
    modals_page.open_simple()
    assert modals_page.visible(modals_page.SIMPLE_CONTENT).text == "Hi, I’m a simple modal."


@pytest.mark.positive
@allure.title("MOD-P04 — Открытие формы и редактирование её полей")
def test_form_fields_are_editable(modals_page: ModalsPage):
    modals_page.open_form()
    assert modals_page.visible(modals_page.FORM_TITLE).text == "Modal Containing A Form"
    assert not modals_page.is_visible(modals_page.SIMPLE)
    modals_page.fill_form("Automation Test", "ui-test@example.com", "Test message")
    assert modals_page.value(modals_page.NAME) == "Automation Test"
    assert modals_page.value(modals_page.EMAIL) == "ui-test@example.com"
    assert modals_page.value(modals_page.MESSAGE) == "Test message"
    modals_page.close_form()
    assert not modals_page.is_visible(modals_page.FORM)


@pytest.mark.positive
@allure.title("MOD-P05 — Закрытие модальной формы по Escape")
def test_form_closes_with_escape(modals_page: ModalsPage):
    modals_page.open_form()
    modals_page.press_escape()
    modals_page.wait_hidden(modals_page.FORM)
    assert not modals_page.is_visible(modals_page.FORM)


@pytest.mark.positive
@allure.title("MOD-P06 — Отправка формы с корректными именем и email")
def test_submit_name_and_email(modals_page: ModalsPage):
    modals_page.open_form()
    modals_page.fill_form("Automation Test", "ui-test@example.com")
    modals_page.submit()
    modals_page.success_summary("#pum-674", ("Automation Test", "ui-test@example.com"))


@pytest.mark.positive
@allure.title("MOD-P07 — Отправка только обязательного имени")
def test_optional_fields_may_be_empty(modals_page: ModalsPage):
    modals_page.open_form()
    modals_page.fill_form("Automation Test")
    assert modals_page.value(modals_page.EMAIL) == ""
    assert modals_page.value(modals_page.MESSAGE) == ""
    modals_page.submit()
    modals_page.success_summary("#pum-674", ("Automation Test",))


@pytest.mark.positive
@allure.title("MOD-P08 — Отправка Unicode и многострочного сообщения")
def test_unicode_multiline_message(modals_page: ModalsPage):
    message = "Проверка формы\nSelenium: строка 2"
    modals_page.open_form()
    modals_page.fill_form("Тест Автоматизации", "ui-test@example.com", message)
    assert modals_page.value(modals_page.MESSAGE) == message
    modals_page.submit()
    modals_page.success_summary("#pum-674", ("Тест Автоматизации", message))


@pytest.mark.negative
@allure.title("MOD-N01 — Запрет отправки без обязательного имени")
def test_required_name(modals_page: ModalsPage):
    modals_page.open_form()
    modals_page.fill_form("", "ui-test@example.com", "Required name test")
    modals_page.submit()
    modals_page.assert_field_invalid(modals_page.NAME, "")
    assert modals_page.value(modals_page.MESSAGE) == "Required name test"


@pytest.mark.negative
@allure.title("MOD-N02 — Запрет отправки с некорректным email")
def test_invalid_email(modals_page: ModalsPage):
    modals_page.open_form()
    modals_page.fill_form("Automation Test", "invalid-email", "Validation test")
    modals_page.submit()
    modals_page.assert_field_invalid(modals_page.EMAIL, "invalid-email")
    assert modals_page.value(modals_page.NAME) == "Automation Test"


@pytest.mark.negative
@allure.title("MOD-N03 — Escape не закрывает простое окно")
def test_simple_modal_ignores_escape(modals_page: ModalsPage):
    modals_page.open_simple()
    modals_page.press_escape()
    modals_page.ensure_visible_for(modals_page.SIMPLE)


@pytest.mark.negative
@allure.title("MOD-N04 — Нажатие на фон не закрывает форму и не стирает данные")
def test_form_ignores_backdrop_click(modals_page: ModalsPage):
    modals_page.open_form()
    modals_page.fill_form("Automation Test", message="Unsaved message")
    modals_page.click_backdrop(modals_page.FORM)
    modals_page.ensure_visible_for(modals_page.FORM)
    assert modals_page.value(modals_page.MESSAGE) == "Unsaved message"

from datetime import date

import allure
import pytest

from automation.pages.calendar_page import CalendarPage

pytestmark = [pytest.mark.calendars, allure.epic("UI Automation"), allure.feature("Calendars")]


@pytest.mark.positive
@allure.title("CAL-P01 — Выбор сегодняшней даты в календаре")
def test_select_today(calendar_page: CalendarPage):
    target = calendar_page.browser_today()
    calendar_page.select_date(target)
    assert calendar_page.value(calendar_page.DATE) == target.isoformat()
    calendar_page.assert_no_error()


@pytest.mark.positive
@allure.title("CAL-P02 — Выбор даты следующего месяца через пагинацию")
def test_select_next_month(calendar_page: CalendarPage):
    calendar_page.enter_date("2026-06-15")
    calendar_page.select_date(date(2026, 7, 10))
    assert calendar_page.value(calendar_page.DATE) == "2026-07-10"


@pytest.mark.positive
@allure.title("CAL-P03 — Выбор даты предыдущего месяца через пагинацию")
def test_select_previous_month(calendar_page: CalendarPage):
    calendar_page.enter_date("2026-06-15")
    calendar_page.select_date(date(2026, 5, 10))
    assert calendar_page.value(calendar_page.DATE) == "2026-05-10"


@pytest.mark.positive
@allure.title("CAL-P04 — Переход из декабря в январь следующего года")
def test_next_year_boundary(calendar_page: CalendarPage):
    calendar_page.enter_date("2026-12-15")
    calendar_page.select_date(date(2027, 1, 1))
    assert calendar_page.value(calendar_page.DATE) == "2027-01-01"


@pytest.mark.positive
@allure.title("CAL-P05 — Переход из января в декабрь предыдущего года")
def test_previous_year_boundary(calendar_page: CalendarPage):
    calendar_page.enter_date("2026-01-15")
    calendar_page.select_date(date(2025, 12, 31))
    assert calendar_page.value(calendar_page.DATE) == "2025-12-31"


@pytest.mark.positive
@allure.title("CAL-P06 — Выбор 29 февраля високосного года")
def test_select_leap_day(calendar_page: CalendarPage):
    calendar_page.enter_date("2024-03-01")
    calendar_page.select_date(date(2024, 2, 29))
    assert calendar_page.value(calendar_page.DATE) == "2024-02-29"
    calendar_page.assert_no_error()


@pytest.mark.positive
@allure.title("CAL-P07 — Ручной ввод и замена ранее выбранной даты")
def test_manual_date_replaces_selection(calendar_page: CalendarPage):
    calendar_page.select_date(calendar_page.browser_today())
    calendar_page.enter_date("2030-08-20")
    assert calendar_page.value(calendar_page.DATE) == "2030-08-20"
    calendar_page.assert_no_error()
    calendar_page.open_picker()
    assert calendar_page.displayed_month() == (2030, 8)


@pytest.mark.positive
@allure.title("CAL-P08 — Успешная отправка формы с датой")
def test_submit_valid_date(calendar_page: CalendarPage):
    calendar_page.enter_date("2026-10-15")
    calendar_page.submit()
    calendar_page.success_summary("article", ("2026-10-15",))


@pytest.mark.negative
@pytest.mark.parametrize(
    "invalid_date,case_id",
    [
        ("2025-02-29", "CAL-N01"),
        ("2026-04-31", "CAL-N02"),
        ("2026-13-10", "CAL-N03"),
        ("not-a-date", "CAL-N04"),
    ],
    ids=["CAL-N01-non-leap", "CAL-N02-day-overflow", "CAL-N03-month-overflow", "CAL-N04-text"],
)
@allure.title("{case_id} — Отклонение некорректной даты: {invalid_date}")
def test_invalid_date_is_rejected(calendar_page: CalendarPage, invalid_date: str, case_id: str):
    calendar_page.enter_date(invalid_date)
    calendar_page.submit()
    calendar_page.assert_rejected(invalid_date)

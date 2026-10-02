import allure
import pytest

from automation.pages.ads_page import AdsPage

pytestmark = [pytest.mark.ads, allure.epic("UI Automation"), allure.feature("Ads")]


@pytest.mark.positive
@allure.title("ADS-P01 — Автоматическое появление рекламы и её содержимое")
def test_ad_appears_without_interaction(ads_page: AdsPage):
    ads_page.wait_for_ad()
    assert ads_page.visible(ads_page.TITLE_AD).text == "Hi"
    assert ads_page.visible(ads_page.CONTENT).text == "I am an ad."


@pytest.mark.positive
@allure.title("ADS-P02 — Закрытие рекламы крестиком")
def test_close_ad(ads_page: AdsPage):
    ads_page.wait_for_ad()
    ads_page.close_ad()
    assert not ads_page.is_visible(ads_page.AD)


@pytest.mark.positive
@allure.title("ADS-P03 — Закрытие рекламы клавиатурой")
def test_close_ad_with_enter(ads_page: AdsPage):
    ads_page.wait_for_ad()
    ads_page.close_ad_with_keyboard()
    assert not ads_page.is_visible(ads_page.AD)


@pytest.mark.positive
@allure.title("ADS-P04 — Повторное появление рекламы после обновления страницы")
def test_reload_restarts_ad(ads_page: AdsPage):
    ads_page.wait_for_ad()
    ads_page.close_ad()
    ads_page.driver.refresh()
    ads_page.wait_for_ad()
    assert ads_page.visible(ads_page.CONTENT).text == "I am an ad."


@pytest.mark.positive
@allure.title("ADS-P05 — Появление рекламы после нового посещения страницы")
def test_new_visit_restarts_ad(ads_page: AdsPage):
    ads_page.wait_for_ad()
    ads_page.close_ad()
    ads_page.go_home()
    ads_page.open()
    ads_page.wait_for_ad()
    assert ads_page.visible(ads_page.CONTENT).text == "I am an ad."


@pytest.mark.positive
@allure.title("ADS-P06 — После закрытия рекламы доступна навигация Home")
def test_navigation_after_closing_ad(ads_page: AdsPage):
    ads_page.wait_for_ad()
    ads_page.close_ad()
    ads_page.go_home()
    assert "Welcome" in ads_page.visible(ads_page.TITLE).text


@pytest.mark.positive
@allure.title("ADS-P07 — Прокрутка страницы не препятствует появлению рекламы")
def test_scrolling_does_not_prevent_ad(ads_page: AdsPage):
    ads_page.scroll_to_footer()
    ads_page.wait_for_ad()
    assert ads_page.visible(ads_page.CLOSE).is_enabled()
    ads_page.close_ad()
    assert not ads_page.is_visible(ads_page.AD)


@pytest.mark.negative
@allure.title("ADS-N01 — Открытая реклама блокирует навигацию фоновой страницы")
def test_ad_blocks_background_navigation(ads_page: AdsPage):
    ads_page.wait_for_ad()
    original_url = ads_page.driver.current_url
    assert ads_page.background_home_is_blocked(), "Клик прошёл сквозь рекламное окно"
    assert ads_page.driver.current_url == original_url
    ads_page.ensure_visible_for(ads_page.AD)


@pytest.mark.negative
@allure.title("ADS-N02 — Escape не закрывает рекламу")
def test_ad_ignores_escape(ads_page: AdsPage):
    ads_page.wait_for_ad()
    ads_page.press_escape()
    ads_page.ensure_visible_for(ads_page.AD)


@pytest.mark.negative
@allure.title("ADS-N03 — Клик на фон не закрывает рекламу")
def test_ad_ignores_backdrop(ads_page: AdsPage):
    ads_page.wait_for_ad()
    ads_page.click_backdrop(ads_page.AD)
    ads_page.ensure_visible_for(ads_page.AD)


@pytest.mark.negative
@allure.title("ADS-N04 — Закрытая реклама не открывается снова в том же посещении")
def test_closed_ad_does_not_reopen(ads_page: AdsPage):
    ads_page.wait_for_ad()
    ads_page.close_ad()
    ads_page.ensure_hidden_for(ads_page.AD, 6)

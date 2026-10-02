import allure
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from automation.pages.base_page import BasePage


class AdsPage(BasePage):
    path = "/ads/"
    heading = "Ads"
    AD = (By.ID, "pum-1272")
    TITLE_AD = (By.ID, "pum_popup_title_1272")
    CONTENT = (By.CSS_SELECTOR, "#pum-1272 .pum-content")
    CLOSE = (By.CSS_SELECTOR, "#pum-1272 .pum-close")

    @allure.step("Дождаться автоматического появления рекламы")
    def wait_for_ad(self) -> None:
        self.visible(self.AD)
        self.visible(self.CLOSE)

    @allure.step("Закрыть рекламу крестиком")
    def close_ad(self) -> None:
        self.click(self.CLOSE)
        self.wait_hidden(self.AD)

    @allure.step("Закрыть рекламу клавишей Enter на кнопке Close")
    def close_ad_with_keyboard(self) -> None:
        self.visible(self.CLOSE).send_keys(Keys.ENTER)
        self.wait_hidden(self.AD)

    @allure.step("Прокрутить страницу вниз до появления рекламы")
    def scroll_to_footer(self) -> None:
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(Keys.END).key_up(
            Keys.CONTROL
        ).perform()

    @allure.step("Попытаться нажать фоновую ссылку Home при открытой рекламе")
    def background_home_is_blocked(self) -> bool:
        try:
            self.click((By.XPATH, "//a[normalize-space()='Home']"))
        except ElementClickInterceptedException as error:
            allure.attach(str(error), "Expected intercepted click", allure.attachment_type.TEXT)
            return True
        return False

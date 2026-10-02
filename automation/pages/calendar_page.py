
    def displayed_month(self) -> tuple[int, int]:
        return int(self.visible(self.YEAR).text), self.MONTH_NAMES.index(
            self.visible(self.MONTH).text
        ) + 1

    @allure.step("Перейти к месяцу выбранной даты {target}")
    def navigate_to(self, target: date) -> None:
        year, month = self.displayed_month()
        distance = (target.year - year) * 12 + target.month - month
        if abs(distance) > 240:
            raise ValueError("Для UI-пагинации задан слишком далёкий месяц (> 20 лет).")
        for _ in range(abs(distance)):
            before = self.displayed_month()
            self.click(self.NEXT if distance > 0 else self.PREVIOUS)
            self.wait.until(lambda _, previous=before: self.displayed_month() != previous)
        assert self.displayed_month() == (target.year, target.month)

    @allure.step("Выбрать в календаре дату {target}")
    def select_date(self, target: date) -> None:
        self.open_picker()
        self.navigate_to(target)
        # Exclude neighboring-month cells with the same day number.
        self.click(
            (
                By.XPATH,
                f"//button[contains(@class,'dp-day') and "
                f"not(contains(@class,'dp-edge-day')) and normalize-space()='{target.day}']",
            )
        )
        self.wait.until(lambda _: self.value(self.DATE) == target.isoformat())
        self.wait_hidden(self.PICKER)

    def browser_today(self) -> date:
        # Use the browser's local date, so CI and Windows time zones do not disagree.
        return date.fromisoformat(
            self.driver.execute_script(
                "const d=new Date(); return d.getFullYear()+'-'+"
                "String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');"
            )
        )

    @allure.step("Отправить календарную форму")
    def submit(self) -> None:
        self.click(self.SUBMIT)

    @allure.step("Проверить отклонение некорректной даты {text}")
    def assert_rejected(self, text: str) -> None:
        self.wait.until(lambda _: "valid date" in self.visible(self.ERROR).text.lower())
        assert self.value(self.DATE) == text
        assert not self.is_visible(self.SUCCESS), "Некорректная дата отправлена успешно"

    def assert_no_error(self) -> None:
        assert not self.is_visible(self.ERROR) or not self.visible(self.ERROR).text.strip()

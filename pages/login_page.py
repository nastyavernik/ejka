import re
from playwright.sync_api import expect
from .base_page import BasePage


class LoginPage(BasePage):
    LOGIN_ENTRY = (
        "https://bun.rt.ru/auth/realms/bun/protocol/openid-connect/auth"
        "?client_id=kolobok&redirect_uri=https://bun.rt.ru/authenticator"
    )
    SUCCESS_URL_PREFIX = "https://bun.rt.ru/list"
    AUTH_FAIL_URL_PREFIX = (
        "https://bun.rt.ru/auth/realms/bun/login-actions/authenticate"
    )

    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#kc-login"
    REMEMBER_ME_BOX = "#checkboxspan"
    ERROR_MESSAGE = ".ui-error"

    def _wait_username_or_timeout(self, timeout_ms: int) -> bool:
        try:
            self.page.wait_for_selector(self.USERNAME_INPUT, timeout=timeout_ms)
            return True
        except Exception:
            return False

    def open(self) -> None:
        self.page.goto(self.LOGIN_ENTRY, wait_until="domcontentloaded")
        if not self._wait_username_or_timeout(5_000):
            raise AssertionError("Форма логина так и не отобразилась")
        expect(self.page.locator(self.USERNAME_INPUT)).to_be_visible()

    def fill_username(self, username: str):
        self.page.fill(self.USERNAME_INPUT, username)

    def fill_password(self, password: str):
        self.page.fill(self.PASSWORD_INPUT, password)

    def toggle_remember_me(self):
        self.page.click(self.REMEMBER_ME_BOX)

    def submit(self):
        self.page.click(self.LOGIN_BUTTON)

    def login_with(self, username: str, password: str, *, remember=False):
        self.open()
        self.fill_username(username)
        self.fill_password(password)
        if remember:
            self.toggle_remember_me()
        self.submit()

    def login(self, username: str, password: str, *, remember=False):
        self.login_with(username, password, remember=remember)
        success_rx = re.compile(rf"^{re.escape(self.SUCCESS_URL_PREFIX)}")
        expect(self.page).to_have_url(success_rx, timeout=10_000)

    def expect_auth_failure(self, expected_text: str | re.Pattern):
        error_locator = self.page.locator(self.ERROR_MESSAGE)
        self.page.wait_for_timeout(300)
        error_locator.scroll_into_view_if_needed(timeout=3000)
        error_locator.wait_for(state="attached", timeout=5000)
        actual_text = error_locator.inner_text().strip()
        assert re.search(expected_text, actual_text), (
            f"Ожидали текст '{expected_text}', но получили '{actual_text}'"
        )

    def login_expect_failure(self, username: str, password: str, expected_error: str | re.Pattern = None):
        self.login_with(username, password)
        self.expect_auth_failure(expected_error or re.compile(r"\s*Логин или пароль указаны неверно\s*"))

    def expect_validation_error(self, expected_text: str | re.Pattern):
        locator = self.page.locator(self.ERROR_MESSAGE)
        self.page.wait_for_timeout(300)
        expect(locator).to_have_text(expected_text, timeout=5000)

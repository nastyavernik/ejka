import re
from playwright.sync_api import expect
from .base_page import BasePage

class ListPage(BasePage):
    URL = "https://bun.rt.ru/list"
    SUCCESS_URL_REGEX = re.compile(r"https://bun\.rt\.ru/list")

    CREATE_PROJECT_BUTTON = 'a[href*="modal=createProject"]'
    TITLE_INPUT = 'input[name="title"]'
    DESCRIPTION_TEXTAREA = 'textarea[name="description"]'
    CODE_INPUT = 'input[name="code"]'
    SUBMIT_BUTTON = 'button:has-text("Создать проект")'
    CANCEL_ICON = 'svg[data-testid="kitIcon"]'
    CANCEL_CONFIRM_TEXT = 'div.confirm_title__ORp5d'
    CANCEL_CONFIRM_BUTTON = 'button:has-text("Не создавать")'

    def open(self):
        self.page.goto(self.URL, wait_until="domcontentloaded")
        expect(self.page).to_have_url(self.SUCCESS_URL_REGEX, timeout=10_000)

    def click_create_project(self):
        self.page.click(self.CREATE_PROJECT_BUTTON)

    def fill_project_title(self, title: str):
        self.page.fill(self.TITLE_INPUT, title)

    def fill_project_description(self, description: str):
        self.page.fill(self.DESCRIPTION_TEXTAREA, description)

    def wait_for_project_code(self) -> str:
        code_input = self.page.locator(self.CODE_INPUT)
        expect(code_input).to_have_value(re.compile(r"[A-Z0-9]{5,}"), timeout=5000)
        return code_input.input_value()

    def submit_create_project(self):
        self.page.click(self.SUBMIT_BUTTON)

    def expect_redirect_to_board(self, project_code: str):
        expect(self.page).to_have_url(re.compile(rf"/project/{project_code}/board"), timeout=10_000)

    def cancel_project_creation(self):
        self.page.locator(self.CANCEL_ICON).click()
        expect(self.page.locator(self.CANCEL_CONFIRM_TEXT)).to_have_text("Не создавать проект?", timeout=3000)
        self.page.click(self.CANCEL_CONFIRM_BUTTON)
        expect(self.page).to_have_url(self.URL, timeout=5000)

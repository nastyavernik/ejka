import re
import random
import string
import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.list_page import ListPage


# ────────────────────────────── HELPERS ──────────────────────────────

def generate_random_name(length=12):
    return 'autotest_' + ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_description(length=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# ─────────────────────── ТЕСТ №1 ───────────────────────

@pytest.mark.skip
@pytest.mark.project
def test_create_new_project_after_manual_login(page, credentials):
    """
    Успешный вход и создание нового проекта с рандомным описанием.
    """
    login_page = LoginPage(page)
    login_page.login(
        username=credentials["username"],
        password=credentials["password"],
        remember=False
    )

    list_page = ListPage(page)
    list_page.open()
    list_page.click_create_project()

    title = generate_random_name()
    description = generate_random_description()

    list_page.fill_project_title(title)
    list_page.fill_project_description(description)
    code = list_page.wait_for_project_code()

    list_page.submit_create_project()
    list_page.expect_redirect_to_board(code)


# ─────────────────────── ТЕСТ №2 ───────────────────────

@pytest.mark.project
def test_create_project_fails_with_empty_description(page, credentials):
    """
    Проект не создаётся, если не заполнено описание.
    """
    login_page = LoginPage(page)
    login_page.login(
        username=credentials["username"],
        password=credentials["password"],
        remember=False
    )

    list_page = ListPage(page)
    list_page.open()
    list_page.click_create_project()

    title = generate_random_name()
    list_page.fill_project_title(title)

    list_page.wait_for_project_code()
    list_page.submit_create_project()

    # Проверяем, что остались в форме создания
    expect(page).to_have_url("https://bun.rt.ru/list?modal=createProject", timeout=5000)


# ─────────────────────── ТЕСТ №3 ───────────────────────

@pytest.mark.skip
@pytest.mark.project
def test_cancel_project_creation_after_filling_form(page, credentials):
    """
    Отмена создания проекта через крестик и 'Не создавать'.
    """
    login_page = LoginPage(page)
    login_page.login(
        username=credentials["username"],
        password=credentials["password"],
        remember=False
    )

    list_page = ListPage(page)
    list_page.open()
    list_page.click_create_project()

    title = generate_random_name()
    list_page.fill_project_title(title)
    list_page.fill_project_description("temporary description")

    list_page.cancel_project_creation()


# ─────────────────────── ТЕСТ №4 ───────────────────────

@pytest.mark.project
def test_continue_project_creation_after_cancel_prompt(page, credentials):
    """
    Появляется окно 'Не создавать проект?' → нажимаем 'Продолжить создание' → создаём проект.
    """
    login_page = LoginPage(page)
    login_page.login(
        username=credentials["username"],
        password=credentials["password"],
        remember=False
    )

    list_page = ListPage(page)
    list_page.open()
    list_page.click_create_project()

    title = generate_random_name()
    description = generate_random_description()

    list_page.fill_project_title(title)
    list_page.fill_project_description(description)

    # Нажимаем крестик
    page.locator('svg[data-testid="kitIcon"]').click()

    # Проверка текста в модалке
    expect(page.locator('div.confirm_title__ORp5d')).to_have_text("Не создавать проект?", timeout=3000)

    # Нажимаем "Продолжить создание"
    page.click('button[data-testid="confirm-cancel-button"]')

    # Убеждаемся, что поля не сброшены
    expect(page.locator('input[name="title"]')).to_have_value(title)

    # Получаем код и завершаем создание
    code = list_page.wait_for_project_code()
    list_page.submit_create_project()
    list_page.expect_redirect_to_board(code)

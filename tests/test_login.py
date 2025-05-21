import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.list_page import ListPage
from builders.user_builder import UserBuilder
import re

# ─────────────────────── CONSTANTS ───────────────────────
INVALID_EMAIL_MESSAGE = r"Введи логин в формате электронной почты"
INVALID_AUTH_MESSAGE  = r"Логин или пароль указаны неверно"
INVALID_PASSWORD_MESSAGE = r"Пароль не подходит"

# ─────────────────────── DATA SETS ───────────────────────
INVALID_PASSWORD_CASES = [
    pytest.param("Aa1@abc",    id="too_short"),
    pytest.param("abcdef1@",   id="no_upper"),
    pytest.param("ABCDEF1@",   id="no_lower"),
    pytest.param("Abcdefg@",   id="no_digit"),
    pytest.param("Abcdefg1",   id="no_symbol"),
]

INVALID_EMAIL_CASES = [
    pytest.param("user",               id="missing_at"),
    pytest.param("user@",             id="missing_domain"),
    pytest.param("@domain.com",       id="missing_username"),
    pytest.param("user@domain",       id="missing_tld"),
    pytest.param("user@domain.c",     id="tld_one_letter"),
    pytest.param("user@.com",         id="missing_domain_prefix"),
    pytest.param("user@@domain.com",  id="double_at"),
    pytest.param("user@domain..com",  id="double_dot"),
]

# ───────────────── Позитивный сценарий ─────────────────
@pytest.mark.auth
def test_login_redirects_to_list(page, credentials):
    login_page = LoginPage(page)
    login_page.login(
        username=credentials["username"],
        password=credentials["password"],
        remember=True,
    )
    list_page = ListPage(page)
    list_page.is_opened()

# ───────────── Неверный пароль, логин валидный ─────────────
@pytest.mark.auth
def test_invalid_password_stays_on_auth_page(page, credentials):
    login_page = LoginPage(page)

    user = UserBuilder() \
        .with_username(credentials["username"]) \
        .with_password("WrongPass123!") \
        .build()

    login_page.login_with(user["username"], user["password"])
    expect(page).to_have_url(re.compile(r"login-actions/authenticate"), timeout=7000)
    login_page.expect_auth_failure(INVALID_AUTH_MESSAGE)

@pytest.mark.auth
def test_invalid_password_shows_generic_error(page, credentials):
    login_page = LoginPage(page)
    login_page.login_with(
        username=credentials["username"],
        password="badPassword123!"
    )
    login_page.expect_auth_failure(INVALID_AUTH_MESSAGE)

# ───────────── Проверка правил к паролю ─────────────
@pytest.mark.auth
@pytest.mark.parametrize("bad_password", INVALID_PASSWORD_CASES)
def test_password_validation_rules(page, credentials, bad_password):
    login_page = LoginPage(page)
    login_page.open()
    page.fill("#username", credentials["username"])
    page.fill("#password", bad_password)
    page.locator("#password").focus()
    page.locator("body").click()
    login_page.expect_validation_error(INVALID_PASSWORD_MESSAGE)

# ───────────── Проверка формата email ─────────────
@pytest.mark.auth
@pytest.mark.parametrize("bad_email", INVALID_EMAIL_CASES)
def test_invalid_email_shows_format_error(page, bad_email):
    login_page = LoginPage(page)
    login_page.open()
    page.fill("#username", bad_email)
    page.locator("#username").focus()
    page.locator("body").click()
    login_page.expect_auth_failure(INVALID_EMAIL_MESSAGE)

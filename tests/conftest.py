import os
import yaml
from dotenv import load_dotenv
from playwright.sync_api import expect, sync_playwright
import pytest
from pages.login_page import LoginPage

# Грузим .env, если он есть
load_dotenv()

@pytest.fixture(scope="session")
def credentials():
    """Читаем логин/пароль из переменных окружения"""
    return {
        "username": os.getenv("TEST_USERNAME"),
        "password": os.getenv("TEST_PASSWORD")
    }

@pytest.fixture(scope="function")
def playwright_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        yield context
        context.close()
        browser.close()

@pytest.fixture
def page(playwright_context):
    page = playwright_context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="function")
def login_if_needed(page, request):
    """
    Автоматический вход перед каждым тестом с UI,
    но с возможной стабилизацией UI только для нужных маркированных тестов.
    """
    page.goto("https://bun.rt.ru/authenticator", wait_until="domcontentloaded")

    if "/list" in page.url or "/projects" in page.url:
        return

    login_page = LoginPage(page)
    login_page.login(
        username="verniknastya11@gmail.com",
        password="adsqewzcxA1!"
    )

    # Обходим баг ТОЛЬКО для нужных тестов
    if "stabilize_ui" in request.keywords:
        for _ in range(2):
            page.goto("https://bun.rt.ru/list", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=10_000)
            page.goto("https://bun.rt.ru", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=10_000)


@pytest.fixture(scope="session")
def credentials():
    """
    Загружает логин и пароль из credentials.yaml
    """
    with open("credentials.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {
        "username": data["login"]["username"],
        "password": data["login"]["password"]
    }

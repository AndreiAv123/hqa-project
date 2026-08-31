"""
UI-suite fixtures — everything Selenium/browser related lives here, scoped
only to tests under tests/ui/. API tests never pull this in.
"""
import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import pytest
import requests


@pytest.fixture
def api_client(user_id, base_url):
    """
    A requests.Session pre-configured with the required x-user-id header
    (spec §5.1), plus small helpers so tests read as api_client.api_get(...).
    """
    session = requests.Session()
    session.headers.update({
        "x-user-id": user_id,
        "Content-Type": "application/json",
    })

    session.api_get = lambda path, **kw: session.request("GET", f"{base_url}{path}", **kw)
    session.api_post = lambda path, **kw: session.request("POST", f"{base_url}{path}", **kw)

    return session


@pytest.fixture
def reset_balance(api_client):
    """
    Resets the test user's balance to the configured initial value before a
    test that depends on a known starting balance (spec §5.3).
    """
    resp = api_client.api_post("/api/reset-balance")
    resp.raise_for_status()
    return resp.json()

@pytest.fixture
def driver(user_id, base_url):
    """
    Chrome WebDriver, pointed at the app with the required ?user-id= query param.
    Headless by default; set HEADED=1 to watch it run locally.
    """
    options = Options()
    # if not os.environ.get("HEADED"):
    #     options.add_argument("--headless=new")

    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(2)
    drv.get(f"{base_url}/?user-id={user_id}")

    yield drv

    drv.quit()

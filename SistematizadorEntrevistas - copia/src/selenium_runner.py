from __future__ import annotations

import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Optional, List

import pyperclip
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import config

@dataclass
class SeleniumResult:
    ok: bool
    tsv_text: str
    message: str


def _kill_edge_processes() -> None:
    for proc in ["msedge.exe", "msedgewebview2.exe", "msedgedriver.exe"]:
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", proc, "/T"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception:
            pass
    time.sleep(2)


def _find_edge_exe() -> str:
    configured = getattr(config, "EDGE_BINARY_PATH", None)
    candidates = [
        configured,
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        shutil.which("msedge"),
    ]
    for item in candidates:
        if item and os.path.exists(item):
            return item
    raise FileNotFoundError("No se encontró msedge.exe. Revisa EDGE_BINARY_PATH en config.py")


def _start_edge_debugger() -> None:
    port = int(getattr(config, "EDGE_DEBUG_PORT", 9222))
    user_data = getattr(config, "EDGE_USER_DATA_DIR", None)
    profile_dir = getattr(config, "EDGE_PROFILE_DIR", "Default")
    edge_exe = _find_edge_exe()

    if not user_data:
        local_app_data = os.environ.get("LOCALAPPDATA")
        user_data = os.path.join(local_app_data, "Microsoft", "Edge", "User Data")

    _kill_edge_processes()

    args = [
        edge_exe,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data}",
        f"--profile-directory={profile_dir}",
        "--start-maximized",
        getattr(config, "CHATGPT_URL", "https://chatgpt.com/"),
    ]

    print(f"[INFO] Abriendo Edge real con perfil: {profile_dir}")
    print(f"[INFO] User Data: {user_data}")
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)


def _make_driver(headless: bool = False, driver_path: Optional[str] = None) -> webdriver.Edge:
    attach = bool(getattr(config, "EDGE_ATTACH_TO_EXISTING", True))
    port = int(getattr(config, "EDGE_DEBUG_PORT", 9222))

    options = Options()
    options.page_load_strategy = "eager"

    if attach:
        _start_edge_debugger()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    else:
        user_data = getattr(config, "EDGE_USER_DATA_DIR", None)
        profile_dir = getattr(config, "EDGE_PROFILE_DIR", "Default")
        if user_data:
            options.add_argument(f"--user-data-dir={user_data}")
            options.add_argument(f"--profile-directory={profile_dir}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

    if headless:
        print("[WARN] headless se ignora cuando se usa perfil real/debugger.")

    service = None
    if driver_path and os.path.exists(driver_path):
        service = Service(executable_path=driver_path)
    else:
        print("[INFO] No se encontró driver local. Selenium intentará resolver EdgeDriver automáticamente...")
        service = Service()

    try:
        return webdriver.Edge(options=options, service=service)
    except Exception as exc:
        print(f"[WARN] Error conectando Edge: {exc}")
        print("[WARN] Reintentando con Edge limpio en modo depuración...")
        _start_edge_debugger()
        return webdriver.Edge(options=options, service=service)


def _try_click_copy_code(driver: webdriver.Edge) -> bool:
    try:
        copiers = driver.find_elements(
            By.XPATH,
            "//button[contains(., 'Copy code') or contains(., 'Copiar código') or contains(., 'Copy') or contains(., 'Copiar')]"
        )
        if not copiers:
            copiers = driver.find_elements(By.CSS_SELECTOR, "button[class*='text-token-text-secondary']")

        if copiers:
            driver.execute_script("arguments[0].scrollIntoView(true);", copiers[-1])
            time.sleep(0.5)
            copiers[-1].click()
            time.sleep(0.8)
            return True
    except Exception:
        pass
    return False


def _extract_last_codeblock_text(driver: webdriver.Edge) -> str:
    try:
        blocks = driver.find_elements(By.CSS_SELECTOR, "pre code")
        if blocks:
            return blocks[-1].text
    except Exception:
        pass
    return ""


def _find_prompt_box(driver: webdriver.Edge):
    textarea_id = getattr(config, "CHATGPT_TEXTAREA_ID", "prompt-textarea")
    selectors = [
        (By.ID, textarea_id),
        (By.CSS_SELECTOR, "#prompt-textarea"),
        (By.CSS_SELECTOR, "div[contenteditable='true']"),
        (By.TAG_NAME, "textarea"),
    ]
    last_error = None
    for by, selector in selectors:
        try:
            return WebDriverWait(driver, 25).until(
                EC.presence_of_element_located((by, selector))
            )
        except Exception as exc:
            last_error = exc
    raise last_error


def run_chatgpt_via_edge(
    prompt_text: str,
    wait_seconds: int = 120,
    sheets_url: Optional[str] = None,
    headless: bool = False,
    driver_path: Optional[str] = None,
    file_paths: Optional[List[str]] = None,
) -> SeleniumResult:
    driver = None
    try:
        path_check = driver_path or str(getattr(config, "DEFAULT_DRIVER_PATH", ""))
        driver = _make_driver(headless, path_check)

        driver.get(getattr(config, "CHATGPT_URL", "https://chatgpt.com/"))
        print("[INFO] Cargando ChatGPT con tu perfil real...")
        time.sleep(7)

        if file_paths:
            print(f"[INFO] Se detectaron {len(file_paths)} archivo(s) para subir.")
            try:
                file_input = WebDriverWait(driver, 25).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
                for f_path in file_paths:
                    if os.path.exists(f_path):
                        print(f"    >> Subiendo: {os.path.basename(f_path)}")
                        file_input.send_keys(os.path.abspath(f_path))
                        time.sleep(4)
                    else:
                        print(f"    [WARN] No existe el archivo: {f_path}")
                print("[INFO] Archivos cargados.")
                time.sleep(4)
            except Exception as exc:
                print(f"[WARN] No se pudieron subir los archivos: {exc}")

        box = _find_prompt_box(driver)
        box.click()
        time.sleep(0.5)

        pyperclip.copy(prompt_text)
        box.send_keys(Keys.CONTROL, "v")
        time.sleep(2)

        try:
            btn = driver.find_element(
                By.CSS_SELECTOR,
                getattr(config, "CHATGPT_SEND_BUTTON_SELECTOR", "[data-testid='send-button']")
            )
            btn.click()
        except Exception:
            box.send_keys(Keys.ENTER)

        print(f"[INFO] Esperando respuesta ({wait_seconds}s)...")
        time.sleep(wait_seconds)

        copied = _try_click_copy_code(driver)
        tsv = (pyperclip.paste() or "").strip() if copied else ""

        if not tsv:
            tsv = _extract_last_codeblock_text(driver)

        if not tsv:
            return SeleniumResult(False, "", "No se obtuvo TSV")

        if sheets_url:
            try:
                driver.get(sheets_url)
                time.sleep(5)
                ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                time.sleep(2)
            except Exception:
                pass

        return SeleniumResult(True, tsv, "OK")

    except Exception as exc:
        return SeleniumResult(False, "", f"Error Selenium: {exc}")
    finally:
        pass

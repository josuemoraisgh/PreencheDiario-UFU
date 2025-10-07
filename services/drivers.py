# drivers.py (online, estilo do exemplo que funcionava)
from __future__ import annotations
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from typing import Callable, Optional

def create_driver(browser: str = "edge", logger: Optional[Callable[[str], None]] = None):
    """
    Inicia o Edge de forma visível priorizando Selenium Manager (Selenium 4.6+).
    Fallback: webdriver_manager (online).
    """
    if browser.lower() != "edge" and logger:
        logger(f"[drivers] Browser {browser!r} não suportado; usando 'edge'.")

    options = EdgeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)  # mantém janela aberta

    # 1) Primeiro tenta Selenium Manager (não depende do repositório do webdriver_manager)
    try:
        if logger: logger("[drivers] Tentando Selenium Manager (padrão do Selenium)...")
        service = EdgeService()  # sem path → Selenium resolve o driver
        driver = webdriver.Edge(service=service, options=options)
        if logger: logger("[drivers] Edge iniciado via Selenium Manager.")
        return driver
    except Exception as e1:
        if logger:
            logger(f"[drivers] Selenium Manager falhou: {type(e1).__name__}: {e1}")

    # 2) Fallback: webdriver_manager (online)
    try:
        if logger: logger("[drivers] Tentando webdriver_manager (baixa driver online)...")
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        if logger: logger("[drivers] Edge iniciado via webdriver_manager.")
        return driver
    except Exception as e2:
        if logger:
            logger(f"[drivers] webdriver_manager falhou: {type(e2).__name__}: {e2}")
        raise

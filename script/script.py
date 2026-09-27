import os
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options

def ejecutar_automatizacion():
    print("\n[Python] Conectando de forma segura a tu Edge activo...")
    
    edge_options = Options()
    edge_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    os.environ['SE_OFFLINE'] = 'true'
    
    try:
        driver = webdriver.Edge(options=edge_options)
        
        print("[Python] Conectado con exito. Navegando a ChatGPT...")
        driver.get("https://chatgpt.com")
        
        time.sleep(3)
        print("[Python] Exito. El sistema esta controlado desde Python.")
    except Exception as e:
        print(f"\n[Python] Error de conexion: {e}")

if __name__ == "__main__":
    ejecutar_automatizacion()

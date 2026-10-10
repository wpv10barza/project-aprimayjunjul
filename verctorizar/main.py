import flet as ft
import requests

IP_LAPTOP = "http://192.168.1.XX:5000/ejecutar_auditoria"

def main(page: ft.Page):
    page.title = "Gestor RAG Auditor"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    titulo = ft.Text("📱 Auditoría Edge", size=24, weight="bold", color=ft.colors.BLUE_400)
    input_pregunta = ft.TextField(label="Código de Pregunta", width=300)
    resultado_texto = ft.Text(value="", selectable=True)
    cargando = ft.ProgressRing(visible=False)

    def ejecutar_auditoria(e):
        if not input_pregunta.value: return
        cargando.visible = True
        page.update()
        try:
            payload = {"pregunta": input_pregunta.value, "criterios": ["Verificar TAT"], "evidencia_cruda": ["Simulación"]}
            response = requests.post(IP_LAPTOP, json=payload, timeout=60)
            resultado_texto.value = response.json().get("resultado", "Error")
        except Exception as ex:
            resultado_texto.value = f"Error: {ex}"
        cargando.visible = False
        page.update()

    btn_ejecutar = ft.ElevatedButton("Ejecutar en PC", on_click=ejecutar_auditoria)
    page.add(ft.Column([titulo, input_pregunta, btn_ejecutar, cargando, resultado_texto]))

if __name__ == "__main__":
    ft.app(target=main)

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import requests
import threading
import json

class PainelOperador(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.base_url = "http://127.0.0.1:5000"

        self.log_box = TextInput(readonly=True, multiline=True, size_hint=(1, 0.85))
        self.add_widget(self.log_box)

        botoes = BoxLayout(size_hint=(1, 0.15), spacing=10)

        btn_status = Button(text="🔄 Obter Status")
        btn_status.bind(on_press=lambda x: self.obter_status())

        btn_iniciar = Button(text="▶️ Iniciar Envio")
        btn_iniciar.bind(on_press=lambda x: self.iniciar_envio())

        btn_encerrar = Button(text="⛔ Encerrar Executor")
        btn_encerrar.bind(on_press=lambda x: self.encerrar_executor())

        botoes.add_widget(btn_status)
        botoes.add_widget(btn_iniciar)
        botoes.add_widget(btn_encerrar)

        self.add_widget(botoes)

    def obter_status(self):
        def thread_func():
            try:
                r = requests.get(f"{self.base_url}/status", timeout=5)
                if r.ok:
                    dados = r.json()
                    logs = "\n".join(dados.get("logs", []))
                    self.log_box.text = logs
                else:
                    self.log_box.text = f"Erro ao obter status: Código {r.status_code}"
            except Exception as e:
                self.log_box.text = f"Erro ao obter status:\n{e}"
        threading.Thread(target=thread_func).start()

    def iniciar_envio(self):
        def thread_func():
            try:
                requests.post(f"{self.base_url}/iniciar", timeout=5)
                self.log_box.text = "▶️ Envio iniciado manualmente!"
            except Exception as e:
                self.log_box.text = f"Erro ao iniciar envio:\n{e}"
        threading.Thread(target=thread_func).start()

    def encerrar_executor(self):
        def thread_func():
            try:
                requests.post(f"{self.base_url}/encerrar", timeout=5)
                self.log_box.text = "⛔ Executor encerrado."
            except Exception as e:
                self.log_box.text = f"Erro ao encerrar:\n{e}"
        threading.Thread(target=thread_func).start()

class OperadorApp(App):
    def build(self):
        return PainelOperador()

if __name__ == "__main__":
    OperadorApp().run()

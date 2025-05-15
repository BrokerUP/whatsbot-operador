import os
import json
import requests
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle

Window.size = (360, 640)  # Simulação de celular

def carregar_ip():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f).get("ip", "http://127.0.0.1:5000")
    return "http://127.0.0.1:5000"

def carregar_nome_empreendimento():
    if os.path.exists("status_envio.json"):
        with open("status_envio.json", "r") as f:
            return json.load(f).get("empreendimento", "Sem nome")
    return "Sem nome"

class PainelOperador(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=10, spacing=10, **kwargs)
        self.base_url = carregar_ip()
        self.empreendimento = carregar_nome_empreendimento()

        # Logo
        self.logo = Image(source="logo.png", size_hint=(1, 0.2), allow_stretch=True)
        self.add_widget(self.logo)

        # Nome do empreendimento
        self.titulo = Label(text=self.empreendimento, size_hint=(1, 0.08),
                            color=(0, 0, 0, 1), bold=True, font_size='18sp')
        self.add_widget(self.titulo)

        # Área do log
        self.log_box = Label(size_hint_y=None, text_size=(Window.width * 0.9, None),
                             color=(1, 1, 1, 1), font_size='14sp', valign="top", halign="left")
        self.log_box.bind(texture_size=self._update_log_height)

        self.scroll = ScrollView(size_hint=(1, 0.6), scroll_type=['bars', 'content'])
        self.scroll.add_widget(self.log_box)

        # Fundo preto com canvas.before
        with self.scroll.canvas.before:
            Color(0, 0, 0, 1)  # Preto
            self.rect = Rectangle(size=self.scroll.size, pos=self.scroll.pos)
        self.scroll.bind(size=self._update_rect, pos=self._update_rect)

        self.add_widget(self.scroll)

        # Botão de menu
        self.botao_menu = Button(text="📱 Menu", size_hint=(1, 0.1),
                                 background_color=(0.1, 0.3, 0.7, 1), color=(1, 1, 1, 1),
                                 bold=True, background_normal='',
                                 font_size='16sp')
        self.botao_menu.bind(on_press=self.abrir_menu)
        self.add_widget(self.botao_menu)

    def _update_rect(self, instance, value):
        self.rect.pos = self.scroll.pos
        self.rect.size = self.scroll.size

    def _update_log_height(self, instance, size):
        self.log_box.height = size[1]

    def abrir_menu(self, *args):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        botoes = [
            ("🔍 Obter Status", self.obter_status),
            ("🚀 Iniciar Envio Manual", self.iniciar_envio),
            ("🛑 Encerrar Executor", self.encerrar_executor)
        ]

        for texto, callback in botoes:
            btn = Button(text=texto, size_hint=(1, None), height=50,
                         background_color=(0.1, 0.3, 0.7, 1), color=(1, 1, 1, 1),
                         background_normal='', bold=True)
            btn.bind(on_press=callback)
            layout.add_widget(btn)

        self.popup = Popup(title="Menu de Ações", content=layout,
                           size_hint=(0.9, 0.6))
        self.popup.open()

    def append_log(self, texto):
        self.log_box.text += f"{texto}\n"

    def obter_status(self, *args):
        if hasattr(self, 'popup'):
            self.popup.dismiss()
        try:
            r = requests.get(f"{self.base_url}/status")
            if r.ok:
                dados = r.json()
                logs = "\n".join(dados.get("logs", []))
                self.log_box.text = logs
            else:
                self.append_log(f"Erro ao obter status: código {r.status_code}")
        except Exception as e:
            self.append_log(f"Erro ao obter status:\n{e}")

    def iniciar_envio(self, *args):
        if hasattr(self, 'popup'):
            self.popup.dismiss()
        try:
            requests.post(f"{self.base_url}/iniciar")
            self.append_log("🚀 Envio iniciado manualmente!")
        except Exception as e:
            self.append_log(f"Erro ao iniciar envio:\n{e}")

    def encerrar_executor(self, *args):
        if hasattr(self, 'popup'):
            self.popup.dismiss()
        try:
            requests.post(f"{self.base_url}/encerrar")
            self.append_log("🛑 Executor encerrado.")
        except Exception as e:
            self.append_log(f"Erro ao encerrar:\n{e}")

class AppOperador(App):
    def build(self):
        return PainelOperador()

if __name__ == "__main__":
    AppOperador().run()

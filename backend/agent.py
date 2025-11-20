import subprocess
import sys
import traceback
import io
import os
import re
from contextlib import redirect_stdout
import google.generativeai as genai

class JarvisAgent:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")

        if self.api_key:
            genai.configure(api_key=self.api_key)

            # NOVO MODELO (o antigo gemini-1.5-flash foi descontinuado)
            self.model = genai.GenerativeModel("gemini-2.5-flash")

            # Inicializa chat
            self.chat = self.model.start_chat(history=[])
        else:
            print("⚠️ GEMINI_API_KEY não encontrada — modo sem IA ativado.")
            self.model = None
            self.chat = None

    def execute_code(self, code):
        """Executa código Python enviado pelo modelo."""
        stdout = io.StringIO()
        try:
            with redirect_stdout(stdout):
                exec(code, {})
            return stdout.getvalue()
        except Exception as e:
            return f"Erro ao executar código:\n{traceback.format_exc()}"

    def ask(self, message: str) -> str:
        """Fluxo principal do Jarvis."""
        if not self.chat:
            return "GEMINI_API_KEY ausente. Configure para usar IA."

        response = self.chat.send_message(message)
        text = response.text

        # Procurar blocos de código
        code_match = re.search(r"```python(.*?)```", text, re.DOTALL)

        current_turn = 0
        MAX_TURNS = 3

        while code_match and current_turn < MAX_TURNS:
            code = code_match.group(1).strip()

            # 3. Executar o código
            execution_result = self.execute_code(code)

            # 4. Mandar o resultado de volta para o modelo
            follow_up_msg = (
                f"Resultado da execução do código:\n{execution_result}\n\n"
                "Use esse resultado para continuar ajudando o usuário."
            )

            response = self.chat.send_message(follow_up_msg)
            text = response.text

            # Procurar novo código
            code_match = re.search(r"```python(.*?)```", text, re.DOTALL)
            current_turn += 1

        return text

agent = JarvisAgent()

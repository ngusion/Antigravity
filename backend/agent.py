import subprocess
import sys
import traceback
import io
import os
import re
from contextlib import redirect_stdout

import google.generativeai as genai


class JarvisAgent:
    def __init__(self) -> None:
        # Lê a chave da API do Gemini das variáveis de ambiente
        self.api_key = os.environ.get("GEMINI_API_KEY")

        self.model = None
        self.chat = None

        if self.api_key:
            genai.configure(api_key=self.api_key)

            # Modelo antigo gemini-1.5-flash foi descontinuado.
            # Aqui usamos um modelo atual (ajuste se quiser outro).
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            self.chat = self.model.start_chat(history=[])
        else:
            # Backend continua subindo, mas o chat avisa que falta chave.
            print("GEMINI_API_KEY não encontrada. Jarvis rodará sem IA.")

    def execute_code(self, code: str) -> str:
        """
        Executa código Python enviado dentro de um bloco ```python```.

        A saída de print() é capturada e retornada como string.
        """
        stdout = io.StringIO()
        try:
            local_scope = {}
            with redirect_stdout(stdout):
                exec(code, local_scope, local_scope)
            output = stdout.getvalue()
            return output if output.strip() else "Código executado com sucesso (sem saída)."
        except Exception:
            return "Erro ao executar código:\n" + traceback.format_exc()

    async def process_message(self, user_message: str) -> str:
        """
        Método chamado pela API (main.py).

        - Envia a mensagem do usuário para o Gemini.
        - Se o modelo devolver blocos ```python```, executa o código.
        - Envia o resultado da execução de volta para o modelo.
        """
        if not self.model or not self.chat:
            return "Erro: GEMINI_API_KEY não está configurada no servidor."

        # Adiciona contexto com lista de arquivos enviados (pasta uploads/)
        files_context = ""
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            files = [
                f
                for f in os.listdir(uploads_dir)
                if os.path.isfile(os.path.join(uploads_dir, f))
            ]
            if files:
                files_context = (
                    "\n[System Note: Arquivos disponíveis em uploads/: "
                    + ", ".join(files)
                    + "]\n"
                )

        # 1. Primeira chamada ao modelo
        response = self.chat.send_message(user_message + files_context)
        text = response.text or ""

        # 2. Procurar blocos de código python na resposta
        code_match = re.search(r"```python(.*?)```", text, re.DOTALL)

        max_turns = 3  # evita loops infinitos
        current_turn = 0

        # Enquanto o modelo continuar mandando código e não estourar o limite
        while code_match and current_turn < max_turns:
            code_block = code_match.group(1).strip()
            print(f"Executando código recebido do modelo:\n{code_block}\n")

            # 3. Executa o código
            execution_result = self.execute_code(code_block)

            # 4. Envia o resultado novamente para o modelo
            follow_up_msg = (
                "Resultado da execução do código:\n"
                f"{execution_result}\n\n"
                "Use esse resultado para continuar ajudando o usuário. "
                "Se precisar, você pode gerar mais código Python em novos blocos ```python```."
            )

            response = self.chat.send_message(follow_up_msg)
            text = response.text or ""

            # 5. Verifica se veio um novo bloco de código
            code_match = re.search(r"```python(.*?)```", text, re.DOTALL)
            current_turn += 1

        return text


# Instância global usada pelo FastAPI em main.py
agent = JarvisAgent()

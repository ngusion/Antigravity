import subprocess
import sys
import traceback
import io
import os
from contextlib import redirect_stdout
import google.generativeai as genai

class JarvisAgent:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.chat = self.model.start_chat(history=[])
        else:
            self.model = None
            print("Warning: GEMINI_API_KEY not found.")

        self.system_prompt = """
        You are Jarvis, an advanced autonomous AI agent running in a cloud environment.
        Your goal is to help the user with ANY task, especially programming, data analysis, and file manipulation.

        ENVIRONMENT:
        - You are running on a Linux server (Render).
        - Working Directory: `/app`
        - File Storage: `/app/uploads` (All uploaded files are here, and you should save output files here).
        
        CAPABILITIES:
        1. **Execute Python Code**: You can write and execute Python code to solve problems.
        2. **Install Libraries**: You can install new libraries using `!pip install <library>` inside your code blocks.
        3. **Internet Access**: You have access to the internet via Python `requests`.
        4. **File Operations**: You can read/write files in `uploads/`. ALWAYS check if a file exists before reading.
        
        PROTOCOL:
        1. **Analyze the Request**: Determine if you need to run code.
        2. **Clarify if Vague**: If the request is too vague (e.g., "fix the pdf"), ask for clarification (e.g., "What specific changes do you need?").
        3. **Autonomous Execution**: If the request is clear, PROCEED IMMEDIATELY. Do not ask for permission to run code.
        4. **File Output**: If you generate a file, save it to `uploads/` and tell the user the filename so they can download it.
        
        CODE FORMAT:
        ```python
        # !pip install pandas  <-- Install dependencies first if needed
        import pandas as pd
        # Your code here
        print("Result")
        ```
        
        EXAMPLE:
        User: "Convert report.pdf to text."
        You: 
        ```python
        !pip install pypdf
        from pypdf import PdfReader
        reader = PdfReader("uploads/report.pdf")
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\\n"
        with open("uploads/report.txt", "w") as f:
            f.write(text)
        print("Converted report.pdf to report.txt")
        ```
        System: (Returns output)
        You: "I have converted the PDF to text. You can download it as [report.txt](/api/download/report.txt)."
        """
        
        # Initialize chat with system prompt if possible, or just prepend it
        if self.model:
            self.chat.history.append({'role': 'user', 'parts': [self.system_prompt]})
            self.chat.history.append({'role': 'model', 'parts': ["I understand. I am ready to assist."]})

    def execute_code(self, code: str) -> str:
        """
        Executes arbitrary Python code.
        """
        output_buffer = []
        
        lines = code.split('\n')
        clean_lines = []
        for line in lines:
            if line.strip().startswith('!pip install'):
                pkg = line.strip().split(' ')[2:]
                pkg_str = ' '.join(pkg)
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", *pkg])
                    output_buffer.append(f"Successfully installed {pkg_str}")
                except Exception as e:
                    output_buffer.append(f"Failed to install {pkg_str}: {str(e)}")
            else:
                clean_lines.append(line)
        
        code_to_run = '\n'.join(clean_lines)
        
        f = io.StringIO()
        try:
            with redirect_stdout(f):
                # Use a persistent local scope if we want variables to survive between turns?
                # For now, fresh scope is safer/simpler, but persistent is better for "notebook" feel.
                # Let's try to use a persistent dict if we were keeping state, but here we just run.
                exec(code_to_run, globals())
            result = f.getvalue()
            return "\n".join(output_buffer) + "\n" + (result if result else "Code executed successfully (no output).")
        except Exception as e:
            return "\n".join(output_buffer) + f"\nError executing code:\n{traceback.format_exc()}"

    async def process_message(self, user_message: str) -> str:
        if not self.model:
            return "Error: GEMINI_API_KEY not configured on server."

        # 1. Send user message to LLM
        # Inject file list into context
        files_context = ""
        if os.path.exists("uploads"):
            files = os.listdir("uploads")
            if files:
                files_context = f"\n[System Note: Available files in uploads/: {', '.join(files)}]\n"
        
        response = self.chat.send_message(user_message + files_context)
        text = response.text
        
        # 2. Check for code blocks
        # Simple parser: look for ```python ... ```
        import re
        code_match = re.search(r"```python(.*?)```", text, re.DOTALL)
        
        max_turns = 3 # Avoid infinite loops
        current_turn = 0
        
        while code_match and current_turn < max_turns:
            code = code_match.group(1)
            print(f"Executing code:\n{code}") # Log for server
            
            # 3. Execute code
            execution_result = self.execute_code(code)
            
            # 4. Send result back to LLM
            follow_up_msg = f"Code Execution Result:\n{execution_result}\n\nPlease use this result to answer the user, or write more code if needed."
            response = self.chat.send_message(follow_up_msg)
            text = response.text
            
            # Check again for code
            code_match = re.search(r"```python(.*?)```", text, re.DOTALL)
            current_turn += 1
            
        return text

agent = JarvisAgent()

import os, json, subprocess, textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../workspace/aynaghor"))

def write(rel_path, content):
    full = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content))

# ---------- Core package ----------
write("core/__init__.py", "")
write("core/engine.py", """
import os
from .config import settings

class Engine:
    def __init__(self):
        self.use_gemini = settings.get('USE_GEMINI', False)
        # placeholder clients – will be filled later
        self.gemini_client = None
        self.localai_client = None

    def route(self, prompt: str) -> str:
        if self.use_gemini:
            return self.gemini_client.generate(prompt)
        else:
            return self.localai_client.generate(prompt)
""")

# ---------- Config ----------
write("config.py", """
from dotenv import load_dotenv
import os
load_dotenv()

settings = {
    "USE_GEMINI": os.getenv("USE_GEMINI", "false").lower() == "true",
    "GEMINI_KEY": os.getenv("GEMINI_KEY", ""),
    "LLM_HOST": os.getenv("LLM_HOST", "http://host.docker.internal:8000"),
}
""")

# ---------- Modules ----------
modules = {
    "voice.py": "# placeholder for Whisper / GTTS integration",
    "image.py": "# placeholder for Pillow / Diffusers integration",
    "memory.py": "# simple JSON vector store placeholder",
    "gemini.py": "# wrapper around Google Gemini API",
    "localai.py": "# wrapper around a local GGUF model (host.docker.internal:8000)"
}
for name, content in modules.items():
    write(f"modules/{name}", content)

# ---------- UI (Streamlit) ----------
write("ui/app.py", """
import streamlit as st
from core.engine import Engine

st.title('AYNAGH0R – Dark & Erotic AI')

prompt = st.text_area('Your prompt')
if st.button('Generate'):
    eng = Engine()
    resp = eng.route(prompt)
    st.write(resp)
""")

# ---------- Requirements ----------
write("requirements.txt", """
fastapi==0.110.*
uvicorn[standard]==0.27.*
streamlit==1.38.*
python-dotenv==1.0.*
# optional – will be installed later by the agent when needed
""")

# ---------- README ----------
write("README.md", """
# AYNAGH0R

A unified intelligence architecture for dark‑fantasy / erotic storytelling.

## Quick start
```bash
# 1️⃣ Install dependencies
pip install -r requirements.txt

# 2️⃣ Set up environment
cp .env.example .env
# Edit .env with your API keys

# 3️⃣ Run the application
streamlit run ui/app.py --server.port=8501
```

## Architecture diagram
```mermaid
graph TD;
    User[User Interface] -->|submits prompts| Engine[Core Engine];
    Engine -->|routes to| Gemini[Google Gemini API];
    Engine -->|routes to| LocalAI[Local AI Models];
    Engine -->|manages| Memory[Conversation Memory];
    UI[Streamlit] --> Engine;
```
""")

print("Generation complete. Commit the new workspace.")
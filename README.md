# 🧩 Comunicação Sem Barreiras

## 🚀 Como rodar o projeto localmente

```bash
# 1️⃣ Clonar o repositório
git clone https://github.com/seuusuario/comunicacao-sem-barreiras.git
cd comunicacao-sem-barreiras

# 2️⃣ Criar e ativar o ambiente virtual (Windows)
python -m venv .venv
.\.venv\Scripts\activate

# (macOS/Linux)
# python3 -m venv .venv
# source .venv/bin/activate

# 3️⃣ Instalar dependências
pip install flask flask_sqlalchemy

# 4️⃣ Criar o banco de dados (v2.db)
python
>>> from app import db
>>> db.create_all()
>>> exit()

# 5️⃣ Rodar o servidor Flask
flask --app app run --debug
# ou
python app.py

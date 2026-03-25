# Lightweight Python
FROM python:3.11-slim

WORKDIR /app

# 👉 Step 1: install dependencies FIRST (cache friendly)
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 👉 Step 2: copy rest of code
COPY . .

# 👉 Step 3: run script
RUN python fix_models.py

# 👉 Step 4: run app
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --upgrade pip

RUN pip install numpy==1.24.3 --only-binary=:all:
RUN pip install scikit-learn==1.4.2 xgboost==2.0.3 joblib==1.5.2
RUN pip install -r requirements.txt --no-deps

RUN python fix_models.py

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
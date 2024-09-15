FROM python:3.12-slim

WORKDIR /app

RUN pip install pipenv

COPY data/yoga_poses.csv data/yoga_poses.csv
COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --deploy --ignore-pipfile --system

COPY yoga-companion .

EXPOSE 5000
EXPOSE 8501

CMD ["sh", "-c", "python app.py & streamlit run streamlit_app.py"]

FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ /app/scripts/
COPY helper_functions/ /app/helper_functions
COPY run.py .

ENTRYPOINT [ "python", "run.py" ]

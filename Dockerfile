FROM python:3.10

WORKDIR /fr_system
COPY ./requirements-base.txt /fr_system/requirements-base.txt
RUN pip install --no-cache-dir --upgrade -r /fr_system/requirements.txt

COPY ./src /fr_system/src
RUN export PYTHONPATH="${PYTHONPATH}:/fr_system"

CMD ["python3", "/fr_system/src/main.py"]

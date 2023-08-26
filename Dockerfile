# Instalar el navegador
FROM python:3.11.4-slim-bullseye as install-browser
RUN apt-get update \
    && apt-get install -y \
    chromium chromium-driver \
    && chromedriver --version

# Instalar las dependencias de Python
FROM install-browser as gpt-researcher-install
ENV PIP_ROOT_USER_ACTION=ignore
RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Configurar el entorno final
FROM gpt-researcher-install AS gpt-researcher
RUN useradd -ms /bin/bash gpt-researcher \
    && chown -R gpt-researcher:gpt-researcher /usr/src/app
USER gpt-researcher
COPY ./ ./
EXPOSE 8000
CMD sh -c "uvicorn api.main:app --host 0.0.0.0 --port 8000"

FROM python:3.9

WORKDIR /src

ENV AWS_SECRETS_MANAGER_SECRET_NAME prod/kahuna
ENV AWS_SECRETS_MANAGER_SECRET_REGION_NAME us-east-1
ENV SECRETS_KEY_DISCORD_TOKEN kahuna-discord-token
ENV SECRETS_KEY_DISCORD_CHANNEL_ID kahuna-discord-channel-id

COPY /src .

RUN pip install -r requirements.txt

CMD ["python", "kahuna.py"]






import json
from flask import Flask, request
from discord.ext import commands
import discord
import datetime
import os
import boto3
import logging
from botocore.exceptions import ClientError

msg_args = None
DISCORD_TOKEN = None
DISCORD_CHANNEL_ID = None
app = Flask(__name__)



def get_secrets():

    secret_name = os.getenv('AWS_SECRETS_MANAGER_SECRET_NAME')
    region_name = os.getenv('AWS_SECRETS_MANAGER_SECRET_REGION_NAME')

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)


    # Decrypts secret using the associated KMS key.
    secrets = json.loads(get_secret_value_response['SecretString'])

    return secrets[os.getenv('SECRETS_KEY_DISCORD_TOKEN')],secrets[os.getenv('SECRETS_KEY_DISCORD_CHANNEL_ID')]




@app.route('/')
def index():
    return json.dumps({'index': None})


@app.route('/', methods=['POST'])
def data():
    rq = request.get_json()

    global msg_args
    if 'message' in rq:
        msg_args = str(rq['message'])
    else:
        msg_args = str(rq)
    bot = MyClient(command_prefix='!', intents=discord.Intents().all())

    global DISCORD_TOKEN
    bot.run(DISCORD_TOKEN)

    return rq


class MyClient(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):

        global msg_args
        global DISCORD_CHANNEL_ID






        channel = self.get_channel(int(DISCORD_CHANNEL_ID))

        x = f'{str(msg_args)}'

        await channel.send(x)
        await self.close()

    async def close(self):
        await super().close()

DISCORD_TOKEN, DISCORD_CHANNEL_ID = get_secrets()
app.run(host='0.0.0.0')

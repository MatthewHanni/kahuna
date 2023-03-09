import json
from flask import Flask, request
from discord.ext import commands
import discord
import os
import boto3

msg_args = None
DISCORD_TOKEN = None
DISCORD_CHANNEL_ID = None
app = Flask(__name__)



def get_secrets():
    """
    Returns secrets from AWS SecretsManager
            Returns:
                    secrets (tuple): Discord Token, Discord Channel ID
    """


    secret_name = os.getenv('AWS_SECRETS_MANAGER_SECRET_NAME')
    region_name = os.getenv('AWS_SECRETS_MANAGER_SECRET_REGION_NAME')
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secrets = json.loads(get_secret_value_response['SecretString'])
    return secrets[os.getenv('SECRETS_KEY_DISCORD_TOKEN')],secrets[os.getenv('SECRETS_KEY_DISCORD_CHANNEL_ID')]




@app.route('/')
def index():
    """
        Handling for a standard HTTP REQUEST call
            Returns:
                    dict (dict): JSON with an empty index
    """
    return json.dumps({'index': None})


@app.route('/', methods=['POST'])
def data():
    """
    Handling for an HTTP POST command
            Returns:
                    rq (dict): JSON object
    """

    # Grab the JSON object that was passed as part of the data in the POST call.
    rq = request.get_json()

    # Argument passing via static variables.
    # Horrible practice but the invocation the different functions is complicated.
    # This is a hacky way to get it to work.
    global msg_args

    if 'message' in rq and len(rq.keys()) == 1:
        #It is generally expected that the JSON will be formatted like {'message': 'blahblah'}, so if we see the key 'message',
        # we pull out the value so that we can send a message without it looking like JSON.
        msg_args = str(rq['message'])
    else:
        # In all other scenarios, we just convert the JSON to a string since it is going to be sent as a flat message.
        msg_args = str(rq)
    bot = DiscordBot(command_prefix='!', intents=discord.Intents().all())

    global DISCORD_TOKEN
    # Invoke the Discord bot
    bot.run(DISCORD_TOKEN)

    return rq


class DiscordBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        """
        Send a message to a channel. This function is executed when bot.run() is called.
        """

        global msg_args
        global DISCORD_CHANNEL_ID
        # Create a connection to the channel based on the channel ID
        channel = self.get_channel(int(DISCORD_CHANNEL_ID))

        await channel.send(msg_args)
        await self.close()

    async def close(self):
        await super().close()


# Retrieve the secrets and set them to these global variables
DISCORD_TOKEN, DISCORD_CHANNEL_ID = get_secrets()

# Start the Flask server
app.run(host='0.0.0.0')

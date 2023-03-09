# Kahuna Flask API for Discord Messages

## Description and Motivation
I need a lightweight client-side solution to push messages (alerts, errors, notifications, debugging information, etc.) programmatically. SMS only pushes to phones, but there are many cases where I'll want to copy, analyze, or search the text and history at my desktop. Email is clunky and is too heavy for this use case. Discord is a logical choice of medium: it is free and ubiquitous - there is a web interface, mobile app with push notifications, and native desktop client software. It was also selected for it's extensibility: there are a wide number of features in Discord which can make for great future feature additions

The native Discord API requires a WebSocket to send messages to a channel. This isn't something I want to maintain and recreate in every application that I write which requires alerting. The question I was asking myself was - *"how can I simplify sending a Discord message via a REST API the same way that I would use Twilio or SNS?"*

I created a Flask API which can accept a JSON message as a parameter. A WebSocket connection to Discord is then created and the message posted automatically. The service is Dockerized and deployed to EC2.

The notes provided below are written in the third person but are mostly for record-keeping.

## Usage
A message can be sent simply via the requests API

    import requests
    endpoint_url = "http://my-fake-endpoint.xyz:5000"
    message = "Greetings! I'm Space Ghost."
    requests.post(url=endpoint_url, json={'message':message})

Alternatively, we could limit ourselves to native Python (or, of course, any other language or framework that allows for REST).

    import json, urllib
    endpoint_url = "http://my-fake-endpoint.xyz:5000"
    message = "Greetings! I'm Space Ghost."
    params = json.dumps({'message':message}).encode('utf8')
    req = urllib.request.Request(endpoint_url, data=params, headers={'content-type':  'application/json'})
    response = urllib.request.urlopen(req)

## Installation and Setup

### Discord
We need to create our bot and generate an access token from Discord. 
1. Click 'New Application' on https://discord.com/developers/applications and give it a name.
2. After the application is created, click on it under the 'My Applications' section.
3. On the left-hand panel, click on the 'Bot' section and create 'Build a Bot'
4. On the Bot page, there will be an option to 'View Token'. Record this in a safe place.
5. Uncheck the 'Public Bot' box and save changes.
6. On the left-hand panel, click OAuth2 > URL Generator
7. Select the 'bot' scope, and any permissions. Required permissions are 'Send Messages'
8. Copy the URL that is generated and paste it into the web browser. Discord will prompt you to select a server to add the bot to. If you do not currently have a server, it is free and easy to create one. You will need to be the administrator of the server to be able to add your bot.

### Domain Configuration (Optional)
If you have a domain name, you can set point your domain to your EC2 IP address. If/when your EC2 IP address changes, you will only need to update your domain registrar's records instead of updating the IP address in every script.
Every registrar's system is different but setting the External Hosts (A,AAAA) DNS records to "discord.your-domain.net" and pointing them to the EC2 IP address will mean that you can reference your endpoint by discord.your-domain.net:5000.

### AWS Secrets Manager
Storing your secrets in AWS simplifies key rotations.
From within the AWS console:
1. Visit the SecretsManager landing page and click 'Store a new Secret'.
2. Name your secret prod/kahuna (if you choose not to, you will need to update the Dockerfile)
3. Set the region for your secret to us-east-1 (if you choose not to, you will need to update the Dockerfile)
4. Select the Secret type : Other type of secret
5. Record our Key/value pairs for our token (kahuna-discord-token) and the channel ID (kahuna-discord-channel-id)


### EC2
Within your region of choice, create a new AWS EC2 instance.
1.  Assign a name (kahuna)
2.  Select an AMI (Amazon Linux)
3.  Select an instance type (t3a.nano)
4.  Network settings:
	a.  Allow ssh traffic from anywhere
	b.  Allow HTTPS traffic from the internet
	c.  Allow HTTP traffic from the internet

Once your instance is configured, you will launch it and run the follwoing commands.
5.  sudo apt update
6.  sudo apt install apt-transport-https ca-certificates curl software-properties-common
7.  curl -fsSL [https://download.docker.com/linux/ubuntu/gpg](https://download.docker.com/linux/ubuntu/gpg) | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
8.  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] [https://download.docker.com/linux/ubuntu](https://download.docker.com/linux/ubuntu) $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
9.  sudo apt update
10.  apt-cache policy docker-ce
11.  sudo apt install docker-ce
12.  sudo systemctl status docker
13.  sudo docker run -d -p 5000:5000 [DOCKER IMAGE] 



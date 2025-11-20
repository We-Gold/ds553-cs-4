---
title: DS 553 Case Study 1
emoji: 💬
colorFrom: yellow
colorTo: purple
sdk: docker
app_port: 7860
tags:
  - streamlit
app_file: app.py
pinned: false
hf_oauth: true
hf_oauth_scopes:
- inference-api
---

## Ngrok URL

https://filmlike-ungaudily-salvador.ngrok-free.dev/

Grafana: https://choregraphically-unvendable-brendan.ngrok-free.dev/

## Running Docker on Server
`docker-compose down`, then `docker-compose up -d`

## Running Locally

Run with Docker Compose:
`docker-compose up --build`

Easier running:

- `pip install -r requirements.txt`
- `python app.py`

For all development, run locally.

To do this, use Docker!

Install:
https://docs.docker.com/desktop/

If on Windows, install WSL first!

https://learn.microsoft.com/en-us/windows/wsl/install

Once you are ready, run it in the following way:

Make sure Docker Desktop is running.

Then,

`./run-dev.sh`

You might need to do `chmod +x run-dev.sh`

## Deployment and Monitoring Scripts

Deply to Prof. Paffenroth's server:

`./deploy.sh -d <your_key>`

Red team other people's deployments:

`./red-team-script.sh`
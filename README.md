# Simple Clip Uploader

This is a simple clip uploader designed to work with Discord embeds.

Discord recently changed their maximum upload file limit to a mere 10 mb, so I created this simple, self-hostable app to upload more. On top of that, Discord does not support AV1 decoding, despite it being far superior to H.264.

## Usage
The recommended usage is via docker. The repo has a sample [docker-compose.yml](/docker-compose.yml)

Set a password in the docker-compose, and then just run `docker compose up` to deploy

**NOTE**: If you plan on encoding/compressing videos before upload with Handbrake, make sure "Web Optimized" is enabled. This tells the browser to not wait for the whole video to load before playing.

![Upload Screen](https://i.imgur.com/GouYewr.png)
![Video Screen](https://github.com/user-attachments/assets/5ce4d098-d37c-458d-87f2-f46fc087670a)
![discord embed](https://github.com/user-attachments/assets/73a1aa70-bfb0-4882-a527-04a88079d303)

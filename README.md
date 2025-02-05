# Plex Logger
This program uses the Python Plex API and discord.py to watch a specified Plex server for periodic changes, and generate changelogs to be sent via Discord or printed to a text file.

## How to Get Started
1. Set up a Discord bot via the Discord Developer portal and invite it to your server
2. Clone this repo and populate the .env file with your Discord bot token, your Plex token, the URL of your Plex server, and the ID of the Discord channel you want the changelogs printed in.
3. Ensure that your bot has the proper permissions in the Discord server.
4. Build the docker image by running `docker build --tag plex-logger .`
5. Run the docker image by running `docker run plex-logger`

## Notes
- Anything in 'notes.txt' will be added to the top of the upcoming changelog, and then the 'notes.txt' file's contents will be cleared.
- The previous log date is determined by looking at the most recent log file in /logs.

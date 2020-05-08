# pyEBOT
Discord bot that automatically handles notifications related to FR17 events.

Note: This project is tailored for a specific discord server. Code is in part open for transparancy reasons.
To make the bot work, some setup is required.

Python environment:
A requirements.txt file is provided. If there are any issues installing from req try to install the following modules using pip.
discord.py
gspread
oauth2client
pydantic

To connect to google sheets you will need to setup authentication. The credentials file should be named creds.json and should be located in the root of the project.
To run the bot you will need to make a discord bot and generate a token. Store the actual token in a file called token.json. Incapsulate the token with quote marks.(") The token.json file should be stored in the root of the project.

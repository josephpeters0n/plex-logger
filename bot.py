import asyncio, datetime, discord, os, re
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from dotenv import load_dotenv
from plexapi.server import PlexServer

# Setup
load_dotenv()
client = commands.Bot(command_prefix="/", intents=discord.Intents.all())
LOGS_DIR = "logs"

# Start the bot
async def main():
    async with client:
        await client.start(os.getenv("DISCORD_TOKEN"))

# Ensures the logs directory exists
def ensure_logs_dir():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

# Reads the date from the most recent log file's filename.
# Expected filename format: changelog_YYYY-MM-DD.txt
def read_log_date():
    ensure_logs_dir()
    files = [f for f in os.listdir(LOGS_DIR) if f.startswith("changelog_") and f.endswith(".txt")]
    dates = []
    for fname in files:
        try:
            date_str = fname[len("changelog_"):-len(".txt")]
            dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
        except Exception:
            pass
    if dates:
        return max(dates)
    # Default to 7 days ago if no log file exists
    return datetime.now() - timedelta(days=7)

# Writes the given log body into a text file named using new_date.
def update_log_date(new_date, body):
    ensure_logs_dir()
    filename = os.path.join(LOGS_DIR, f"changelog_{new_date.strftime('%Y-%m-%d')}.txt")
    with open(filename, 'w') as f:
        f.write(body)

# Formats a list of numbers into a condensed string range
def format_numbers(arr):
    if not arr: return ""
    result = []
    start = end = arr[0]
    for num in arr[1:]:
        if num == end + 1:
            end = num
        else:
            result.append(f"{start:02d}" if start == end else f"{start:02d}-{end:02d}")
            start = end = num
    result.append(f"{start:02d}" if start == end else f"{start:02d}-{end:02d}")
    return ", ".join(result)

# Get the notes from the notes file then clears it
def get_notes(filepath='notes.txt'):
    try:
        with open(filepath, 'r+') as f:
            notes = f.readlines()
            f.truncate(0)
        if notes:
            return "Notes\n-----\n" + "".join(f"- {line}" for line in notes) + "\n\n"
    except FileNotFoundError:
        return ""
    return ""

# Constructs the movie section of the changelog from movies added after log_date.
def get_movie_section(movies, log_date):
    movieList = ""
    for m in movies.search():
        if m.addedAt >= log_date:
            edition = f" [{m.editionTitle}]" if m.editionTitle else ""
            movieList += f" + {m.title} ({m.year}){edition}\n"
    return "Movies\n------\n" + movieList + "\n\n" if movieList else ""

# Constructs the show section of the changelog from episodes added after log_date.
def get_show_section(series, log_date):
    showList = ""
    for s in series.search():
        episodes_by_season = {}
        for e in s.episodes():
            if e.addedAt >= log_date:
                m = re.search(r"[sS](\d{1,4})[eE](\d{1,4})", e.locations[0])
                if m:
                    season, episode = m.group(1), int(m.group(2))
                    episodes_by_season.setdefault(season, []).append(episode)
        if episodes_by_season:
            showList += f" o {s.title} ({s.year})\n"
            for season in sorted(episodes_by_season, key=int):
                episodes = format_numbers(sorted(set(episodes_by_season[season])))
                showList += f"    + S{season}E{episodes}\n"
    return "Shows\n-----\n" + showList + "\n\n" if showList else ""

# Check if it's time, then generate and send the changelog via Discord
@tasks.loop(minutes=5.0)
async def plexLog():
    # print("Performing Plex check!")
    log_date = read_log_date()
    now = datetime.now()
    if (now - log_date).days < 6:
        # print("Plex log conditions not met.")
        return
    
    # print("Plex log conditions met.")
    # print(f"Current: {now}, Log date: {log_date}, Diff: {(now-log_date).days} days")
    plex = PlexServer(os.getenv("PLEX_URL"), os.getenv("PLEX_TOKEN"))
    movies = plex.library.section('Movies')
    series = plex.library.section('Series')

    header = f"FULCRUM Automated Plex Changelog // {log_date.strftime('%Y/%m/%d')} - {now.strftime('%Y/%m/%d')}\n\n"
    body = "```\n" + header
    body += get_notes()
    body += get_movie_section(movies, log_date)
    body += get_show_section(series, log_date) + "```"

    new_date = now + timedelta(days=1)
    update_log_date(new_date, body)
    
    channel = client.get_channel(int(os.getenv("DISCORD_CHANNEL")))
    if len(body) < 2000:
        await channel.send(body)
    else:
        # Send changelog parts separately if too long
        for part in [header, get_notes(), get_movie_section(movies, log_date), 
                     get_show_section(series, log_date)]:
            if part.strip():
                await channel.send("```\n" + part + "\n```")
                await asyncio.sleep(1)
    # print("Sent plex logger message!")

# Bot online event
@client.event
async def on_ready():
    # print("Bot is online.")
    plexLog.start()

# Run the bot
asyncio.run(main())
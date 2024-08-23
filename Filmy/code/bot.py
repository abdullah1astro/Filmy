import discord 
from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv
from insertToDB import insert_or_update
from insertToDB import fetch_tmdb_description
from googletrans import Translator
from discord.ui import View

# Initialize the bot
intents = discord.Intents.default()
intents = discord.Intents.all()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix='-', intents=intents)

load_dotenv()
TOKEN = getenv("TOKEN")
translator = Translator()



def translate_description(text, target_language='ar'):
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return text




# MongoDB connection
client = MongoClient('mongodb+srv://astro251sq:king-dcv12yx@mydb.faqppaq.mongodb.net/?retryWrites=true&w=majority&appName=MyDB')
db = client['FilmyDB']  # Replace with your DB name
films_collection = db['films']
tv_series_collection = db['tv_series']

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        await bot.tree.sync()
        print("Commands synced successfully")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.command(name="movieList")
async def filmList(ctx):
    films = list(films_collection.find())
    if len(films) == 0:
        await ctx.send("No films found.")
    else:
        film_list = "\n".join([film['name'] for film in films])
        await ctx.send(f"Films:\n{film_list}")

@bot.command(name="tvList")
async def tvList(ctx):
    try:
        tv_series = list(tv_series_collection.find())
        if len(tv_series) == 0:
            await ctx.send("No TV series found.")
        else:
            tv_list = "\n".join([series['name'] for series in tv_series])
            await ctx.send(f"TV Series:\n{tv_list}")
    except Exception as e :
        print(f"error raised an exception: {e}")



def get_movie_choices():
    movies_list = films_collection.find({}, {"name": 1, "_id": 0})
    choices = [discord.app_commands.Choice(name=movie['name'], value=movie['name']) for movie in movies_list]
    print("Fetched Movies:", choices)  # Debugging
    return choices

@bot.tree.command(name="movie_list")
@app_commands.describe(
    movie="Choose a movie to get more information."
)
async def movie_list(interaction: discord.Interaction, movie: str):
    try:
        # Fetch the movie information from the database
        movie_info = films_collection.find_one({"name": movie})
        
        if movie_info:
            # Create the embed
            embed = discord.Embed(
                title=movie_info['name'],
                description=f"**English:** {movie_info.get('description_en', 'No description available')}\n"
                            f"**الْعَرَبِيَّةِ:** {movie_info.get('description_ar', 'لا توجد تفاصيل متوفرة')}",
                color=discord.Color.dark_red()  # You can change the color if desired
            )
            embed.add_field(name='Link', value=movie_info.get('link', 'No link available'))
            
            # Set small image (thumbnail) if available
            if 'thumbnail' in movie_info and movie_info['thumbnail']:
                embed.set_thumbnail(url=movie_info['thumbnail'])
            else:
                embed.add_field(name='Thumbnail', value='No thumbnail image found.')
            
            # Set large image if available
            if 'poster' in movie_info and movie_info['poster']:
                embed.set_image(url=movie_info['poster'])
            else:
                embed.add_field(name='Poster', value='No poster image found.')
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Movie not found.")
    
    except Exception as e:
        print(f"Error in movie_list command: {e}")
        await interaction.response.send_message("An error occurred while processing the request.")

@movie_list.autocomplete('movie')
async def movie_autocomplete(
    interaction: discord.Interaction, 
    current: str
) -> list[app_commands.Choice[str]]:
    # Fetching movies from the database
    movie_choices = get_movie_choices()
    
    # Filtering based on current input
    filtered_choices = [
        app_commands.Choice(name=choice.name, value=choice.value) 
        for choice in movie_choices if current.lower() in choice.name.lower()
    ]
    
    print("Filtered Choices:", filtered_choices)  # Debugging
    return filtered_choices





def get_tv_series_choices():
    series_list = tv_series_collection.find({}, {"name": 1, "_id": 0})
    choices = [discord.app_commands.Choice(name=series['name'], value=series['name']) for series in series_list]
    print("Fetched TV Series:", choices)  # Debugging
    return choices

@bot.tree.command(name="tv_list")
@app_commands.describe(
    tv_series="Choose a TV series to get more information."
)
async def tv_list(interaction: discord.Interaction, tv_series: str):
    try:
        # Fetch the TV series information from the database
        tv_show = tv_series_collection.find_one({"name": tv_series})
        
        if tv_show:
            # Create the embed
            embed = discord.Embed(
                title=tv_show['name'],
                description=f"**English:** {tv_show.get('description_en', 'No description available')}\n"
                            f"**الْعَرَبِيَّةِ:** {tv_show.get('description_ar', 'لا توجد تفاصيل متوفرة')}",
                color=discord.Color.dark_blue()  # You can change the color if desired
            )
            embed.add_field(name='Link', value=tv_show.get('link', 'No link available'))
            
            # Set small image (thumbnail) if available
            if 'thumbnail' in tv_show and tv_show['thumbnail']:
                embed.set_thumbnail(url=tv_show['thumbnail'])
            else:
                embed.add_field(name='Thumbnail', value='No thumbnail image found.')
            
            # Set large image if available
            if 'poster' in tv_show and tv_show['poster']:
                embed.set_image(url=tv_show['poster'])
            else:
                embed.add_field(name='Poster', value='No poster image found.')
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("TV series not found.")
    
    except Exception as e:
        print(f"Error in tv_list command: {e}")
        await interaction.response.send_message("An error occurred while processing the request.")


@tv_list.autocomplete('tv_series')
async def tv_series_autocomplete(
    interaction: discord.Interaction, 
    current: str
) -> list[app_commands.Choice[str]]:
    # Fetching TV series from the database
    series_choices = get_tv_series_choices()
    
    # Filtering based on current input
    filtered_choices = [
        app_commands.Choice(name=choice.name, value=choice.value) 
        for choice in series_choices if current.lower() in choice.name.lower()
    ]
    
    print("Filtered Choices:", filtered_choices)  # Debugging
    return filtered_choices



@bot.command(name="movieName")
async def filmName(ctx, *, name: str = None):
    if not name:
        await ctx.send("Please provide the name of the film. Usage: !filmName <film_name>")
        return

    film = films_collection.find_one({'name': {'$regex': f'^{name}$', '$options': 'i'}})
    if not film:
        await ctx.send("Film not found.")
    else:
        # Create the embed
        embed = discord.Embed(
            title=film['name'],
            description=f"**English:** {film.get('description_en', 'No description available')}\n"
                        f"**Arabic:** {film.get('description_ar', 'لا توجد تفاصيل متوفرة')}",
            color=discord.Color.dark_green()
        )
        embed.add_field(name='Link', value=film.get('link', 'No link available'))
        
        # Set small image (thumbnail) if available
        if 'thumbnail' in film and film['thumbnail']:
            embed.set_thumbnail(url=film['thumbnail'])
        else:
            embed.add_field(name='Thumbnail', value='No thumbnail image found.')
        
        # Set large image if available
        if 'poster' in film and film['poster']:
            embed.set_image(url=film['poster'])
        else:
            embed.add_field(name='Poster', value='No poster image found.')
        
        await ctx.send(embed=embed)


@bot.command(name="tvName")
async def tvName(ctx, *, name: str = None):
    if not name:
        await ctx.send("Please provide the name of the TV series. Usage: !tvName <tv_series_name>")
        return

    series = tv_series_collection.find_one({'name': {'$regex': f'^{name}$', '$options': 'i'}})
    if not series:
        await ctx.send("TV series not found.")
    else:
        # Create the embed
        embed = discord.Embed(
            title=series['name'],
            description=f"**English:** {series.get('description_en', 'No description available')}\n"
                        f"**Arabic:** {series.get('description_ar', 'لا توجد تفاصيل متوفرة')}",
            color=discord.Color.dark_green()
        )
        embed.add_field(name='Link', value=series.get('link', 'No link available'))
        
        # Set small image (thumbnail) if available
        if 'thumbnail' in series and series['thumbnail']:
            embed.set_thumbnail(url=series['thumbnail'])
        else:
            embed.add_field(name='Thumbnail', value='No thumbnail image found.')
        
        # Set large image if available
        if 'poster' in series and series['poster']:
            embed.set_image(url=series['poster'])
        else:
            embed.add_field(name='Poster', value='No poster image found.')
        
        await ctx.send(embed=embed)

@bot.tree.command(name="add")
@app_commands.describe(
    content_type="Type of content: 'movies' or 'series'.",
    name="Name of the movie or series.",
    description_en="English description of the content.",
    description_ar="Arabic description of the content (it will translate the en version).",
    link="Link to the content.",
    poster="Link to the poster image.",
    thumbnail="Link to the thumbnail image.",
)
@app_commands.choices(
    content_type=[
        discord.app_commands.Choice(name="movie", value="movie"),
        discord.app_commands.Choice(name="tv_series", value="tv_series")
    ],
    description_en=[
        discord.app_commands.Choice(name="useApi", value="api")
    ],
    description_ar=
    [
        app_commands.Choice(name = "useApi" , value="api")
    ],
)
@app_commands.checks.has_role('FilmyEditor')
async def add_content(interaction: discord.Interaction, content_type: str, name: str, description_en: str, description_ar: str ,link: str, poster: str, thumbnail: str):
    try:
        print(f"Received command: {content_type}, {name}, {description_en}, {description_ar}, {link}, {poster}, {thumbnail}")
        
        if content_type not in ['movie', 'tv_series']:
            await interaction.response.send_message("Invalid type. Please specify 'movie' or 'tv_series'.")
            return

        if content_type == 'movie':
            collection = films_collection
        else:
            collection = tv_series_collection

        # Use description from API if specified
        if description_en == 'api':
            description_en = fetch_tmdb_description(name, content_type == 'movie')
        if description_ar == "api":
            description_ar = translate_description(description_en) if description_en else "Translation failed"
            print(f"Translated description (AR): {description_ar}")

        # Prepare data to be inserted
        data = {
            "name": name,
            "description_en": description_en,
            "description_ar": description_ar,
            "link": link,
            "poster": poster,
            "thumbnail": thumbnail
        }
        
        print("Before database insertion")
        # Insert or update the record
        insert_or_update(collection, [data], useApi=(description_en == 'api'))
        
        print("After database insertion")
        # Sending a response after insertion
        if description_en == 'api':
            await interaction.response.send_message(f"Updated {content_type}: {name} with API description.")
        else:
            await interaction.response.send_message(f"Inserted new {content_type}: {name} with custom description.")
        print("Response sent successfully")
        
    except Exception as e:
        print(f"Error in add_content command: {e}")
        await interaction.response.send_message("An error occurred while processing the request.")



@bot.tree.command(name="custom_add")
@app_commands.describe(
    content_type="Type of content: 'movies' or 'series'.",
    name="Name of the movie or series.",
    description_en="English description of the content.",
    description_ar="Arabic description of the content.",
    link="Link to the content.",
    poster="Link to the poster image.",
    thumbnail="Link to the thumbnail image.",
)
@app_commands.choices(
    content_type=[
        discord.app_commands.Choice(name="movie", value="movie"),
        discord.app_commands.Choice(name="tv_series", value="tv_series")
    ]
)
@app_commands.checks.has_role('FilmyEditor')
async def custom_add(interaction: discord.Interaction, content_type: str, name: str, description_en: str, description_ar: str, link: str, poster: str, thumbnail: str):
    try:
        print(f"Received command: {content_type}, {name}, {description_en}, {description_ar}, {link}, {poster}, {thumbnail}")

        if content_type not in ['movie', 'tv_series']:
            await interaction.response.send_message("Invalid type. Please specify 'movie' or 'tv_series'.")
            return

        if content_type == 'movie':
            collection = films_collection
        else:
            collection = tv_series_collection

        # Prepare data to be inserted
        data = {
            "name": name,
            "description_en": description_en,
            "description_ar": description_ar,
            "link": link,
            "poster": poster,
            "thumbnail": thumbnail
        }
        
        print("Before database insertion")
        # Insert or update the record
        insert_or_update(collection, [data], useApi=False)
        
        print("After database insertion")
        # Sending a response after insertion
        await interaction.response.send_message(f"Inserted new {content_type}: {name} with custom descriptions.")
        print("Response sent successfully")
        
    except Exception as e:
        print(f"Error in custom_add command: {e}")
        await interaction.response.send_message("An error occurred while processing the request.")




class DeleteCollectionView(discord.ui.View):
    def __init__(self, collection_name: str):
        super().__init__()
        self.collection_name = collection_name

    @discord.ui.button(label="Confirm Deletion", style=discord.ButtonStyle.danger, custom_id="confirm_delete")
    async def confirm_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Check if the collection exists
        if self.collection_name in db.list_collection_names():
            db.drop_collection(self.collection_name)
            await button.response.send_message(f"Collection '{self.collection_name}' has been deleted.")
        else:
            await button.response.send_message("Collection not found. Deletion aborted.")

# Get the list of collection names for autocompletion
def get_collection_choices():
    collections = db.list_collection_names()
    choices = [discord.app_commands.Choice(name=col, value=col) for col in collections]
    return choices

# Slash command to initiate collection deletion with autocomplete
@bot.tree.command(name="delete_collections")
@app_commands.describe(
    collection="Choose a collection to delete."
)
async def delete_collections(interaction: discord.Interaction, collection: str):
    if collection not in db.list_collection_names():
        await interaction.response.send_message("Collection not found. Please try again.", ephemeral=True)
        return

    # Create a view with the collection name
    view = DeleteCollectionView(collection_name=collection)
    
    # Send a message with the button
    await interaction.response.send_message(
        f"Click the button below to delete the collection '{collection}'.",
        view=view
    )

@delete_collections.autocomplete('collection')
async def collection_autocomplete(
    interaction: discord.Interaction, 
    current: str
) -> list[app_commands.Choice[str]]:
    # Fetching collection names from the database
    collection_choices = get_collection_choices()
    
    # Filtering based on current input
    filtered_choices = [
        app_commands.Choice(name=choice.name, value=choice.value) 
        for choice in collection_choices if current.lower() in choice.name.lower()
    ]
    
    return filtered_choices
bot.run(TOKEN)
import discord 
from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv
from insertToDB import insert_or_update
from insertToDB import fetch_tmdb_description , fetch_anilist_description
from googletrans import Translator
from discord.ui import View
import re
import asyncio
import webserver

# Initialize the bot
intents = discord.Intents.default()
intents = discord.Intents.all()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix='-', intents=intents)
discord.AllowedMentions(roles=True)
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
user_xp_collection = db["user_xp"]
anime_collection = db["Anime"]
manga_collection = db["Manga"]

def get_user_xp(user_id):
    return user_xp_collection.find_one({"_id": user_id}) or {"xp": 0, "level": 1}

def update_user_xp(user_id, xp_to_add):
    user_data = get_user_xp(user_id)
    new_xp = user_data['xp'] + xp_to_add
    level = (new_xp // 100) + 1  # Example level calculation
    user_xp_collection.update_one(
        {"_id": user_id},
        {"$set": {"xp": new_xp, "level": level}},
        upsert=True
    )

async def increment_xp(ctx, xp_amount):
    update_user_xp(ctx.author.id, xp_amount)
    print(get_user_xp())


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
    await increment_xp(ctx , 5)

    films = list(films_collection.find())
    if len(films) == 0:
        await ctx.send("No films found.")
    else:
        film_list = "\n".join([film['name'] for film in films])
        await ctx.send(f"Films:\n{film_list}")

@bot.command(name="tvList")
async def tvList(ctx):
    try:
        await increment_xp(ctx , 5)
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
                description=f"**English:** {movie_info.get('description_en', 'No description available')}\n\n"
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
                description=f"**English:** {tv_show.get('description_en', 'No description available')}\n\n"
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
            description=f"**English:** {series.get('description_en', 'No description available')}\n\n"
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


from discord import ButtonStyle, ui

class InfoButton(ui.Button):
    def __init__(self, embed):
        super().__init__(label="التفاصيل", style=ButtonStyle.primary)
        self.embed = embed

    async def callback(self, interaction: discord.Interaction):
        # Send the embed as an ephemeral message
        await interaction.response.send_message(embed=self.embed, ephemeral=True)

class CustomView(ui.View):
    def __init__(self, embed):
        super().__init__(timeout=86400)  # 24 hours
        self.add_item(InfoButton(embed))

    async def on_timeout(self):
        # Optionally do something when the view times out
        for item in self.children:
            item.disabled = True  # Disable all buttons after timeout
        await self.message.edit(view=self)

@bot.tree.command(name="add")
@app_commands.describe(
    content_type="Type of content: 'movie', 'tv_series', or 'anime'.",
    name="Name of the movie, series, or anime.",
    description_en="English description of the content.",
    description_ar="Arabic description of the content (it will translate the en version).",
    link="Link to the content.",
    poster="Link to the poster image.",
    thumbnail="Link to the thumbnail image.",
)
@app_commands.choices(
    content_type=[
        discord.app_commands.Choice(name="movie", value="movie"),
        discord.app_commands.Choice(name="tv_series", value="tv_series"),
        discord.app_commands.Choice(name="anime", value="anime"),
        discord.app_commands.Choice(name="manga", value="manga"),
    ],
    description_en=[
        discord.app_commands.Choice(name="useApi", value="api")
    ],
    description_ar=[
        app_commands.Choice(name="useApi", value="api")
    ],
)
@app_commands.checks.has_role('FilmyEditor')
async def add_content(interaction: discord.Interaction, content_type: str, name: str, description_en: str, description_ar: str, link: str, poster: str, thumbnail: str):
    try:
        print(f"Received command: {content_type}, {name}, {description_en}, {description_ar}, {link}, {poster}, {thumbnail}")

        if content_type not in ['movie', 'tv_series', 'anime' , 'manga']:
            await interaction.response.send_message("Invalid type. Please specify 'movie', 'tv_series', or 'anime' or 'manga'.")
            return

        if content_type == 'movie':
            collection = films_collection
        elif content_type == 'tv_series':
            collection = tv_series_collection
        elif content_type == "manga":
            collection = manga_collection
        else:
            collection = anime_collection
        if content_type == "manga" and description_en == "api" and description_ar == "api":
            description_en = fetch_anilist_description(name , is_anime=False)
            description_ar = translate_description(description_en)
        if description_en == 'api' and not content_type == "manga":
            description_en = fetch_tmdb_description(name, content_type == 'movie')
        if description_ar == "api" and not content_type == "manga":
            description_ar = translate_description(description_en) if description_en else "Translation failed"
            print(f"Translated description (AR): {description_ar}")

        data = {
            "name": name,
            "description_en": description_en,
            "description_ar": description_ar,
            "link": link,
            "poster": poster,
            "thumbnail": thumbnail
        }

        print("Before database insertion")

            # Mention roles based on content type
        role_mentions = {
            'anime': '<@&1278039731938000906>',
            'movie': '<@&1278039853224820768>',
            'tv_series': '<@&1278039906483961887>' ,
            'manga' : "<@&1279446022145445999>"
        }

        role_mention = role_mentions.get(content_type, '')
        is_new_insert = insert_or_update(collection, [data], useApi=(description_en == 'api'))

        if is_new_insert:
            response_message = f"Inserted new {content_type}: {name} with custom description."
        else:
            response_message = f"Updated {content_type}: {name} with API description."
        
        await interaction.response.send_message(response_message)
        
        if is_new_insert:
            # Prepare the embed
            embed = discord.Embed(
                title=name,
                description=f"**English:** {description_en or 'No description available'}\n\n"
                            f"**الْعَرَبِيَّةِ:** {description_ar or 'لا توجد تفاصيل متوفرة'}",
                color=discord.Color.purple()
            )
            embed.add_field(name='Link', value=link or 'No link available')
            if thumbnail:
                embed.set_thumbnail(url=thumbnail)
            else:
                embed.add_field(name='Thumbnail', value='No thumbnail image found.')
            if poster:
                embed.set_image(url=poster)
            else:
                embed.add_field(name='Poster', value='No poster image found.')

            # Send a message to another channel with the user information
            target_channel_id = 1278027649167523944  # Replace with your channel ID
            target_channel = interaction.guild.get_channel(target_channel_id)
            if target_channel:
                user_embed = discord.Embed(
                    title=f"New {content_type.capitalize()} Added",
                    description=f"من قبل اليوزر المبدع:  **{interaction.user.name}**   😍",
                    color=discord.Color.blue()
                )
                user_embed.set_author(
                    name=f"{interaction.user.name}#{interaction.user.discriminator}",
                    icon_url=interaction.user.avatar.url
                )
                user_embed.add_field(name=f"{content_type.capitalize()} Name:", value=f"{name}")
                view = ui.View()
                view.add_item(InfoButton(embed=embed))
                
                try:
                    message = role_mention
                    await target_channel.send(embed=user_embed ,content=message ,view=view , allowed_mentions=discord.AllowedMentions(roles=True))


                except discord.Forbidden:
                    print("Bot does not have permission to send messages in the target channel.")

            
        print("Response sent successfully")

    except Exception as e:
        print(f"Error in add_content command: {e}")
        await interaction.response.send_message("An error occurred while processing the request.")




@bot.tree.command(name="custom_add")
@app_commands.describe(
    content_type="Type of content: 'movie', 'tv_series', or 'anime'.",
    name="Name of the movie, series, or anime.",
    description_en="English description of the content.",
    description_ar="Arabic description of the content.",
    link="Link to the content.",
    poster="Link to the poster image.",
    thumbnail="Link to the thumbnail image.",
)
@app_commands.choices(
    content_type=[
        discord.app_commands.Choice(name="movie", value="movie"),
        discord.app_commands.Choice(name="tv_series", value="tv_series"),
        discord.app_commands.Choice(name="anime", value="anime")
    ]
)
@app_commands.checks.has_role('FilmyEditor')
async def custom_add(interaction: discord.Interaction, content_type: str, name: str, description_en: str, description_ar: str, link: str, poster: str, thumbnail: str):
    try:
        print(f"Received command: {content_type}, {name}, {description_en}, {description_ar}, {link}, {poster}, {thumbnail}")

        if content_type not in ['movie', 'tv_series', 'anime']:
            await interaction.response.send_message("Invalid type. Please specify 'movie', 'tv_series', or 'anime'.")
            return

        if content_type == 'movie':
            collection = films_collection
        elif content_type == 'tv_series':
            collection = tv_series_collection
        else:
            collection = anime_collection

        data = {
            "name": name,
            "description_en": description_en,
            "description_ar": description_ar,
            "link": link,
            "poster": poster,
            "thumbnail": thumbnail
        }

        print("Before database insertion")
        insert_or_update(collection, [data], useApi=False)

        print("After database insertion")
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
@app_commands.checks.has_role("FilmyEditor")
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

def get_anime_choices():
    anime_list = db['Anime'].find({}, {"name": 1, "_id": 0})
    choices = [discord.app_commands.Choice(name=anime['name'], value=anime['name']) for anime in anime_list]
    return choices

@bot.tree.command(name="anime_list")
@app_commands.describe(
    anime="Choose an anime series to get more information."
)
async def anime_list(interaction: discord.Interaction, anime: str):
    try:
        anime_info = db['Anime'].find_one({"name": anime})
        
        if anime_info:
            embed = discord.Embed(
                title=anime_info['name'],
                description=f"**English:** {anime_info.get('description_en', 'No description available')}\n\n"
                            f"**الْعَرَبِيَّةِ:** {anime_info.get('description_ar', 'لا توجد تفاصيل متوفرة')}",
                color=discord.Color.purple()  # You can change the color if desired
            )
            embed.add_field(name='Link', value=anime_info.get('link', 'No link available'))
            
            if 'thumbnail' in anime_info and anime_info['thumbnail']:
                embed.set_thumbnail(url=anime_info['thumbnail'])
            else:
                embed.add_field(name='Thumbnail', value='No thumbnail image found.')
            
            if 'poster' in anime_info and anime_info['poster']:
                embed.set_image(url=anime_info['poster'])
            else:
                embed.add_field(name='Poster', value='No poster image found.')
            
            await interaction.response.send_message(embed=embed)
                        # Send an empty embedded message to another channel
        else:
            await interaction.response.send_message("Anime series not found.")
    
    except Exception as e:
        print(f"Error in anime_list command: {e}")
        await interaction.response.send_message("An error occurred while processing the request.")

@anime_list.autocomplete('anime')
async def anime_autocomplete(
    interaction: discord.Interaction, 
    current: str
) -> list[app_commands.Choice[str]]:
    anime_choices = get_anime_choices()
    
    filtered_choices = [
        app_commands.Choice(name=choice.name, value=choice.value) 
        for choice in anime_choices if current.lower() in choice.name.lower()
    ]
    
    return filtered_choices
def get_manga_choices():
    manga_list = db['Manga'].find({}, {"name": 1, "_id": 0})
    choices = [discord.app_commands.Choice(name=manga['name'], value=manga['name']) for manga in manga_list]
    return choices

@bot.tree.command(name="manga_list")
@app_commands.describe(
    manga="Choose a manga series to get more information."
)
async def manga_list(interaction: discord.Interaction, manga: str):
    try:
        manga_info = db['Manga'].find_one({"name": manga})
        
        if manga_info:
            embed = discord.Embed(
                title=manga_info['name'],
                description=f"**English:** {manga_info.get('description_en', 'No description available')}\n\n"
                            f"**الْعَرَبِيَّةِ:** {manga_info.get('description_ar', 'لا توجد تفاصيل متوفرة')}",
                color=discord.Color.purple()  # You can change the color if desired
            )
            embed.add_field(name='Link', value=manga_info.get('link', 'No link available'))
            
            if 'thumbnail' in manga_info and manga_info['thumbnail']:
                embed.set_thumbnail(url=manga_info['thumbnail'])
            else:
                embed.add_field(name='Thumbnail', value='No thumbnail image found.')
            
            if 'poster' in manga_info and manga_info['poster']:
                embed.set_image(url=manga_info['poster'])
            else:
                embed.add_field(name='Poster', value='No poster image found.')
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Manga series not found.")
    
    except Exception as e:
        print(f"Error in manga_list command: {e}")
        await interaction.response.send_message("An error occurred while processing the request.")

@manga_list.autocomplete('manga')
async def manga_autocomplete(
    interaction: discord.Interaction, 
    current: str
) -> list[app_commands.Choice[str]]:
    manga_choices = get_manga_choices()
    
    filtered_choices = [
        app_commands.Choice(name=choice.name, value=choice.value) 
        for choice in manga_choices if current.lower() in choice.name.lower()
    ]
    
    return filtered_choices


@bot.event
async def on_message(message):
    smart_search_channel_id = 1278073827280031775
    if message.channel.id == smart_search_channel_id and not message.author.bot:
        try:
            user_input = message.content.strip()
            print(f"User input: {user_input}")
            
            # Perform a regex search for the input in the anime, movies, and TV shows collections
            anime_info = db['Anime'].find_one({"name": {"$regex": re.compile(user_input, re.IGNORECASE)}})
            movie_info = db['films'].find_one({"name": {"$regex": re.compile(user_input, re.IGNORECASE)}})
            tv_info = db['tv_series'].find_one({"name": {"$regex": re.compile(user_input, re.IGNORECASE)}})
            manga_info = manga_collection.find_one({"name": {"$regex": re.compile(user_input, re.IGNORECASE)}})

            content_found = False

            if anime_info:
                content_found = True
                await send_content_info(message, anime_info, content_type="Anime")
            if movie_info:
                content_found = True
                await send_content_info(message, movie_info, content_type="Movie")
            if tv_info:
                content_found = True
                await send_content_info(message, tv_info, content_type="TV Show")
            if manga_info:
                content_found = True
                await send_content_info(message, manga_info, content_type="Manga")


            if not content_found:
                no_match_msg = await message.channel.send("No matching content found.")
                await asyncio.sleep(2)  # Delete the message after 5 seconds
                await no_match_msg.delete()
        except Exception as e:
            print(f"Error in on_message event: {e}")
            await message.channel.send("An error occurred while processing your request.")

async def send_content_info(message, content_info, content_type):
    embed = discord.Embed(
        title=f"{content_info['name']} ({content_type})",
        description=f"**English:** {content_info.get('description_en', 'No description available')}\n\n"
                    f"**الْعَرَبِيَّةِ:** {content_info.get('description_ar', 'لا توجد تفاصيل متوفرة')}",
        color=discord.Color.purple()
    )
    embed.add_field(name='Link', value=content_info.get('link', 'No link available'))
    
    if 'thumbnail' in content_info and content_info['thumbnail']:
        embed.set_thumbnail(url=content_info['thumbnail'])
    if 'poster' in content_info and content_info['poster']:
        embed.set_image(url=content_info['poster'])
    
    await message.channel.send(embed=embed)




webserver.keep_alive()
bot.run(TOKEN)
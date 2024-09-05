from pymongo import MongoClient
import requests
# MongoDB connection
client = MongoClient('mongodb+srv://astro251sq:king-dcv12yx@mydb.faqppaq.mongodb.net/?retryWrites=true&w=majority&appName=MyDB')
db = client['FilmyDB']  # Replace with your DB name
films_collection = db['films']
tv_series_collection = db['tv_series']


TMDB_API_KEY = 'bba5941b8c91e395e688d89dc32dbd56'

def fetch_tmdb_description(name, is_film=True):
    base_url = 'https://api.themoviedb.org/3'
    search_url = f"{base_url}/search/{'movie' if is_film else 'tv'}?api_key={TMDB_API_KEY}&query={name}"
    
    response = requests.get(search_url)
    data = response.json()
    
    if data['results']:
        item = data['results'][0]
        description_en = item.get('overview', 'No description available')
        return description_en
    else:
        return None
    

def fetch_anilist_description(name, is_anime=True):
    search_type = 'anime' if is_anime else 'manga'
    query = """
    query ($search: String) {
      Media (search: $search, type: %s) {
        title {
          romaji
        }
        description
      }
    }
    """ % ('ANIME' if is_anime else 'MANGA')

    url = 'https://graphql.anilist.co'
    variables = {
        'search': name
    }

    response = requests.post(url, json={'query': query, 'variables': variables})
    data = response.json()

    if data.get('data') and data['data']['Media']:
        item = data['data']['Media']
        description = item.get('description', 'No description available')
        return description
    else:
        return None

# Sample films data with posters, thumbnails, and Arabic descriptions
films_data = [
    {
        "name": "Inception",
        "link": "https://example.com/inception",
        "description_en": "A mind-bending thriller directed by Christopher Nolan.",
        "description_ar": "فيلم مثير للعقل من إخراج كريستوفر نولان.",
        "poster": "https://example.com/inception-poster.jpg",
        "thumbnail": "https://example.com/inception-thumbnail.jpg"
    },
    {
        "name": "The Matrix",
        "link": "https://example.com/the-matrix",
        "description_en": "A hacker discovers a shocking truth about reality.",
        "description_ar": "هاكر يكتشف حقيقة صادمة عن الواقع.",
        "poster": "https://example.com/the-matrix-poster.jpg",
        "thumbnail": "https://example.com/the-matrix-thumbnail.jpg"
    },
    {
        "name": "Interstellar",
        "link": "https://example.com/interstellar",
        "description_en": "Explorers travel through a wormhole in search of a new home for humanity.",
        "description_ar": "مستكشفون يسافرون عبر ثقب دودي بحثاً عن موطن جديد للبشرية.",
        "poster": "https://example.com/interstellar-poster.jpg",
        "thumbnail": "https://example.com/interstellar-thumbnail.jpg"
    }
]

# Sample TV series data with posters, thumbnails, and Arabic descriptions
tv_series_data = [
    {
        "name": "Breaking Bad",
        "link": "https://example.com/breaking-bad",
        "description_en": "A high school chemistry teacher turned methamphetamine manufacturer.",
        "description_ar": "مدرس كيمياء في المدرسة الثانوية يتحول إلى مصنع للميثامفيتامين.",
        "poster": "https://example.com/breaking-bad-poster.jpg",
        "thumbnail": "https://example.com/breaking-bad-thumbnail.jpg"
    },
    {
        "name": "Game of Thrones",
        "link": "https://example.com/game-of-thrones",
        "description_en": "Noble families vie for control of the Iron Throne in a mythical land.",
        "description_ar": "العائلات النبيلة تتنافس على السيطرة على العرش الحديدي في أرض خيالية.",
        "poster": "https://example.com/game-of-thrones-poster.jpg",
        "thumbnail": "https://example.com/game-of-thrones-thumbnail.jpg"
    },
    {
        "name": "The Witcher",
        "link": "https://example.com/the-witcher",
        "description_en": "A monster hunter battles dark forces in a medieval fantasy world.",
        "description_ar": "صائد الوحوش يقاتل قوى مظلمة في عالم خيالي من العصور الوسطى.",
        "poster": "https://cdn.discordapp.com/attachments/1273410260605861995/1276358591821123614/The_Witcher.jpeg?ex=66c93d11&is=66c7eb91&hm=9b460d487b66dce83db239002bd99ed39b6b8830ef59fbb9e923f0c9315f61a9&",
        "thumbnail": "https://cdn.discordapp.com/attachments/1273410260605861995/1276358591821123614/The_Witcher.jpeg?ex=66c93d11&is=66c7eb91&hm=9b460d487b66dce83db239002bd99ed39b6b8830ef59fbb9e923f0c9315f61a9&"
    }
]


# Function to insert or update data with duplicate checking
def insert_or_update(collection, data_list , useApi = False):
    for data in data_list:
        existing_record = collection.find_one({'name': data['name']})
        if existing_record:
            # Check if any fields have changed
            if (existing_record.get('link') != data.get('link') or
                existing_record.get('description_en') != data.get('description_en') or
                existing_record.get('description_ar') != data.get('description_ar') or
                existing_record.get('poster') != data.get('poster') or
                existing_record.get('thumbnail') != data.get('thumbnail')):
                # Update existing record with new data
                collection.replace_one({'name': data['name']}, data)
                print(f"Updated: {data['name']}")
                return False
            else:
                print(f"No changes for: {data['name']}")
                return False
        else:
            # Insert new record
            if useApi == True:
                descreption_en = fetch_tmdb_description(data['name'] , )
                if descreption_en :
                    data['description_en'] = descreption_en
            collection.insert_one(data)
            print(f"Inserted: {data['name']}")
            return True

if __name__ == "__main__":
# Insert or update data into the films collection
    insert_or_update(films_collection, films_data)

# Insert or update data into the tv_series collection
    insert_or_update(tv_series_collection, tv_series_data)

from flask import Flask, render_template, request
import requests
from env import tmdb_api_key

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        show_name = request.form.get("show_name")
        if show_name:
            episode_list = get_chart_data(show_name)
            name_list = [episode.name for episode in episode_list]
            rating_list = [episode.rating for episode in episode_list]
            episode_number_list = [episode.episode_number for episode in episode_list]
            return render_template("index.html", name_list=name_list, rating_list=rating_list, episode_number_list=episode_number_list)
    return render_template("index.html")

# getting data from the api
apikey = tmdb_api_key
headers = {
    "Authorization": f"Bearer {apikey}",
}

class Episode:
    def __init__(self, name, episode_number, rating):
        self.name = name
        self.episode_number = episode_number # format: "1x1"
        self.rating = rating

def get_chart_data(show_name):
    show_id = get_show_id(show_name)
    no_seasons = get_no_seasons(show_id)
    episode_list = []
    for season in no_seasons:
        if season != 0:
            episodes = get_episodes(show_id, season)
            for episode in episodes:
                episode_name = episode["name"]
                episode_number = episode["episode_number"]
                rating = episode["vote_average"]
                episode = Episode(episode_name, f"{season}x{episode_number}", rating) # format: "1x1"
                episode_list.append(episode)
    return episode_list

def get_show_id(name):
    params = {
        "query": name
    }
    url = f"https://api.themoviedb.org/3/search/tv"
    rawdata = requests.get(url, headers=headers, params=params)
    newdata = rawdata.json()
    return newdata["results"][0]["id"]

def get_no_seasons(id):
    url = f"https://api.themoviedb.org/3/tv/{id}"
    rawdata = requests.get(url, headers=headers)
    newdata = rawdata.json()
    seasonlist = []
    for season in newdata["seasons"]:
        seasonlist.append(season["season_number"])
    return seasonlist

def get_episodes(id, season_number):
    url = f"https://api.themoviedb.org/3/tv/{id}/season/{season_number}"
    rawdata = requests.get(url, headers=headers)
    newdata = rawdata.json()
    episode_list = []
    for episode in newdata["episodes"]:
        episode_list.append({
            "name": episode["name"],
            "episode_number": episode["episode_number"],
            "vote_average": episode["vote_average"]
        })
    return episode_list #only gives list of episode numbers, not the episode name

if __name__ == "__main__":
    app.run(debug=True)
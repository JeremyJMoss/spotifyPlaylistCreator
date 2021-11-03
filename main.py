from tkinter import *
from tkinter import messagebox
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()


# button function
def submit():
    try:
        int(entry.get())
    except ValueError:
        messagebox.showwarning(title="Enter a year", message="Please enter a valid year in format 'YYYY'")
        entry.delete(0, END)
    else:
        text = entry.get()
        entry.delete(0, END)
        label.focus()
        today = datetime.now().strftime(f"{text}-%m-%d")
        url = f"https://www.billboard.com/charts/hot-100/{today}"
        response = requests.get(url)
        billboard_website = response.text
        soup = BeautifulSoup(billboard_website, "html.parser")
        songs = soup.find_all(name="span", class_="chart-element__information__song")
        all_songs = [song.getText() for song in songs]
        auth_manager = SpotifyOAuth(client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                                    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                                    redirect_uri=os.getenv("SPOTIPY_REDIRECT-URI"),
                                    scope="playlist-modify-private",
                                    show_dialog=True,
                                    cache_path=".cache")
        sp = spotipy.Spotify(auth_manager=auth_manager)
        sp_user_id = sp.current_user()["id"]
        song_uris = []
        for song in all_songs:
            result = sp.search(q=f"track:{song} year:{text}", type="track")
            try:
                uri = result["tracks"]["items"][0]["uri"]
                song_uris.append(uri)
            except IndexError:
                print(f"{song} doesn't exist in spotify. Skipped.")
        playlist = sp.user_playlist_create(user=sp_user_id, name=f"{text} Billboard Top 100", public=False)
        sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)


window = Tk()
window.config(padx=40, pady=40)
window.title("Top 100 Billboard Hits")
label = Label(text="What year would you like to create a playlist for?", font=("Arial", 11, "bold"))
label.pack(pady=10)
entry = Entry(width=20, justify="center", font=("Arial", 15, "normal"))
entry.focus()
entry.pack(pady=10)
button = Button(width=10, text="Submit", command=submit)
button.pack(pady=10)


window.mainloop()

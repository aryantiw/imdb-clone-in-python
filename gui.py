import pprint
from urllib.request import Request, urlopen                                        # importing modules
from bs4 import BeautifulSoup
import re
from tkinter import *
import textwrap


root = Tk()
root.title('VITMDB')
root.geometry("1920x1080")


def find(search):
    if search == "":
        search = "hero"

    url = "https://www.imdb.com/find?q="                                           # creating url for request
    for words in search.split():
        url += words + "+"
    url = url[0:-1] + '&ref_=nv_sr_sm'

    site0 = urlopen(url)                                                           # getting initial search html
    soup = BeautifulSoup(site0, 'html.parser')                                     # parsing html
    names = soup.find_all("td", "a", class_="result_text")                         # searching for results

    results = {}
    for name in names:                                                             # creating dict with name and link
        link = re.findall('href="\s*([^"]*)\s*"', str(name))[0]
        search = name.text
        if link.startswith('/name/'):
            results[search.strip()] = ['https://www.imdb.com' + link, "name"]
        elif link.startswith('/title/'):
            results[search.strip()] = ['https://www.imdb.com' + link, "title"]
    return results


def select_name(url):
    html = urlopen(url)
    final_soup = BeautifulSoup(html, 'html.parser')
    movies = final_soup.find_all("b")
    results = {}
    bio_element = final_soup.find("span", class_="see-more inline nobr-only")
    bio_link = "https://www.imdb.com" + re.findall('href="\s*([^"]*)\s*"', str(bio_element))[0]
    bio_html = urlopen(bio_link)
    bio_soup = BeautifulSoup(bio_html, 'html.parser')
    bio = bio_soup.find("div", class_="soda odd").text
    for movie in movies:
        results[movie.text] = "https://www.imdb.com" + re.findall('href="\s*([^"]*)\s*"', str(movie))[0]
    return bio, results


def select_movie(url, movie_name):
    global audience_score, tomato_meter
    imdb_html = urlopen(url)
    imdb_soup = BeautifulSoup(imdb_html, 'html.parser')
    try:
        score = imdb_soup.find_all('span', class_="AggregateRatingButton__RatingScore-sc-1ll29m0-1 iTLWoV")[0].text
    except:
        score = "-"
    try:
        popularity = imdb_soup.find_all('div', class_="TrendingButton__TrendingScore-bb3vt8-1 gfstID")
        popularity = popularity[0].text
    except:
        popularity = "-"
    try:
        top_review = imdb_soup.find_all("div", class_="ipc-html-content ipc-html-content--base")[1].text
    except:
        try:
            top_review = imdb_soup.find_all("div", class_="ipc-html-content ipc-html-content--base")[0].text.strip()
        except:
            top_review = ""

    plot = imdb_soup.find_all('span', class_="GenresAndPlot__TextContainerBreakpointXL-cum89p-2 gCtawA")[0].text.strip()
    director_html = imdb_soup.find_all('a', class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")
    director_name = director_html[0].text
    director_link = "https://www.imdb.com" + re.findall('href="\s*([^"]*)\s*"', str(director_html))[0]
    tomato_search_link = "https://www.rottentomatoes.com/search?search="
    metacritic_search_link = "https://www.metacritic.com/search/movie/"
    met = True
    for words in movie_name.split():
        for element in words:
            if element == "(":
                met = False
        tomato_search_link += words + "%20"
        if met:
            metacritic_search_link += words + "%20"
    tomato_search_link = tomato_search_link[0:-3]
    metacritic_search_link = metacritic_search_link[0:-3] + "/results"

    tomato_html = urlopen(tomato_search_link)
    tomato_soup = BeautifulSoup(tomato_html, 'html.parser')
    tomato_titles = tomato_soup.find_all("a", class_="unset", slot="title")
    tomato_links = []
    for title in tomato_titles:
        tomato_title_link = re.findall('href="\s*([^"]*)\s*"', str(title))[0]
        if tomato_title_link.startswith("https"):
            tomato_links.append(tomato_title_link)
    for link in tomato_links:
        tomato_link_html = urlopen(link)
        tomato_link_soup = BeautifulSoup(tomato_link_html, 'html.parser')
        try:
            tomato_director = tomato_link_soup.find("a", attrs={'data-qa': "movie-info-director"}).text
        except:
            tomato_director = "-"

        if tomato_director == director_name:
            score_board = tomato_link_soup.find("score-board")
            try:
                audience_score = score_board["audiencescore"]
            except:
                audience_score = "-"
            try:
                tomato_meter = score_board["tomatometerscore"]
            except:
                tomato_meter = "-"
            break
        else:
            audience_score = "-"
            tomato_meter = "-"
    req = Request(metacritic_search_link, headers={'User-Agent': 'Mozilla/5.0'})
    meta_html = urlopen(req)
    meta_soup = BeautifulSoup(meta_html, "html.parser")
    try:
        meta_score = meta_soup.find("span", class_="metascore_w medium movie positive").text
    except:
        meta_score = "-"

    return score, popularity, director_name, audience_score, tomato_meter, meta_score, plot, top_review, director_link


search_bar = Entry(root, width=50, borderwidth=5,)
search_bar.insert(0, "search a movie or celebrity")


def select_click(type_title, click_url, name):
    print(type_title, click_url, name)
    for widgets in root.winfo_children():
        widgets.destroy()
    if type_title == "name":
        final_result = select_name(click_url)
        print(final_result)
        scr = final_result[1]
        keys = list(scr.keys())
        len_keys = len(keys)
        bio_list = textwrap.wrap(final_result[0], width=125)
        bio = ""
        for items in bio_list:
            bio += items + "\n"
        bio_label = Label(root, text=bio)
        bio_label.grid(row=0, column=0, pady=20)
        small_labels = Label(text="")
        small_labels.grid(row=1, column=0, pady= 0)
        if len_keys >= 1:
            search_result_button1 = Button(text=keys[0], command=lambda: select_click("title", scr[keys[0]], keys[0]))
            search_result_button1.grid(row=2, column=0, padx=650, pady=8)
        if len_keys >= 2:
            search_result_button1 = Button(text=keys[1], command=lambda: select_click("title", scr[keys[1]], keys[1]))
            search_result_button1.grid(row=3, column=0, padx=625, pady=8)
        if len_keys >= 3:
            search_result_button1 = Button(text=keys[2], command=lambda: select_click("title", scr[keys[2]], keys[2]))
            search_result_button1.grid(row=4, column=0, padx=625, pady=8)
        if len_keys >= 4:
            search_result_button1 = Button(text=keys[3], command=lambda: select_click("title", scr[keys[3]], keys[3]))
            search_result_button1.grid(row=5, column=0, padx=625, pady=8)
        if len_keys >= 5:
            search_result_button1 = Button(text=keys[4], command=lambda: select_click("title", scr[keys[4]], keys[4]))
            search_result_button1.grid(row=6, column=0, padx=625, pady=8)
        if len_keys >= 6:
            search_result_button1 = Button(text=keys[5], command=lambda: select_click("title", scr[keys[5]], keys[5]))
            search_result_button1.grid(row=7, column=0, padx=625, pady=8)
        if len_keys >= 7:
            search_result_button1 = Button(text=keys[6], command=lambda: select_click("title", scr[keys[6]], keys[6]))
            search_result_button1.grid(row=8, column=0, padx=625, pady=8)
        if len_keys >= 8:
            search_result_button1 = Button(text=keys[7], command=lambda: select_click("title", scr[keys[7]], keys[7]))
            search_result_button1.grid(row=9, column=0, padx=625, pady=8)
        if len_keys >= 9:
            search_result_button1 = Button(text=keys[8], command=lambda: select_click("title", scr[keys[8]], keys[8]))
            search_result_button1.grid(row=10, column=0, padx=625, pady=8)

    elif type_title == "title":
        final_result = select_movie(click_url, name)
        imdb_score_label = Label(root, text=f"IMDB score : {final_result[0]}", font=("Arial", 12))
        popularity_label = Label(root, text=f"Popularity : {final_result[1]}", font=("Arial", 12))
        director_button = Button(root, text=f"Director : {final_result[2]}", font=("Arial", 12), command= lambda: select_click("name", final_result[8],final_result[2]))
        audience_score_label = Label(root, text=f"Audience score : {final_result[3]}", font=("Arial", 12))
        tomatometer_label = Label(root, text=f"Tomatometer : {final_result[4]}", font=("Arial", 12))
        metascore_label = Label(root, text=f"MetaScore : {final_result[5]}", font=("Arial", 12))
        plot_list = textwrap.wrap(final_result[6], width=125)
        plot = ""
        for items in plot_list:
            plot += items + "\n"
        plot_label = Label(root, text=f"Plot : {plot}", font=("Arial", 12))
        top_review_list = textwrap.wrap(final_result[7], width=125)
        top_review = ""
        for item in top_review_list:
            top_review += item + "\n"
        fake_label = Label(root, text="")
        top_review_label = Label(root, text=f"Top review : {top_review}", font=("Arial", 12))
        imdb_score_label.grid(row=0, column=1, pady=10, padx=50)
        popularity_label.grid(row=0, column=2, pady=10)
        director_button.grid(row=3, column=1, pady=10, padx=50)
        audience_score_label.grid(row=2, column=1, pady=10, padx=50)
        tomatometer_label.grid(row=1, column=1, pady=10, padx=50)
        metascore_label.grid(row=1, column=2, pady=10)
        fake_label.grid(row=4, column=0)
        plot_label.grid(row=4, column=1, pady=25, padx=200, columnspan=2)
        top_review_label.grid(row=5, column=1, pady=10, padx=200, columnspan=2)
    pass


def search_click():
    scresult = find(search_bar.get())
    for widgets in root.winfo_children():
        widgets.destroy()
    pprint.pprint(scresult)
    keys = list(scresult.keys())
    print(keys)

    small_labels = Label(text="")
    small_labels.grid(row=1, column=0, pady=75)

    len_keys = len(keys)
    if len_keys >= 1:
        search_result_button1 = Button(text=keys[0], command=lambda: select_click(scresult[keys[0]][1], scresult[keys[0]][0], keys[0]))
        search_result_button1.grid(row=2, column=0, padx=650, pady=8)
    if len_keys >= 2:
        search_result_button2 = Button(text=keys[1], command=lambda: select_click(scresult[keys[1]][1], scresult[keys[1]][0], keys[1]))
        search_result_button2.grid(row=3, column=0, pady=8)
    if len_keys >= 3:
        search_result_button3 = Button(text=keys[2], command=lambda: select_click(scresult[keys[2]][1], scresult[keys[2]][0], keys[2]))
        search_result_button3.grid(row=4, column=0, pady=8)
    if len_keys >= 4:
        search_result_button4 = Button(text=keys[3], command=lambda: select_click(scresult[keys[3]][1], scresult[keys[3]][0], keys[3]))
        search_result_button4.grid(row=5, column=0, pady=8)
    if len_keys >= 5:
        search_result_button5 = Button(text=keys[4], command=lambda: select_click(scresult[keys[4]][1], scresult[keys[4]][0], keys[4]))
        search_result_button5.grid(row=6, column=0, pady=8)
    if len_keys >= 6:
        search_result_button6 = Button(text=keys[5], command=lambda: select_click(scresult[keys[5]][1], scresult[keys[5]][0], keys[5]))
        search_result_button6.grid(row=7, column=0, pady=8)
    if len_keys >= 7:
        search_result_button7 = Button(text=keys[6], command=lambda: select_click(scresult[keys[6]][1], scresult[keys[6]][0], keys[6]))
        search_result_button7.grid(row=8, column=0, pady=8)


photo = PhotoImage(file="VITMDB3.png")
button = Label(root, image=photo)
button.grid(row=1, column=1)
small_label = Label(text="")
search_button = Button(root, text="search", command=search_click)

search_bar.grid(row=7, column=1, padx=600, pady=2, columnspan=1,rowspan=1)
small_label.grid(row=0, column=0, pady=25)
search_button.grid(row=8, column=1,)


root.mainloop()

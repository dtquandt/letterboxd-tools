import streamlit as st
import lbxd

import pandas as pd
import numpy as np

import requests

@st.cache(show_spinner=False)
def load_film_data():
    return pd.read_pickle('data/film_data.p')

@st.cache(show_spinner=False)
def get_user_ratings(username):
    try:
        user_id = lbxd.get_id_from_username(username)
        ratings = lbxd.get_user_ratings(user_id)
        return ratings
    except:
        return None

@st.cache(show_spinner=False)
def fetch_watchlist(username):
        try:
            user_watchlist = lbxd.get_member_watchlist(username)
            return user_watchlist
        except:
            return None
            
@st.cache(show_spinner=False)
def discover_api_base():
    api_base = 'http://localhost:8000'
    try:
        requests.get(api_base+'/')
    except:
        api_base = 'http://backend:8000'
        requests.get(api_base+'/')
        return api_base
        

API_BASE = discover_api_base()
film_data = load_film_data()

def intro():
    st.sidebar.success("Select a tool above.")
    

def random_movie_picker():

    st.write("## Can't pick a movie?\nRandomly select one from your watchlist!")

    username = st.text_input('Letterboxd username')
    if username:
        with st.spinner('Please wait a moment while we fetch your watchlist...'):
            user_watchlist = fetch_watchlist(username)
        if user_watchlist is not None:
            if len(user_watchlist) > 0:
                user_watchlist = user_watchlist.merge(film_data[['id', 'tagline', 'description']], how='left', on='id')
                st.success('Watchlist loaded successfully.')
                if st.button('Get random movie!'):
                    sample = user_watchlist.sample(1).iloc[0]                                        
                    movie_directors = ', '.join(
                        [x['name'] for x in sample['directors']])
                    movie_release_year = sample['releaseYear']
                    movie_title = sample['name']
                    movie_poster_url = sample['poster']['sizes'][-1]['url'] if len(
                        sample['poster'].get('sizes')) >= 1 else ''
                    movie_links = [x['url'] for x in sample['links']]
                    st.markdown(f'# {movie_title}')
                    if movie_poster_url:
                        st.image(f"{movie_poster_url}", width=400)
                    st.markdown(
                        f'## {movie_release_year:.0f} | {movie_directors}')
                    st.subheader(sample['tagline'])
                    st.write(sample['description'])
                    for link in movie_links:
                        st.write(link)
            else:
                st.error(
                    'Sorry, but it looks like this user has no watchlist or it is set to private!')
        else:
            st.error(
                "User not found. Please make sure you've typed a valid Letterboxd username.")


def group_watchlist_picker():

    st.write("## Having trouble picking a film as a group?")
    st.write("Find common movies in your watchlists!")

    @st.cache(show_spinner=False)
    def fetch_watchlist(username):
        with st.spinner(f'Please wait a moment while we fetch the watchlist for {username}...'):
            try:
                user_watchlist = lbxd.get_member_watchlist(username)
                return user_watchlist
            except:
                return None

    count = st.slider('How many of you are there?', 2, 10)
    all_users = []

    for i in range(0, count):
        user = st.text_input(f'Letterboxd username for #{i+1}')
        all_users.append(user)

    if len(all_users) == len([x for x in all_users if x]):
        if st.button('All done?'):

            all_watchlists = []
            for user in all_users:
                user_watchlist = fetch_watchlist(user)
                if user_watchlist is not None and len(user_watchlist) > 0:
                    st.success(f'Successfully pulled watchlist for {user}')
                    all_watchlists.append(user_watchlist)
                else:
                    st.error(
                        f'There was a problem getting the watchlist for {user}')

            combined = pd.concat(all_watchlists)
            counts = combined.groupby('id')['name'].count().sort_values()
            combined['Count'] = combined['id'].apply(lambda x: counts[x])
            combined = combined.drop_duplicates(
                subset=['id']).sort_values(by='Count', ascending=False)
            combined['Film'] = combined['name']
            combined['Year'] = combined['releaseYear']
            combined['Directed by'] = combined['directors'].apply(
                lambda x: ', '.join([y['name'] for y in x]))
            combined['Letterboxd URL'] = combined['links'].str[0].str['url']
            results = combined[combined['Count'] >= 2].copy()

            if len(results) > 0:
                st.write(
                    'Here are the movies that show up in at least 2 watchlists for this group:')
                st.table(
                    results[['Film', 'Year', 'Directed by', 'Letterboxd URL', 'Count']])
            else:
                st.write(
                    'Looks like there are no films in common between your watchlists.')
                st.error('Should you even really be friends?')

    else:
        st.info(
            """Looks like we're still missing some folks! Make sure you fill in every box.""")


def movie_compatibility_score():

    st.title('Coming soon!')

    pass


def recommendation_system():

    

    @st.cache(show_spinner=False)
    def model_api_get(url):
        return requests.get(API_BASE+url).json()

    def model_api_post(url):
        return requests.post(API_BASE+url).json()

    st.title("So many movies, so little time!")
    st.write(
        "To make it easier, we'll use fancy math to figure out which ones we think you'll like.")

    with st.spinner('Please wait a second while we set things up - loading film and model data...'):
        model_movies = model_api_get('/model_items')['items']

    user_ratings = None
    user_watchlist = None            
    username = st.text_input('Please enter your Letterboxd username')

    if username:
        with st.spinner('Please wait while we grab your ratings and watchlist. If you have a lot, it could take a while.'):
            try:
                user_ratings = get_user_ratings(username)
                user_watchlist = fetch_watchlist(username)
                st.write(
                    f"Looks like you've rated **{len(user_ratings)} films**, giving an average rating of **{user_ratings['rating'].mean():.2f} stars**.")
            except:
                st.error(
                    "Sorry, we couldn't get the ratings for that user. Try again.")
                user_ratings = None
                user_watchlist = None

    if user_ratings is not None and len(user_ratings.dropna(subset=['rating'])) > 0:
        
        with st.beta_expander('Advanced filters'):
            row1_col1, row1_col2 = st.beta_columns(2)
            row2_col1, row2_col2 = st.beta_columns(2)
            row3_col1, row3_col2 = st.beta_columns(2)
            year_range = row1_col1.slider('Release year', 1900, 2021, value=(1900, 2021), step=1, format='%i', key='year_sli')
            runtime_range = row1_col2.slider('Runtime (minutes)', 60, 240, value=(60, 240), step=10, format='%i', key='runtime_sli')
            
            max_popularity_range = ((len(model_movies) + 99) // 100) * 100
            popularity_range = row2_col1.slider('Popularity ranking (higher = more obscure)', 0, max_popularity_range, value=(0, max_popularity_range), step=100, format='%i', key='pop_sli')
            rating_range = row2_col2.slider('Average Letterboxd rating', 0.0, 5.0, value=(0.0,5.0), step=0.5, format='%.1f', key='rat_sli')
            
            #Spacing
            row3_col1.title('')
            include_watchlist = row3_col1.checkbox('Include watchlisted films', True)            
            country_specification = row3_col2.text_input('Country filter | 2 letter ISO-3166 code (eg: US, BR, GB)\nLeave blank to include all', '', key='country_txt')
            
        valid_ratings = user_ratings.dropna(subset=['rating'])
        valid_ratings = valid_ratings[valid_ratings['film'].isin(model_movies)]
        user = user_ratings['member'].iloc[0]

        if len(valid_ratings) < 30:
            st.warning(
                "Warning: you don't have that many ratings. To improve recommendations, rate more movies! 30 or so is a good start.")
            
        st.write('')
        st.write('')

        if st.button('Generate predictions'):
            with st.spinner('Training model with your ratings and generating predictions...'):
                item_list = ','.join([x[1] for x in valid_ratings.values])
                rating_list = ','.join([str(x[2])
                                        for x in valid_ratings.values])
                pred_url = f'/get_recommendations/user={user}&item_list={item_list}&rating_list={rating_list}'
                predictions = model_api_post(pred_url)['results']

            predictions = pd.DataFrame(predictions)
            predictions = predictions.merge(
                film_data[['id', 'name', 'rating', 'poster', 'links', 'releaseYear', 'runTime', 'popularity', 'countries']], how='left', left_on='film', right_on='id')
            predictions['difference'] = predictions['prediction'] - predictions['rating']
            predictions['score'] = predictions['prediction'] + predictions['difference']
            predictions = predictions[~predictions['film'].isin(user_ratings['film'])]

            predictions = predictions.sort_values(by='score', ascending=False)
            if year_range:
                predictions = predictions[predictions['releaseYear'].between(year_range[0], year_range[1])]
            if runtime_range:
                predictions = predictions[predictions['runTime'].between(runtime_range[0], runtime_range[1])]
            if popularity_range:
                predictions = predictions[predictions['popularity'].between(popularity_range[0], popularity_range[1])]
            if country_specification:
                country_filter = predictions['countries'].apply(lambda x: country_specification in [c.get('code') for c in x] if type(x) == list else False)
                predictions = predictions[country_filter]
            if user_watchlist is not None and len(user_watchlist) > 0 and include_watchlist == False:
                predictions = predictions[~predictions['film'].isin(user_watchlist['id'])]
            if rating_range:
                predictions = predictions[predictions['rating'].between(rating_range[0], rating_range[1])]

            if len(predictions) < 9:
                st.error('Sorry, your filters did not leave enough films to make recommendations. Try easing up.')
            else:
                st.header('Here are your picks')
                st.write(
                    "Based on what you're into, we feel like you should give these movies a chance:")

                for row in range(3):
                    with st.beta_container():
                        for col_idx, col in enumerate(st.beta_columns(3)):
                            i = (row+1)*3 + col_idx
                            movie = predictions.iloc[i]
                            movie_name = movie['name']
                            while '**' in movie_name:
                                movie_name = movie_name.replace('**', r'\*\*')
                            col.write(f'**{movie_name}**')
                    with st.beta_container():
                        for col_idx, col in enumerate(st.beta_columns(3)):
                            i = (row+1)*3 + col_idx
                            movie = predictions.iloc[i]
                            movie_poster = movie['poster']['sizes'][-1]['url'] if len(
                                movie['poster'].get('sizes')) >= 1 else ''
                            letterboxd_link = movie['links'][0]['url']
                            poster_html = f"""<a href="{letterboxd_link}"> <img src="{movie_poster}" width=100%> </a>"""
                            col.markdown(poster_html, unsafe_allow_html=True)
                            col.write
                    st.write('')

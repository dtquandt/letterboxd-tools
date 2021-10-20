import streamlit as st
import streamlit_analytics
import lbxd

import pandas as pd
import numpy as np
import os

import requests

def get_filters(hide_watchlist_filter=True):
    
    with st.beta_expander('Advanced filters'):
            row1_col1, row1_col2 = st.beta_columns(2)
            row2_col1, row2_col2 = st.beta_columns(2)
            row3_col1, row3_col2 = st.beta_columns(2)
            with row1_col1:
                year_range = st.slider('Release year', 1900, 2021, value=(1900, 2021), step=1, format='%i', key='year_sli')
            with row1_col2:
                runtime_range = st.slider('Runtime (minutes)', 60, 240, value=(60, 240), step=10, format='%i', key='runtime_sli')
            
            with row2_col1:
                max_popularity_range = 5000
                popularity_range = st.slider('Popularity ranking (higher = more obscure)', 0, max_popularity_range, value=(0, max_popularity_range), step=100, format='%i', key='pop_sli')
            with row2_col2:
                rating_range = st.slider('Average Letterboxd rating', 0.0, 5.0, value=(0.0,5.0), step=0.5, format='%.1f', key='rat_sli')
            
            with row3_col1:
                #Spacing
                st.title('')
                if not hide_watchlist_filter:
                    include_watchlist = st.checkbox('Include watchlisted films', True, key='include_watchlist')
            with row3_col2:
                country_specification = st.text_input('Country filter | 2 letter ISO-3166 code (eg: US, BR, GB)\nLeave blank to include all', '', key='country_txt')
            
            possible_genres = sorted(['Comedy', 'Drama', 'Thriller', 'Crime', 'Science Fiction',
                                      'Action', 'Adventure', 'Horror', 'Mystery', 'Animation', 'Music',
                                      'Romance', 'Fantasy', 'War', 'Western', 'Family', 'History',
                                      'TV Movie', 'Documentary'])
            include_genres = st.multiselect('Genres', options=possible_genres, default=possible_genres, key='genre_picker')
    
    if hide_watchlist_filter:
        return year_range, runtime_range, popularity_range, rating_range, country_specification, include_genres
    else:
        return year_range, runtime_range, popularity_range, rating_range, include_watchlist, country_specification, include_genres
    

def filter_movie_list(movie_list, year_range, runtime_range, popularity_range, rating_range, country_specification, include_genres):
    
        if year_range:
            movie_list = movie_list[movie_list['releaseYear'].between(year_range[0], year_range[1])]
        if runtime_range:
            movie_list = movie_list[movie_list['runTime'].between(runtime_range[0], runtime_range[1])]
        if popularity_range:
            movie_list = movie_list[movie_list['popularity'].between(popularity_range[0], popularity_range[1])]
        if country_specification:
            country_filter = movie_list['countries'].apply(lambda x: country_specification in [c.get('code') for c in x] if type(x) == list else False)
            movie_list = movie_list[country_filter]
        if rating_range:
            movie_list = movie_list[movie_list['rating'].between(rating_range[0], rating_range[1])]
        if include_genres and 'genres' in movie_list.columns:
            movie_list['genre_names'] = movie_list['genres'].apply(lambda x: [y['name'] for y in x])
            valid_genres = movie_list['genre_names'].apply(lambda x: any(genre in include_genres for genre in x))
            movie_list = movie_list[valid_genres]
            
        return movie_list
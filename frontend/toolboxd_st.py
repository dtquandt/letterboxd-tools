import streamlit as st

import pandas as pd
import numpy as np

from collections import OrderedDict

st.set_page_config(page_title='Toolboxd', page_icon='🎬')

import tools

# Dictionary of
# demo_name -> (demo_function, demo_description)
TOOLS = OrderedDict(
    [
        ("Introduction", (tools.intro, None)),
        ("Random movie picker", (tools.random_movie_picker, 'https://i.imgur.com/jj7Ds9X.png')),
        ("Group watchlist picker", (tools.group_watchlist_picker, 'https://i.imgur.com/Q0JtBIk.jpg')),
        ("Recommendation system", (tools.recommendation_system, 'https://i.imgur.com/a4ja6ax.jpeg')),
        ("Film taste compatibility test", (tools.movie_compatibility_score, None)),
    ]
)

        
def run():
        
    tool_name = st.sidebar.selectbox("Choose a tool", list(TOOLS.keys()), 0)
    tool = TOOLS[tool_name][0]

    if tool_name == "Introduction":
        st.write("# Welcome to *Toolboxd*!")
        st.write("""This is a suite of tools which use the Letterboxd API to make your experience on the platform even better.
                 Use the dropdown menu on the sidebar to select which tool you'd like to try out!""")
        st.image('https://upload.wikimedia.org/wikipedia/commons/3/3a/Letterboxd_logo_%282018%29.png', use_column_width=True)               
        st.write('This is not an official Letterboxd project, but it was made possible thanks to the generous API access they provided. Thanks!')
        st.write('Made by Daniel Quandt | @dtquandt | https://danielquandt.com')

    else:
        st.markdown(f"# {tool_name}")
        logo = TOOLS[tool_name][1]
        if logo:
            st.image(logo, use_column_width=True)
        # Clear everything from the intro page.
        # We only have 4 elements in the page so this is intentional overkill.
        for i in range(10):
            st.empty()

    tool()


if __name__ == "__main__":
    run()
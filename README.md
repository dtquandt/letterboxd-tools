# letterboxd-tools
### Suite of tools for Letterboxd users (including a recommendation system)

This is the source code for the http://letterboxd.tools website! Visit that first to understand what it's about.

This repo is sectioned into a frontend, powered by Streamlit, which is served by a backend, powered by FastAPI, which loads a model trained using the matrix-factorization library. This will not work unless you have API credentials for the Letterboxd API, which should be placed in a file called credentials.txt inside the /frontend folder. One line for each component of the credentials.

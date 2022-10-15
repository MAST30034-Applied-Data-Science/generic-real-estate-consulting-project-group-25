# Generic Real Estate Consulting Project
Groups should generate their own suitable `README.md`.

Bokeh and the jupyter extension of vscode do not get along, especially the show(p) command. To fix this, there are no good ways, only workarounds.
    - putting ; after show(p) to prevent it from rendering in the notebook and looking at the generated map from a normal browser
    - running `jupyter notebook --no-browser --port=8889` in the terminal and then using it from the browser

All commands are assumed to be run from the root folder if not specified otherwise.

## Scraping
1. Please download the `useragents.txt` (provided under MIT License) in the following way:
    ```shell
    cd data
    wget https://raw.githubusercontent.com/DavidWittman/requests-random-user-agent/master/requests_random_user_agent/useragents.txt
    cd ..
    ```
2. Run the notebook `Scrape.ipynb` or directly from the command line `cd scripts/ && python scrape.py`{:.language-shell}

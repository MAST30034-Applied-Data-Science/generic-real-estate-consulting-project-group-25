# Generic Real Estate Consulting Project
All commands are assumed to be run from the root folder if not specified otherwise.

## Scraping
1. Please download the `useragents.txt` (provided under MIT License) in the following way:
    ```shell
    cd data
    wget https://raw.githubusercontent.com/DavidWittman/requests-random-user-agent/master/requests_random_user_agent/useragents.txt
    cd ..
    ```
2. Run the notebook `Scrape.ipynb` or directly from the command line `cd scripts/ && python scrape.py`{:.language-shell}
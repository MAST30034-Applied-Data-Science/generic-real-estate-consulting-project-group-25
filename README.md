# Generic Real Estate Consulting Project
Groups should generate their own suitable `README.md`.

Bokeh and the jupyter exctension of vscode do not get along, especially the show(p) command. To fix this, there are no good ways, only workarounds.
    - putting ; after show(p) to prevent it from rendering in the notebook and looking at the generated map from a normal browser
    - running `jupyter notebook --no-browser --port=8889` in the terminal and then using it from the browser
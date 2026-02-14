# Paste coordinates (x,y) in chord-normalized form for one base 6-series airfoil.
# Example: NACA 63A010 symmetric. You can paste from a textbook or the UIUC database
# into the list below, then we scale to target thickness in the API.
# If you don’t have a dataset yet, leave as empty dict; the endpoint will explain what to add.

NACA6_LIBRARY = {
    # "63A010": [
    #   [1.0, 0.0], [0.99, 0.0012], ... upper surface to LE, then lower surface back to TE
    # ]
}
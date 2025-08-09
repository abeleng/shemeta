This directory handles loading historical data, doing further processing and clustering them into kebele-crop groups.

In the data folder, there are the following files:
aez_data.json and aez.json - Contain information about the agroecological zones in Ethiopia.
crop_calander.json - Contains the crop calander timeline for various crops in ethiopia. Downloaded from FAO.
crop_yield.csv - National crop yield per year.

gee.py - Handles downloading historical weather data per kebele from google earth engine.

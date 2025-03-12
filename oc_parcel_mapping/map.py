# How to use this code:
# First get the OCPA data from my Google Drive. Then unzip it and put it in
# the data folder.
# Then import this file, and run read_data() to put the data into a DataFrame.
# Last, run do_stuff(df) with df being the DataFrame you got from read_data().
# You can you importlib.reload(map) to change the code without needing to
# read the data every time.

# pip install matplotlib geopandas PyQt6

# Example:
# $ python3
# >>> import map
# >>> df = map.read_data()
# >>> map.do_stuff(df)
# edit map.py
# >>> import importlib
# >>> importlib.reload(map)
# >>> map.do_stuff(df)


# Some issues with this:
# Doesn't really account for density. There are "Multi Family" places that are way less dense
# than single family homes.
# The data doesn't have # people living there unfortunately. Making it hard to find density.
# Maybe we can use the square footage to help approximate density. A few fields correspond such as
# "LIVING_AREA" or "DEEDED_SQFT"
# Maybe we can also find the legal density of a place somehow based on zoning? 

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors
from matplotlib.colors import ListedColormap

GEOJSON_PATH = "data/OCPA_Data/OCPA_LAYERS.gdb"

# Based on "Building Type Codes" found here: https://ocpaweb.ocpafl.org/codetables
# All property use codes that start with 0 are residential. The second number corresponds with the building type.
building_codes = ["Vacant", "Single Fam Residence", "Manufactured Home","Multi Fam Residence","Condominium","Cooperative","Assisted Living","Hotel Or Motel","Condominium","Other",]
general_types = ["Grey: Other", "Blue: Probably Single Family", "Red: Probably Multi Family"]

# maps the building type codes with the General types of Single Family, Multi Family, and Other
general_map = {0: 0, 1:1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2}

def read_data():
    data = gpd.read_file(GEOJSON_PATH, layer="PARCELS")

    return data

def do_stuff(df):

    # Uncomment for only city of orlando.
    # not_orl = df['CITY_CODE'] != "ORL"
    # df = df[~not_orl]

    plot_use(df)
    # plot_lvpa(df)


def plot_use(df):
    df['RES_BUILDING_TYPE'] = df.apply(lambda row: use_category(row), axis=1)

    print("plotting data")

    colors = ['blue', 'grey', 'red']

    cmap = ListedColormap(colors)

    df.plot(column="RES_BUILDING_TYPE", legend=True, cmap=cmap)
    print("showing data")
    plt.show()


def plot_lvpa(df):
    df['LND_VAL_ACR'] = df.apply(lambda row: land_val_per_acre(row), axis=1)

    # Remove extremes
    lower_bound = 1000
    upper_bound = 10_000_000
    df = df[(df['LND_VAL_ACR'] > lower_bound) & (df['LND_VAL_ACR'] < upper_bound)]


    print("plotting data")
    norm = matplotlib.colors.LogNorm(vmin=df.LND_VAL_ACR.min(), vmax=df.LND_VAL_ACR.max())


    df.plot(column="LND_VAL_ACR", legend=True, norm=norm)
    print("showing data")
    plt.show()


def use_category(row):

    code = str(row['DOR_CODE'])

    # Exlude all codes that are either empty or don't start with 0.
    # 0 means it is residential.
    if code is None or code == '' or code[0:1] != '0':
        return "Grey: Other"

    # Get the second number in use code. This corresponds with Building type.
    rcode = int(code[1:2])
    rcode = general_map[rcode]

    return general_types[rcode] 


def land_val_per_acre(row):
    land_val = row['LAND_MKT']
    acreage = row['ACREAGE']

    land_val_acr =  land_val / acreage

    # if(land_val_acr > 10_000_000):
    #     land_val_acr = 0

    return land_val_acr


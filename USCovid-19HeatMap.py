import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Polygon
from bs4 import BeautifulSoup
import requests

"""
This function Web scrapes data from this link: https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/ and
returns a list of all the rows of data in question.
"""
def extract_Data():
    website = "https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/"
    request = requests.get(website)  # allow us to send requests to the website
    text = request.text  # get website elements
    soup = BeautifulSoup(text, 'lxml')  # get all the HTML code for the website for data scraping
    data_chart = soup.find_all('tr') #all the actual data is in blocks with the tags <tr> ..... <\tr> in the table chart

    data_rows = []
    for row in data_chart[3:]: #skip first 3 rows
        temp_row = []
        for data_element in row: #for each data piece in the data table row
            temp_row.append(data_element.text)
        data_rows.append(temp_row)
    return data_rows

"""
This function returns a data frame of the web scraped data.
"""
def get_Data_Frame():
    data = extract_Data()
    df_data = []
    for row in data[1:]: #skip first row
                                #We need to remove the ',' in the death counts, and turn them into integers
        df_data.append([row[0], int(row[4].replace(',',''))])
    df = pd.DataFrame(df_data, columns = ['State', 'Deaths']) #create data frame
    return df

"""
This function merges the data frame and shape file by the keys/columns "NAME" in the shape file and "State" in the data frame.
"""
def get_Merged_Data():
    map = gpd.read_file("cb_2018_us_state_500k.shx")  # Read the US map shape file
    df = get_Data_Frame()
    map_and_stats = map.merge(df, left_on="NAME", right_on="State")
    return map_and_stats

"""
This function loads the graph by plotting the title, colorbar, and all the US states, and annotation. Note each state
will be plotted with their value adjusted color using the argument cmap = "Blues". 
"""
def load_Graph():
    fig, ax = plt.subplots(1, figsize=(16, 8))
    ax.set_title("Total Covid Deaths per US State Colormap",fontdict={'fontsize': '20'})
    map_and_stats = get_Merged_Data()
    load_States(fig, ax, map_and_stats) #plot all states EXCEPT Hawaii and Alaska (they will be added later)
    load_Hawaii(fig, map_and_stats) #plot Hawaii
    load_Alaska(fig, map_and_stats) #plot Alaska
    load_Color_Bar(fig) #plot colorbar
    load_Annotation(fig) #plot annotation near the bottom of the center of the plot


"""
This function plots all the states from the merged data except for Hawaii and Alaska.
"""
def load_States(fig, ax, map_and_stats):
    map_and_stats[~map_and_stats.NAME.isin(["Alaska", "Hawaii"])].plot(column="Deaths", cmap="Blues", ax=ax,
                                                                       edgecolor="0.8")
    ax.axis('off')

"""
This function plots Hawaii in respect to the plot with a specific axis.
"""
def load_Hawaii(fig, map_and_stats):
    hiax = fig.add_axes([.28, 0.20, 0.1, 0.1]) #specific axis for plotting Hawaii on the plot
    hipolygon = Polygon([(-160, 23), (-160, 19), (-155, 19), (-155, 23)])
    map_and_stats.clip(hipolygon).plot(column="Deaths", cmap="Blues", ax=hiax, edgecolor='0.8')
    hiax.axis('off')

"""
This function plots Alaska in respect to the plot with a specific axis.
"""
def load_Alaska(fig, map_and_stats):
    akax = fig.add_axes([0.1, 0.17, 0.2, 0.19]) #specific axis for plotting Hawaii on the plot
    #We will crop the Alaska image from this shape file as its a better representation of what alaska should look like for our map
    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    akpolygon = Polygon([(-170, 50), (-170, 72), (-141, 72), (-141, 50)])
    alaska_gdf = world.clip(akpolygon) #Crop/Clip that image with the polygon from the "naturalearth_lowres" file
    alaska_deaths = int(map_and_stats[map_and_stats.NAME == "Alaska"]['Deaths'])
    #We need to add a "Deaths" column for that cliped Alaska image for our color map
    alaska_gdf = alaska_gdf.assign(deaths=[alaska_deaths, 0])
    alaska_gdf[alaska_gdf.deaths == 1457].plot(column="deaths", cmap="Blues", ax=akax, edgecolor='0.8')
    akax.axis('off')

"""
This function plots the color bar of our color map.
"""
def load_Color_Bar(fig):
    cbax = fig.add_axes([0.90, 0.05, 0.03, 0.5]) #specific axis for the color bar on the plot
    cbax.set_title("Covid Deaths\n", fontdict={'fontsize': '10'})
    bar_info = plt.cm.ScalarMappable(cmap="Blues", norm=plt.Normalize(vmin=0, vmax=105000))
    bar_info._A = []
    plt.colorbar(bar_info, cax=cbax)

"""
This function annotated our map with the source and access date of the data being presented/visualized.
Data is from: "https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/".
"""
def load_Annotation(fig):
    anax = fig.add_axes([0.5, 0.001, 0.03, 0.05]) #axis for annotation on the plot
    anax.set_title("Data: USAFACTS, accessed 3 Jul 24\nhttps://usafacts.org/visualizations/coronavirus-covid-19-spread-map/",
                   fontdict={'fontsize': '10'})
    anax.axis('off')

load_Graph() #loads the graph to the screen
plt.show()
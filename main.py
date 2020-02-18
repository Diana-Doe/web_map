import geopy
from geopy.geocoders import Nominatim
from geopy import ArcGIS
import folium
from folium.plugins import MiniMap
import math
import reverse_geocoder as rg 

def read_file(file,year,user_loc):
    """
    str, str, str -> dict
    Take file, year and user location and return dictionary where keys are coordinats of movies which
    were filmed near user location and values are sets with names of movies
    """
    user_loc1, user_loc2 = user(user_loc)
    with open(file, encoding='utf-8', errors='ignore') as f:
        # for line in f:
        #     if line.strip() == 'Anhonee (1952)						Modern Studio, Andheri, Mumbai, Maharashtra, India': #start working with file from this line
        #         break
        dic = {}
        movies = set()
        l = 0
        for line in f:
            # if line.strip() == 'www.betreuteLoecher.de (2002)				B�sum, Schleswig-Holstein, Germany': #end working with file on this line
            #     break
            if year in line.split(')')[0] and (user_loc1 in line.split('\t')[-1] or user_loc2 in line.split('\t')[-1]):
                lst = line.strip().split("\t")
                movie = lst[0].split("(")[0].replace('"','')
                if "(" in lst[-1]:
                    location = lst[-2]
                else:
                    location = lst[-1]
                location = find_loc(location)
                if location == None:
                    continue
                near_loc = nearest(location, user_loc)
                if near_loc == False:
                    continue
                movies.add(movie)
                if len(movies) == l:
                    continue
                else:
                    l = len(movies)
                if l > 10:
                    break
                if location not in dic:
                    dic[location] = set()
                dic[location].add(movie)
        return dic
                


def find_loc(loc):
    """
    str -> tuple
    Take name of location and return coordinats of this location
    """
    locator = Nominatim(user_agent="myGeocoder")
    try:
        locator = ArcGIS(timeout = 10)
        location = locator.geocode(loc)
        coord = (location.latitude, location.longitude)
    except AttributeError:
        return None
    except:
        return None
    return coord

def nearest(loc, user_loc):
    """
    tuple, tuple -> bool
    Take coordinates of movie and coordinates of user and return True if movie were filmed near user location
    """
    if (loc[0] <= user_loc[0] + 0.5) and (loc[0] >= user_loc[0] - 0.5) and (loc[1] <= user_loc[1] + 0.5) and (loc[1] >= user_loc[1] - 0.5):
        return True
    else: 
        return False

def map(loc,user_loc):
    """
    dict -> html
    Take locations and names of movies and create html file with map
    """
    m = folium.Map(tiles='OpenStreetMap', zoom_start=12, control_scale=True)
    minimap = MiniMap(position='topleft', toggle_display=True, zoom_level_offset=-5)
    minimap.add_to(m)
    m.add_child(folium.Marker(location = user_loc, popup = "You are here", icon = folium.Icon(color="blue",icon='home')))
    for i in loc:
        movie = ''
        for n in loc[i][0]:
            movie += '"' + n + '",' + '\n'
        m.add_child(folium.Marker(location=list(i), popup = movie + '\n' + loc[i][1], icon = folium.Icon(color="red")))
    # locationDrive = [33.567309999999964, -119.94222999999996]
    # locationLaLaLand = [34.2193883184503, -118.62327726954592]
    # locationBlade = [34, -118]
    # iconDrive= folium.features.CustomIcon('Drive.png', icon_size=(100,100))
    # iconLaLaLand = folium.features.CustomIcon('LaLaLand.png', icon_size=(100,100))
    # iconBlade = folium.features.CustomIcon('Blade.png', icon_size=(100,100))
    # popupDrive = "<strong>Drive</strong><br>Starring:Ryan Gosling<br>year: 2011<br>Rate:7.8"
    # popupBlade = "<strong>Blade Runner 2049</strong><br>Starring:Ryan Gosling<br>year: 2017<br>Rate:8"
    # popupLaLaLand = "<strong>La La Land</strong><br>Starring:Ryan Gosling<br>year: 2016<br>Rate:8"
    # folium.Marker(locationDrive,tooltip = "Drive", popup=popupDrive,icon = iconDrive).add_to(m)
    # folium.Marker(locationBlade,tooltip = "Blade Runner 2049", popup=popupBlade,icon = iconBlade).add_to(m)
    # folium.Marker(locationLaLaLand,tooltip = "La La Land", popup=popupLaLaLand,icon = iconLaLaLand).add_to(m)
    m.save('index.html')
 
  
def user(user_loc): 
    """
    tuple -> str,str
    Take user location and return 2 possible cities(states) of his coordanates
    """
    result = rg.search(user_loc) 
    result1 = result[0]['admin1']
    result2 = result[0]['admin2']
    return result1, result2

def distance(user_loc, movie_loc):
    """
    tuple,tuple -> int
    Find distance between two coordinates
    """
    print(user_loc, movie_loc)
    lat1, long1 = user_loc
    for i in movie_loc:
        print(i)
        lat2, long2 = i
        radius = 6367
        lat = math.radians(lat2-lat1)
        llong = math.radians(long2-long1)
        a = math.sin(lat/2) * math.sin(lat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(llong/2) * math.sin(llong/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = "Distance: "+ str(int(radius * c)) + "km"
        movies = movie_loc[i] 
        movie_loc[i] = []
        movie_loc[i].append(movies)
        movie_loc[i].append(distance)

    return movie_loc


if __name__ == "__main__":
    year = int(input("Please enter a year you would like to have a map for: "))
    coord = input("Please enter your location (format: lat, long): ").split(",")
    coord = tuple([float(i) for i in coord])
    print("Please wait...")
    loc = read_file("locations.list",str(year),tuple(coord))
    loc = distance(tuple(coord), loc)
    print("Map is generating")
    map(loc, tuple(coord))
    print("Map is ready")

import geopandas as gpd
import matplotlib.pyplot as plt

# Provided list of APAC countries
APAC_COUNTRIES = [
    "Australia", "Bangladesh", "Bhutan", "Brunei", "Myanmar", "Cambodia",
    "China", "Fiji", "India", "Indonesia", "Japan", "Kiribati",
    "Laos", "Malaysia", "Maldives", "Marshall Islands", "Micronesia", "Nepal",
    "New Zealand", "North Korea", "Palau", "Papua New Guinea", "Philippines",
    "Samoa", "Singapore", "Solomon Islands", "South Korea", "Sri Lanka", "Taiwan",
    "Thailand", "Timor-Leste", "Tonga", "Tuvalu", "Vanuatu",
    "Viet Nam", "South Vietnam", "Russia", "Vietnam", "Burma"
]

# Load the world map
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Standardize country names for matching (fixing specific known issues)
world['name'] = world['name'].replace({
    "Myanmar": "Burma",
    "Viet Nam": "Vietnam"
})

# Filter the world map for the APAC countries
apac_map = world[world['name'].isin(APAC_COUNTRIES)]

# Plotting the APAC countries on a map
fig, ax = plt.subplots(figsize=(15, 10))
world.boundary.plot(ax=ax)
apac_map.plot(ax=ax, color='orange')

# Adding title and labels
plt.title('APAC Countries')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

# Display the plot
plt.show()

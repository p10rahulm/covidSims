# README #
This directory contains the mined, cleaned data for each city that is used to create the instantiations for the Markov chain simulator. The instantiated parameters are passed as JSON objects to the simulator.

### Data Needs
The following table lists the data needs for the instantiation script to run 
| Dataset Description                                                       | Required Fields in the Data                                                                                                     | File Format |
|---------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|-------------|
| Ward boundaries of a city                                                 | ward no, ward name, geometry(Multipolygon Geometry)                                                                             | GeoJSON     |
| Demographic data for all wards with Age Distribution (bins of 5), household size distribution for the  city                          | ward no, total population in the ward, area of the ward, total number of households per ward                                    | JSON         |
| Common Areas (or) Points of Interest in the City                          | latitude, longitude of common areas like transport communities, markets, restaurants, places of worship) per ward (if possible) | JSON         |

### Sub-Directory Structure
The sub-directory structure followed for storing and processing of static data source used for instantiations is outlined as follows. 


```
|- modules/                          #modules for data processing and adaptation of algorithms in legacy/
|- legacy/                           #original code for instantiations
|- data/
   |- base/                         # Raw data for each city
      |- bangalore/                  # Data for Banglore City
         |- demographics.csv       # demographic data about each ward 
         |- households_and_age.json # age and household-size distributions
         |- common_areas.csv       # location of places where people congrugate
         |- city.geojson       # geographic boundaries of wards
         |- employment.csv    # census data on employed people
	 |- cityProfile.json       # processed demographic data dump for all wards
      |- chennai/
   |      
   |- bangalore/      # Data used for instantiating banglore city
      |- workplaces.json    # instantiation of workplaces
      |- commonArea.json  # instantiation of commonplaces
      |- households.json    # instantiation of households
      |- schools.json       # instantiation of schools
      |- individuals.json       # instantiation of individuals
      |- map.geojson   # instantiation of individuals
```

**Suggestion**: For consistency, we can have naming convention in lowercase-only with underscore separators. 

### Status of Data Collection ###
The following table gives a status of the data collection effort. The cells can be populated with the link of data sources used

| City     | GeoJSON for city wards | Demographic Data of city wards | Age and Household-size Distributions for City | Points of Interests (Common Spaces) | 
|----------|------------------------|--------------------------------|-----------------------------------------------|-------------------------------------|
| Banglore | [Link to Raw GeoJSON](https://github.com/datameet/Municipal_Spatial_Data/raw/master/Bangalore/BBMP.GeoJSON) |[Link to 2011 Census Data](https://smartcities.data.gov.in/catalog/city-profile-bengaluru?filters%5Bfield_catalog_reference%5D=2916949&format=json&offset=0&limit=9&sort%5Bcreated%5D=desc) select `Demographic Profile Bengaluru As On 01-03-2011`|                [Link to 2011 Census Data](https://smartcities.data.gov.in/catalog/city-profile-bengaluru?filters%5Bfield_catalog_reference%5D=2916949&format=json&offset=0&limit=9&sort%5Bcreated%5D=desc) select  `Household Profile Bengaluru As On 01-03-2011`|                  |
| New York  |                        |                                |                                               |                                     |             
| Mumbai   |                        |                                |                                               |                                     |             
| Bergamo  |                        |                                |                                               |                                     |             
| Wuhan    |                        |                                |                                               
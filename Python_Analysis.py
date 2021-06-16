import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import json
import folium

"""
Read the dataset
"""
Age_Group = pd.read_csv('AgeGroupDetails.csv')
ICMRTestingDetails = pd.read_csv('ICMRTestingDetails.csv')
covid19India = pd.read_csv('covid_19_india.csv')
HospitalBedsIndia = pd.read_csv('HospitalBedsIndia.csv')
India_Census_2011 = pd.read_csv('population_india_census2011.csv')
Individual_Details = pd.read_csv('IndividualDetails.csv')


""""
Bar plot of total cases based on Age Group
"""
sns.set_style('whitegrid')
sns.set_context("talk")
plt.figure(figsize=(14,8))
sns.barplot(data=Age_Group,x='AgeGroup',y='TotalCases',color=sns.color_palette('Set3')[0])
plt.title('Age Group Distribution')
plt.xlabel('Age Group')
plt.ylabel('Total Cases')
for i in range(Age_Group.shape[0]):
    count = Age_Group.iloc[i]['TotalCases']
    plt.text(i,count+1,Age_Group.iloc[i]['Percentage'],ha='center')
plt.show()


"""
Data Correction & Rectification
Creation of a State list
"""
covid19India['Date'] = pd.to_datetime(covid19India['Date'],dayfirst=True)
covid19India.at[1431,'Deaths']= 119
covid19India.at[1431,'State/UnionTerritory']='Madhya Pradesh'
covid19India['Deaths']= covid19India['Deaths'].astype(int)
states_list=['Maharashtra','Gujarat','Delhi','Rajasthan','Madhya Pradesh','Tamil Nadu','Uttar Pradesh','Telengana','Andhra Pradesh',
            'West Bengal','Karnataka','Kerala','Jammu and Kashmir','Punjab','Haryana','Delhi','Ladakh','Uttarakhand','Odisha','Puducherry',
             'Chhattisgarh','Chandigarh','Himachal Pradesh','Bihar','Manipur','Mizoram','Andaman and Nicobar Islands','Goa','Assam','Jharkhand',
             'Arunachal Pradesh','Tripura','Meghalaya','Nagaland']

"""
PLotting daily cases details for each state
"""
for i,state in enumerate(states_list):
    df0 = covid19India[covid19India['State/UnionTerritory'] == state]
    df1 = df0.groupby('Date').sum()
    df1.reset_index(inplace=True)
    plt.figure(figsize= (14,8))
    plt.xticks(rotation = 90 ,fontsize = 10)
    plt.yticks(fontsize = 10)
    plt.xlabel("Dates",fontsize = 20)
    plt.ylabel('Total cases',fontsize = 20)
    plt.title("Total Confirmed, Recovered, Death in India in {}".format(state), fontsize = 20)

    ax1 = plt.plot_date(data=df1,y= 'Confirmed',x= 'Date',label = 'Confirmed',linestyle ='-',color = 'b')
    ax2 = plt.plot_date(data=df1,y= 'Cured',x= 'Date',label = 'Recovered',linestyle ='-',color = 'g')
    ax3 = plt.plot_date(data=df1,y= 'Deaths',x= 'Date',label = 'Death',linestyle ='-',color = 'r')
    plt.legend()
plt.show()

"""
Plotting Daily case details for entire country
"""
df2=covid19India.groupby('Date').sum()
df2.reset_index(inplace=True)

plt.figure(figsize= (14,8))
plt.xticks(rotation = 90 ,fontsize = 10)
plt.yticks(fontsize = 10)
plt.xlabel("Dates",fontsize = 20)
plt.ylabel('Total cases',fontsize = 20)
plt.title("Total Confirmed, Active, Death in India" , fontsize = 20)

ax1 = plt.plot_date(data=df2,y= 'Confirmed',x= 'Date',label = 'Confirmed',linestyle ='-',color = 'b')
ax2 = plt.plot_date(data=df2,y= 'Cured',x= 'Date',label = 'Recovered',linestyle ='-',color = 'g')
ax3 = plt.plot_date(data=df2,y= 'Deaths',x= 'Date',label = 'Death',linestyle ='-',color = 'r')
plt.legend()
plt.show()

"""
Active Cases in each state
"""
state_cases=covid19India.groupby('State/UnionTerritory')['Confirmed','Deaths','Cured'].max().reset_index()
state_cases['Active'] = state_cases['Confirmed'] - state_cases['Deaths']- state_cases['Cured']
pd.to_numeric(India_Census_2011['Density'])
for i,state in enumerate(states_list):
    intensity = state_cases['Active']/India_Census_2011['Density']

state_cases['intensity'] = intensity
state_cases=state_cases.sort_values('intensity', ascending= False).fillna(0)
plt.figure(figsize=(20,8))
sns.barplot(data=state_cases,x='State/UnionTerritory',y='intensity',color=sns.color_palette('Set3')[3],label='Intensity')
plt.xticks(rotation=90)
plt.legend();
plt.show();

"""
Identification of States which are Hotspots
"""
Current_Details = Individual_Details[Individual_Details.status_change_date <= '10/04/2020']
Hospitalized_Currently = Current_Details[Current_Details.current_status == 'Hospitalized']

Future_Recovered = Individual_Details[Individual_Details.status_change_date > '10/04/2020']
Diagnosed_Currently = Future_Recovered[Future_Recovered.diagnosed_date <= '10/0/2020']

#To combine the hospitalised cases and the cases that haven't recovered
Confirmed_Cases = pd.concat([Hospitalized_Currently,Diagnosed_Currently])

Hotspots = Confirmed_Cases.groupby('detected_district')['current_status'].count().reset_index()
Hotspots = Hotspots[Hotspots['current_status'] > 10]

#geojsonData = gpd.read_file('india_districts.geojson')

#For the visualisation of hotspots in india
with open('india_districts.geojson') as file:
    geojsonData = json.load(file)

for i in geojsonData['features']:
    if (i['properties']['NAME_2'] == 'Greater Bombay'):
        i['properties']['NAME_2'] = 'Mumbai'

for i in geojsonData['features']:
    i['id'] = i['properties']['NAME_2']

data = Hotspots
map_choropleth = folium.Map(location=[20.5937, 78.9629], zoom_start=4)

folium.Choropleth(geo_data=geojsonData,
                  data=data,
                  name='CHOROPLETH',
                  key_on='feature.id',
                  columns=['detected_district','current_status'],
                  fill_color = 'YlOrRd',
                  fill_opacity=0.7,
                  line_opacity=0.5,
                  legend_name='Confirmed Cases',
                  highlight=True).add_to(map_choropleth)

folium.LayerControl().add_to(map_choropleth)

display(map_choropleth)

"""
Barplot of hotspots in India
"""
plt.figure(figsize=(14,50))
sns.barplot(x=Hotspots['current_status'],y=Hotspots['detected_district'],color=sns.color_palette('Set3')[10])
plt.xlabel('No. of Positive cases')
plt.ylabel('Districts')
plt.title('Positive Cases')
plt.show()


"""
Identification of maximal change in hotspots
"""
April_10_Details = Individual_Details[Individual_Details.status_change_date <= '10/04/2020']
Hospitalized_April_10 = April_10_Details[April_10_Details.current_status == 'Hospitalized']

Future_Recovered_April_10 = Individual_Details[Individual_Details.status_change_date > '10/04/2020']
Diagnosed_April_10 = Future_Recovered_April_10[Future_Recovered_April_10.diagnosed_date <= '10/04/2020']

Confirmed_Cases_April_10 = pd.concat([Hospitalized_April_10,Diagnosed_April_10])

April_3_Details = Individual_Details[Individual_Details.status_change_date <= '03/04/2020']
Hospitalized_April_3 = April_3_Details[April_3_Details.current_status == 'Hospitalized']

Future_Recovered_April_3 = Individual_Details[Individual_Details.status_change_date > '03/04/2020']
Diagnosed_April_3 = Future_Recovered_April_3[Future_Recovered_April_3.diagnosed_date <= '03/04/2020']

Confirmed_Cases_April_3 = pd.concat([Hospitalized_April_3,Diagnosed_April_3])

March_27_Details = Individual_Details[Individual_Details.status_change_date <= '27/03/2020']
Hospitalized_March_27 = March_27_Details[March_27_Details.current_status == 'Hospitalized']

Future_Recovered_March_27 = Individual_Details[Individual_Details.status_change_date > '27/03/2020']
Diagnosed_March_27 = Future_Recovered_March_27[Future_Recovered_March_27.diagnosed_date <= '27/03/2020']

Confirmed_Cases_March_27 = pd.concat([Hospitalized_March_27,Diagnosed_March_27])

March_20_Details = Individual_Details[Individual_Details.status_change_date <= '20/03/2020']
Hospitalized_March_20 = March_20_Details[March_20_Details.current_status == 'Hospitalized']

Future_Recovered_March_20 = Individual_Details[Individual_Details.status_change_date > '20/03/2020']
Diagnosed_March_20 = Future_Recovered_March_20[Future_Recovered_March_20.diagnosed_date <= '20/03/2020']

Confirmed_Cases_March_20 = pd.concat([Hospitalized_March_20,Diagnosed_March_20])

Hotspots_April_10 = Confirmed_Cases_April_10.groupby(['detected_state','detected_district'])['current_status'].count().reset_index()
Hotspots_April_3 = Confirmed_Cases_April_3.groupby(['detected_state','detected_district'])['current_status'].count().reset_index()
Hotspots_March_27 = Confirmed_Cases_March_27.groupby(['detected_state','detected_district'])['current_status'].count().reset_index()
Hotspots_March_20 = Confirmed_Cases_March_20.groupby(['detected_state','detected_district'])['current_status'].count().reset_index()

#Hotspots on each date
Hotspots_April_10 = Hotspots_April_10[Hotspots_April_10['current_status'] >= 10]
Hotspots_April_3 = Hotspots_April_3[Hotspots_April_3['current_status'] >= 10]
Hotspots_March_27 = Hotspots_March_20[Hotspots_March_27['current_status'] >= 10]
Hotspots_March_20 = Hotspots_March_20[Hotspots_March_20['current_status'] >= 10]

#Hotspots  in states
Hotspots_States_April_10 = Hotspots_April_10['detected_state'].value_counts().reset_index()
Hotspots_States_April_3 = Hotspots_April_3['detected_state'].value_counts().reset_index()
Hotspots_States_March_27 = Hotspots_March_27['detected_state'].value_counts().reset_index()
Hotspots_States_March_20 = Hotspots_March_20['detected_state'].value_counts().reset_index()

#To plot the no. of hotspots in each date in each state
plt.figure(figsize=(20,8))
plt.plot_date(data=Hotspots_States_March_20,x='index',y='detected_state',color=sns.color_palette('Set3')[9],label='20/03/2020')
plt.plot_date(data=Hotspots_States_March_27,x='index',y='detected_state',color=sns.color_palette('Set3')[1],label='27/03/2020')
plt.plot_date(data=Hotspots_States_April_3,x='index',y='detected_state',color=sns.color_palette('Set3')[6],label='03/04/2020')
plt.plot_date(data=Hotspots_States_April_10,x='index',y='detected_state',color=sns.color_palette('Set3')[3],label='10/04/2020')

plt.xticks(rotation=90)
plt.legend()
plt.show()
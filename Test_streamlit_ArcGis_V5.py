# Import required libraries
# Imports
from arcgis.gis import GIS
from pathlib import Path
from zipfile import ZipFile
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from arcgis.geometry import Geometry
from arcgis.features import FeatureLayer, FeatureLayerCollection
from datetime import datetime as dt
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import shape
from pyproj import CRS
import streamlit as st


# Dekorieren Sie die Funktionen mit @st.cache, um ihre Ergebnisse zu cachen
@st.cache_resource()
def Load_data():
    # GIS login details (use Streamlit secrets for production apps)
    username_v = 'raphael.vogt0'
    passwort_v = 'GSa01.12'

    # Initialize GIS
    gis = GIS(username=username_v, password=passwort_v)

    #Inhalte von ArcGis Cloud importieren mit Layer ID 
    Nutzungszonen_layer_ID = '2b505b38fe8843709b60961b6db2b220'
    Gebäude_nach_Nutzungen_ID = '819e1f498597426c9fb490a6848d3aa3'
    Freiraumversorgung_neu_ID = '1d6a690abdbf41faa644f3ddbea2bf53'

    #Layers einlesen mit Layer ID
    Nutzungszonen_item= gis.content.get(Nutzungszonen_layer_ID)
    Gebäude_nach_Nutzungen_item = gis.content.get(Gebäude_nach_Nutzungen_ID)
    Freiraumversorgung_Item = gis.content.get(Freiraumversorgung_neu_ID)

    # Spatially Enabled DataFrame object erstellen aus den Layern
    flayer = Nutzungszonen_item.layers[0]
    Nutzungszonen_sdf = pd.DataFrame.spatial.from_layer(flayer)

    flayer = Gebäude_nach_Nutzungen_item.layers[0]
    Gebäude_nach_Nutzungen_sdf = pd.DataFrame.spatial.from_layer(flayer)

    flayer = Freiraumversorgung_Item.layers[0]
    Freiraumversorgung_sdf = pd.DataFrame.spatial.from_layer(flayer)


    #Dataframes bereinigen und aufbereiten 
    #Platzhalter für NaT Baubeginn
    ersatz_date = dt(2023, 1, 1)

    Gebäude_nach_Nutzungen_sdf['Baubeginn'].fillna(0, inplace=True)
    Gebäude_nach_Nutzungen_sdf['BGF_Gewerb'].fillna(0, inplace=True)
    Gebäude_nach_Nutzungen_sdf['BGF_Wohnen'].fillna(0, inplace=True)
    Gebäude_nach_Nutzungen_sdf['BGF_Tot'] = Gebäude_nach_Nutzungen_sdf['BGF_Gewerb'] + Gebäude_nach_Nutzungen_sdf['BGF_Wohnen']
    Gebäude_nach_Nutzungen_sdf['BGF'].fillna(0, inplace=True)

    Freiraumversorgung_sdf['Baubeginn'].fillna(ersatz_date, inplace=True)
    Freiraumversorgung_sdf.loc[:, 'Variante'] = Freiraumversorgung_sdf.loc[:, 'Variante'].astype(int)
    Freiraumversorgung_sdf = Freiraumversorgung_sdf[Freiraumversorgung_sdf['Variante'] == 1]

    # Spatially Enabled DataFrame object erstellen aus den Layern
    flayer = Nutzungszonen_item.layers[0]
    Nutzungszonen_sdf = pd.DataFrame.spatial.from_layer(flayer)

    flayer = Gebäude_nach_Nutzungen_item.layers[0]
    Gebäude_nach_Nutzungen_sdf = pd.DataFrame.spatial.from_layer(flayer)

    flayer = Freiraumversorgung_Item.layers[0]
    Freiraumversorgung_sdf = pd.DataFrame.spatial.from_layer(flayer)

    #Dataframes bereinigen und aufbereiten 
    #Platzhalter für NaT Baubeginn
    ersatz_date = dt(2023, 1, 1)

    Gebäude_nach_Nutzungen_sdf['Baubeginn'].fillna(0, inplace=True)
    Gebäude_nach_Nutzungen_sdf['BGF_Gewerb'].fillna(0, inplace=True)
    Gebäude_nach_Nutzungen_sdf['BGF_Wohnen'].fillna(0, inplace=True)
    Gebäude_nach_Nutzungen_sdf['BGF_Tot'] = Gebäude_nach_Nutzungen_sdf['BGF_Gewerb'] + Gebäude_nach_Nutzungen_sdf['BGF_Wohnen']
    Gebäude_nach_Nutzungen_sdf['BGF'].fillna(0, inplace=True)

    Freiraumversorgung_sdf['Baubeginn'].fillna(ersatz_date, inplace=True)
    Freiraumversorgung_sdf.loc[:, 'Variante'] = Freiraumversorgung_sdf.loc[:, 'Variante'].astype(int)
    Freiraumversorgung_sdf = Freiraumversorgung_sdf[Freiraumversorgung_sdf['Variante'] == 1]

    # Erstelle GeoDataFrames aus den Spatially Enabled DataFrames
    Nutzungszonen_gdf = gpd.GeoDataFrame(Nutzungszonen_sdf, geometry=Nutzungszonen_sdf['SHAPE'].apply(shape))
    Gebäude_nach_Nutzungen_gdf = gpd.GeoDataFrame(Gebäude_nach_Nutzungen_sdf, geometry=Gebäude_nach_Nutzungen_sdf['SHAPE'].apply(shape))
    Freiraumversorgung_gdf = gpd.GeoDataFrame(Freiraumversorgung_sdf, geometry=Freiraumversorgung_sdf['SHAPE'].apply(shape))

    # Definiere das aktuelle und das Ziel-Koordinatensystem
    aktuelles_crs = CRS("EPSG:2056")  # CH1903+/LV95
    ziel_crs = CRS("EPSG:3857")       # Web Mercator

    # Stelle sicher, dass das aktuelle CRS gesetzt ist
    Nutzungszonen_gdf.set_crs(ziel_crs, inplace=True)
    Gebäude_nach_Nutzungen_gdf.set_crs(ziel_crs, inplace=True)
    Freiraumversorgung_gdf.set_crs(ziel_crs, inplace=True)


    # Konvertiere die GeoDataFrames zurück in Spatially Enabled DataFrames
    Nutzungszonen_sdf = pd.DataFrame.spatial.from_geodataframe(Nutzungszonen_gdf)
    Gebäude_nach_Nutzungen_sdf = pd.DataFrame.spatial.from_geodataframe(Gebäude_nach_Nutzungen_gdf)
    Freiraumversorgung_sdf = pd.DataFrame.spatial.from_geodataframe(Freiraumversorgung_gdf)


    # Display the spatial references in the Streamlit app
    #st.write('Spatial Reference for Gebäude_nach_Nutzungen:', Gebäude_nach_Nutzungen_sdf.spatial.sr)
    #st.write('Spatial Reference for Freiraumversorgung:', Freiraumversorgung_sdf.spatial.sr)
    #st.write('Spatial Reference for Nutzungszonen:', Nutzungszonen_sdf.spatial.sr)


    #Räumlicher Verschnitt mit ArcGis: 
    joined_sdf = Gebäude_nach_Nutzungen_sdf.spatial.join(Nutzungszonen_sdf)
    return Nutzungszonen_sdf, Gebäude_nach_Nutzungen_sdf, Freiraumversorgung_sdf, joined_sdf

if 'results_tot' not in st.session_state:
    st.session_state['results_tot'] = pd.DataFrame()
# Definieren Sie die Berechnung als Funktion
def calculate_freiflaeche(Wohnen_n, Wohnen_f, Wohnen_const, Rest_n, Rest_f, Rest_const, Nutzungszonen_sdf, Gebäude_nach_Nutzungen_sdf, Freiraumversorgung_sdf,joined_sdf):
    # Ihre Datenverarbeitung und Berechnungen kommen hier...
    # Zum Beispiel:
    Gebäude_nach_Nutzungen_sdf['Freiflächebedarf'] = Gebäude_nach_Nutzungen_sdf['BGF_Wohnen']/Wohnen_n*Wohnen_f*Wohnen_const + (Gebäude_nach_Nutzungen_sdf['BGF_Tot']-Gebäude_nach_Nutzungen_sdf['BGF_Wohnen'])/Rest_n*Rest_f*Rest_const
        
    ### Kopieren Sie die DataFrames, um "SettingWithCopyWarning" zu vermeiden
    Nutzungsmix_db_copy = Gebäude_nach_Nutzungen_sdf.copy()
    Freiraumversorgung_neu_df_Var0_copy = Freiraumversorgung_sdf.copy()

    # Konvertieren Sie die Spalte 'Baubeginn' in Nutzungsmix_db in den Datumsdatentyp
    Nutzungsmix_db_copy['Baubeginn'] = pd.to_datetime(Nutzungsmix_db_copy['Baubeginn'])

    # Konvertieren Sie die Spalte 'baubeginn' in Freiraumversorgung_neu_df_Var0 in den Datumsdatentyp
    Freiraumversorgung_neu_df_Var0_copy['Baubeginn'] = pd.to_datetime(Freiraumversorgung_neu_df_Var0_copy['Baubeginn'])

    # Zuerst müssen wir die eindeutigen 'Baubeginn'-Werte in Nutzungsmix_db und Freiraumversorgung_neu_df_Var0 finden
    # Convert 'DatetimeArray' to a Python list and then sort
    unique_baubeginn_a = list(Nutzungsmix_db_copy['Baubeginn'].unique())
    unique_baubeginn_a.sort()

    # Convert 'DatetimeArray' to a Python list and then sort
    unique_baubeginn_b = list(Freiraumversorgung_neu_df_Var0_copy['Baubeginn'].unique())
    unique_baubeginn_b.sort()

    # Erstellen Sie einen leeren DataFrame, um die Ergebnisse zu speichern
    results = []


    # Iterieren Sie durch die eindeutigen 'Baubeginn'-Werte in Nutzungsmix_db
    for Baubeginn in unique_baubeginn_a:
        # Filtern Sie Nutzungsmix_db_copy, um nur Zeilen mit dem aktuellen 'Baubeginn'-Datum zu erhalten
        filtered_a = Nutzungsmix_db_copy[Nutzungsmix_db_copy['Baubeginn'] <= Baubeginn]
        
        # Filtern Sie Freiraumversorgung_neu_df_Var0_copy, um nur Zeilen mit 'baubeginn'-Datum vor oder gleich dem aktuellen 'Baubeginn'-Datum in Nutzungsmix_db zu erhalten
        filtered_b = Freiraumversorgung_neu_df_Var0_copy[Freiraumversorgung_neu_df_Var0_copy['Baubeginn'] <= Baubeginn]
        
        # Summieren Sie die 'Freifläche' in Nutzungsmix_db_copy und 'Versorgung' in Freiraumversorgung_neu_df_Var0_copy für die gefilterten Daten
        freiflaeche_sum = filtered_a['Freiflächebedarf'].sum()
        versorgung_sum = filtered_b['Anrechenba'].sum()
        
        # Fügen Sie die Ergebnisse in die Ergebnisliste ein
        results.append({'Baubeginn': Baubeginn, 'Freifläche_sum': freiflaeche_sum, 'Versorgung_sum': versorgung_sum})

    # Erstellen Sie einen DataFrame aus der Ergebnisliste
    results_df = pd.DataFrame(results)
    results_df['Dif_'] =  results_df['Versorgung_sum'] - results_df['Freifläche_sum']

    # Selektiere die gewünschten Zeilen
    selected_rows = results_df.iloc[:, 0:4]

    # Ändere die Spaltennamen am Ende mit '_Var_a'
    selected_rows.columns = [col + '_' + Name_Var for col in selected_rows.columns]
    selected_rows_df = pd.DataFrame(selected_rows)
    # Füge die ausgewählten Zeilen den bestehenden Spalten in 'results' hinzu
    #results_tot = pd.concat([results_tot, selected_rows_df], ignore_index=True)
    if st.session_state.results_tot.empty:
        st.session_state.results_tot = selected_rows_df
    else:
        #st.session_state.results_tot = pd.merge(st.session_state.results_tot, selected_rows_df, how='outer', on=[selected_rows_df.columns[0]])
        st.session_state.results_tot = pd.merge(st.session_state.results_tot, selected_rows_df, left_on=st.session_state.results_tot.columns[0], right_on=selected_rows_df.columns[0])
    return st.session_state.results_tot

# Prüfen, ob die Variablen bereits im Session State gespeichert sind, sonst Initialisieren
if 'init' not in st.session_state:
    st.session_state['Wohnen_n'] = 93.0
    st.session_state['Wohnen_f'] = 9.0
    st.session_state['Wohnen_const'] = 0.9
    st.session_state['Rest_n'] = 44.5
    st.session_state['Rest_f'] = 2.0
    st.session_state['Rest_const'] = 0.8
    st.session_state['Name_Var'] = 'Var_a'
    st.session_state['init'] = True

# Streamlit UI Komponenten zur Eingabe der Parameter
st.title('Freiraumberechung')
st.write('Berechne hier die Freiraumversorgung basierend auf den variablen Parametern')

Name_Var = st.text_input('Variantenname', st.session_state['Name_Var'])
Wohnen_n = st.number_input('Wohnen normalisieren', min_value=0.0, max_value=100.0, value=st.session_state['Wohnen_n'])
Wohnen_f = st.number_input('Flächenverbrauch Personen Wohnen', min_value=0.0, max_value=100.0, value=st.session_state['Wohnen_f'])
Wohnen_const = st.number_input('Wohnen Faktor', min_value=0.0, max_value=1.0, value=st.session_state['Wohnen_const'], format="%.2f")
Rest_n = st.number_input('Rest normalisieren', min_value=0.0, max_value=100.0, value=st.session_state['Rest_n'])
Rest_f = st.number_input('Flächenverbrauch Personen Arbeiten', min_value=0.0, max_value=100.0, value=st.session_state['Rest_f'])
Rest_const = st.number_input('Arbeit Faktor', min_value=0.0, max_value=1.0, value=st.session_state['Rest_const'], format="%.2f")

# Aktualisieren des Session State bei Eingabeänderungen
st.session_state['Name_Var'] = Name_Var
st.session_state['Wohnen_n'] = Wohnen_n
st.session_state['Wohnen_f'] = Wohnen_f
st.session_state['Wohnen_const'] = Wohnen_const
st.session_state['Rest_n'] = Rest_n
st.session_state['Rest_f'] = Rest_f
st.session_state['Rest_const'] = Rest_const

a,b,c,d = Load_data()

# Knopf zur Auslösung der Berechnung
if st.button('Variante berechnen'):
    results_df = calculate_freiflaeche(Wohnen_n, Wohnen_f, Wohnen_const, Rest_n, Rest_f, Rest_const,a,b,c,d)
    # Plotten der Ergebnisse
    st.write("Plot der Ergebnisse")
    fig, ax = plt.subplots()
    x = results_df.iloc[:, 0]
    for col_idx in range(3, len(results_df.columns), 4):
        y = results_df.iloc[:, col_idx]
        # Verwenden von Name_Var für die Beschriftung der Kurve
        ax.plot(x, y, marker='o', linestyle='-', label=results_df.columns[col_idx])
    ax.set_xlabel('Baubeginn')
    ax.set_ylabel('Verfügbare Freifläche')
    ax.grid(True)

    # Setzen der Position der Ticks und der Beschriftungen
    ax.set_xticks(x)
    ax.set_xticklabels(x, rotation=45)

    # Anzeigen der Legende
    ax.legend()
    st.pyplot(fig)



#Print C:/Users/VogtR/AppData/Local/anaconda3/envs/Streamlit_2/Scripts/streamlit run c:/Projekte/Area/Test_raphi/ArcGis/Tests/VSCode/Test_streamlit_ArcGis_V3.py in Anaconda Prompt to start Streamlit

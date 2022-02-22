from ctypes import alignment
from turtle import color
from h2o_wave import Q, ui, app, main, data, pack
from firebase_admin import credentials
from firebase_admin import firestore
from geopy.distance import distance
from geopy.geocoders import Nominatim

import pandas as pd
import folium
import numpy as np
import datetime
import lightgbm as lgb
import firebase_admin
import json
import requests

latitude_list = []
longitude_list = []
severity_list = []
severity_clr = []

cred = credentials.Certificate('nodemcu-tester-firebase-adminsdk-p8xun-4c3dfad99c.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
url = 'https://firestore.googleapis.com/v1/projects/nodemcu-tester/databases/(default)/documents/H2O/'

postalData = pd.read_csv('ZipUS.csv',index_col="PostalCode")

async def displayError(q, message):
    q.page['error'] = ui.preview_card(
        name='preview_card',
        box='1 6 10 1',
        image='http://pldindustries.com/wave/istockphoto.jpg',
        title=message,
    )
    await q.page.save()

async def showMap(q: Q, lat, long):
    deletePages(q)
    m = folium.Map(location=[lat, long], tiles="Stamen Terrain", zoom_start=4)
    m.add_child(folium.LatLngPopup())

    q.page['map'] = ui.form_card(
        box='1 6 10 5',
        items=[
            ui.text('Map: Click on the desired location to get geo coordinates to predict wildfire severity.'),
            ui.frame(content=m._repr_html_(), height='400px'),
        ]
    )
    await q.page.save()


async def showResult(q, lat, long):
    sev = await getSeverity(q,lat, long, str(q.args.date_boundaries))
    if (sev is None):
        deletePages(q)
        await displayError(q,'Sorry! Weather Data Not Available for the Selected Location')

    else:
        q.page['result'] = ui.form_card(
            box='1 6 5 3',
            items=[
                ui.text_l('Selected Point...'),
                ui.text('Latitude: ' + str(lat)),
                ui.text('Longitude: ' + str(long)),
                ui.text('Date: ' + str(q.args.date_boundaries)),
                ui.text('Severity: ' + str(await getSeverity(q,lat, long, str(q.args.date_boundaries)))),
                ui.button(name='historyBtn', label='Show History',primary=True),
            ],
        )
        q.page['result1'] = ui.image_card(
            box='6 6 5 3',
            title='',
            path="https://raw.githubusercontent.com/pldrobot/ML_Course_Submissions/main/class_1.jpg",
        )
        
        severity_value = await getSeverity(q,lat, long, str(q.args.date_boundaries))
        latitude_list.append(lat)
        longitude_list.append(long)
        severity_list.append(str(severity_value))

        if (severity_value == 0):
            severity_clr.append("darkgreen")
        elif (0< severity_value and 0.25>severity_value):
            severity_clr.append("green")
        elif (0.25<= severity_value and 10>severity_value):
            severity_clr.append("lightgreen")
        elif (10<= severity_value and 100>severity_value):
            severity_clr.append("orange")
        elif (100<= severity_value and 300>severity_value):
            severity_clr.append("pink")
        elif (300<= severity_value and 1000>severity_value):
            severity_clr.append("lightred")
        elif (1000<= severity_value and 5000>severity_value):
            severity_clr.append("red")
        else:
            severity_clr.append("darkred")

    await q.page.save()


def deletePages(q):
    pages = ['result', 'map', 'error', 'result1','loadImage','about','history', 'history_error', 'history_map','history_tab']
    for page in pages:
        del q.page[page]


def cal2jd(date):
    fmt = '%Y-%m-%d'
    sdtdate = datetime.datetime.strptime(date, fmt)
    return sdtdate.toordinal() + 1721424.5


async def getSeverity(q,lat, lon, date):
    model = lgb.Booster(model_file='Model/wildfire_detector.model')
    weather_data = getData(lat, lon, date)
    if (weather_data is None):
        return None
    else:
        prediction = model.predict([weather_data])
        if(prediction[0] <= 0):
            return 0
        else:
            return prediction[0]


def getData(lat, lon, date):
    upload_list = []
    dist_list = []
 
    x = requests.get(
        "https://firestore.googleapis.com/v1/projects/nodemcu-tester/databases/(default)/documents/H2O/DATA_LOC").json()
    meta_data = x["fields"]["DATA_LOC"]["stringValue"]
    meta_data = meta_data.replace("[[", "")
    meta_data = meta_data.replace("]]", "")
    meta_data = meta_data.replace("], [", "|")
    keys = meta_data.split("|")
    for key in keys:
        upload_list.append(list(np.fromstring(key, dtype=np.float64, sep=',')))
 
    for loc in upload_list:
        dist_list.append(distance((loc[1], loc[0]), (lat, lon)).km)
 
    min_val = min(dist_list)
    out_loc = upload_list[dist_list.index(min_val)]
    # print(out_loc)
 
    location = str('%.4f' % out_loc[0])+','+str('%.4f' % out_loc[1])
    doy = datetime.datetime.strptime(date, '%Y-%m-%d').timetuple().tm_yday
    # print(location)
 
    w_data_year_req = requests.get(url+location).json()
    if("error" in w_data_year_req):
        return None
    else:
        w_data_year_req = w_data_year_req["fields"]
        w_data_year = {}
        for key in w_data_year_req:
            w_data_year[key] = w_data_year_req[key]["stringValue"]

        w_data_dict = {}
        header = ['YEAR', 'MO', 'DY', 'T2M', 'T2MDEW', 'T2MWET', 'TS', 'T2M_RANGE', 'T2M_MAX', 'T2M_MIN', 'QV2M', 'RH2M',
                  'PRECTOTCORR', 'PS', 'WS10M', 'WS10M_MAX', 'WS10M_MIN', 'WS10M_RANGE', 'WS50M', 'WS50M_MAX', 'WS50M_MIN']
        for i in range(0, 7):
            w_data = json.loads(w_data_year[str(doy-6+i)])
            for ind, val in enumerate(header[3:], start=3):
                key = val+'_'+str(i)
                w_data_dict[key] = float(w_data[ind])
        entries_to_remove = ('T2M_RANGE_0', 'QV2M_0', 'QV2M_1', 'T2M_RANGE_2', 'QV2M_2',
                             'QV2M_3', 'T2M_RANGE_4', 'T2M_RANGE_5', 'PRECTOTCORR_5', 'T2M_RANGE_6')
        for k in entries_to_remove:
            w_data_dict.pop(k, None)
        final_list = [lon, lat, cal2jd(date)]+list(w_data_dict.values())

        return final_list

def convertZip(zip_value):
    try:
        zip = float(zip_value)
    except:
        return "None"
    else:
        if (zip in postalData.index):
            address = ""
            if (str(postalData.Town[zip]) != "nan"):
                address = address + str(postalData.Town[zip])
            elif (str(postalData.Region[zip]) != "nan"):
                address = address + ", " + str(postalData.Region[zip])
            elif (str(postalData.Area[zip]) != "nan"):
                address = address + ", " + str(postalData.Area[zip])
            location = [postalData.Latitude[zip],postalData.Longitude[zip], address]
            return location
        else:
            return "None"

async def loadPage(q):
    q.page['inputLatLong'] = ui.form_card(
        box='1 2 6 4',
        items=[
            ui.text_s("Wildfire prediction for a location in North American territory can be obtained by entering relevant longitude and latitude in following fields. Date entry is used to obtain prediction result for entered date. (Note: for development purposes dates in the range of 07/01/2021 to 01/12/2021 will only be accepted)"),
            ui.textbox(name='latitude', label='Latitude', required=True,
                       placeholder="Add a value in between 17.9397 and 70.3306 ", tooltip=""),
            ui.textbox(name='longitude', label='Longitude', required=True,
                       placeholder="Add a value in between -178.8026 and -65.2569 ", tooltip=""),
            ui.date_picker(name='date_boundaries', label='Pick a Date',
                           value='2021-01-07', min="2021-01-07", max="2021-12-01"),
            ui.buttons([
                ui.button(name='submit', label='Predict', primary=True),
                # ui.button(name='showmap', label='Mark on the Map',primary=True),
            ]),
        ],
    )

    q.page['inputPostalCode'] = ui.form_card(
        box='7 2 4 4',
        items=[
            ui.text_l("Know the Geolocation?"),
            ui.textbox(name='postalCode', label='Postal/Zip Code', required=True,
                       placeholder="Only in USA Region ", tooltip=""),
            ui.buttons([
                ui.button(name='convert', label='Convert Zip Code', primary=True)
            ]),
            ui.text("-- OR --"),
            ui.button(name='showmap', label='Mark on the Map', primary=True),
        ],
    )

    q.page['loadImage'] = ui.image_card(
        box='1 6 10 5',
        title='',
        path="http://pldindustries.com/wave/loadImage2.jpg",
    )

    if q.args.showmap:
        deletePages(q)
        await showMap(q, 45.33, -107.95)
    if q.args.submit:
        deletePages(q)
        if q.args.latitude and q.args.longitude:
            try:
                lat= float(q.args.latitude)
                lon = float(q.args.longitude)
            except:
                await displayError(q,'ERROR! Enter geolocations in valid format')
            else:
                if ((float(q.args.latitude) > 17.9397) and (float(q.args.latitude) < 70.3306) and (float(q.args.longitude) > -178.8026) and (float(q.args.longitude) < -65.2569)):
                    await showResult(q, float(q.args.latitude), float(q.args.longitude))
                else:
                    await displayError(q,'ERROR! Geolocations are out of range')
        else:
            await displayError(q,'ERROR! Fill all blank areas')

    if q.args.convert:
        result = convertZip(q.args.postalCode)
        del q.page['inputPostalCode']

        if (result == "None"):
            q.page['inputPostalCode'] = ui.form_card(
                box='7 2 4 4',
                items=[
                    ui.text_l("Know the Geolocation?"),
                    ui.textbox(name='postalCode', label='Postal/Zip Code', required=True,
                            placeholder="Only in USA Region ", tooltip=""),
                    ui.buttons([
                        ui.button(name='convert', label='Convert Zip Code', primary=True)
                    ]),
                    ui.text("Invalid Data"),
                    ui.text("-- OR --"),
                    ui.button(name='showmap', label='Mark on the Map',primary=True),
                ],
            )
        else:
            del q.page['inputLatLong']
            q.page['inputLatLong'] = ui.form_card(
                box='1 2 6 4',
                items=[
                    ui.text_s("Wildfire prediction for a location in North American territory can be obtained by entering relevant longitude and latitude in following fields. Date entry is used to obtain prediction result for entered date. (Note: for development purposes dates in the range of 07/01/2021 to 01/12/2021 will only be accepted)"),
                    ui.textbox(name='latitude', label='Latitude', required=True,
                            value=str(result[0]), tooltip=""),
                    ui.textbox(name='longitude', label='Longitude', required=True,
                            value=str(result[1]), tooltip=""),
                    ui.date_picker(name='date_boundaries', label='Pick a Date',
                                value='2021-01-07', min="2021-01-07", max="2021-12-01"),
                    ui.buttons([
                        ui.button(name='submit', label='Predict', primary=True),
                        ui.button(name='clear_form', label='Clear'),
                    ]),
                ],
            )
            q.page['inputPostalCode'] = ui.form_card(
                box='7 2 4 4',
                items=[
                    ui.text_l("Know the Geolocation?"),
                    ui.textbox(name='postalCode', label='Postal/Zip Code', required=True,
                            placeholder="Only in USA Region ", tooltip=""),
                    ui.buttons([
                        ui.button(name='convert', label='Convert Zip Code', primary=True)
                    ]),
                    ui.text("Address: " + str(result[2])),
                    ui.text("-- OR --"),
                    ui.button(name='showmap', label='Mark on the Map', primary=True),
                ],
            )
            deletePages(q)
            df = pd.DataFrame({'lat':[result[0]], 'lon':[result[1]], 'name':[result[2]]})
            m = folium.Map(location=[df.iloc[0]['lat'], df.iloc[0]['lon']], tiles="Stamen Terrain", zoom_start=4)
            folium.Marker(location = [df.iloc[0]['lat'], df.iloc[0]['lon']], popup=df.iloc[0]['name'],).add_to(m)

            q.page['map'] = ui.form_card(
                box='1 6 10 5',
                items=[
                    ui.text('This is the point you have selected.'),
                    ui.frame(content=m._repr_html_(), height='400px'),
                ]
            )
    if q.args.clear_form:
        result = "None"
        q.page['inputLatLong'] = ui.form_card(
            box='1 2 6 4',
            items=[
                ui.text_s("Wildfire prediction for a location in North American territory can be obtained by entering relevant longitude and latitude in following fields. Date entry is used to obtain prediction result for entered date. (Note: for development purposes dates in the range of 07/01/2021 to 01/12/2021 will only be accepted)"),
                ui.textbox(name='latitude', label='Latitude', required=True,
                        placeholder="Add a value in between 17.9397 and 70.3306 ", tooltip=""),
                ui.textbox(name='longitude', label='Longitude', required=True,
                        placeholder="Add a value in between -178.8026 and -65.2569 ", tooltip=""),
                ui.date_picker(name='date_boundaries', label='Pick a Date',
                            value='2021-01-07', min="2021-01-07", max="2021-12-01"),
                ui.buttons([
                    ui.button(name='submit', label='Predict', primary=True),
                    # ui.button(name='showmap', label='Pin on the Map', primary=True),
                ]),
            ],
        )

        q.page['inputPostalCode'] = ui.form_card(
            box='7 2 4 4',
            items=[
                ui.text_l("Know the Geolocation?"),
                ui.textbox(name='postalCode', label='Postal/Zip Code', required=True,
                        placeholder="Only in USA Region ", tooltip=""),
                ui.buttons([
                    ui.button(name='convert', label='Convert Zip Code', primary=True)
                ]),
                ui.text("-- OR --"),
                ui.button(name='showmap', label='Mark on the Map', primary=True),
            ],
        )

    await q.page.save()


@app('/')
async def serve(q: Q):
    q.page['meta'] = ui.meta_card(
        box='',
        themes=[
            ui.theme(
                name='my-awesome-theme', 
                primary='#FF9F1C',
                text='#e8e1e1',
                card='#000000',
                page='#000000',
            )
        ],
        theme='my-awesome-theme'
    )
    q.page['head'] = ui.header_card(
        box='1 1 10 1',
        title='Defense Against WildFire',
        subtitle='Get to know whether you need a firetruck today.',
        image='http://pldindustries.com/wave/logo.png',
        items=[
            ui.button(name='refreshBtn', label='Refresh'),
            ui.button(name='showHistoryBtn', label='History'),
            ui.button(name='aboutBtn', label='About'),
            ui.link(label='Demo', path='https://drive.google.com/file/d/1nmo7erS0tv_OUt_e4FngjLXIgR9WPo5I/view?usp=sharing', target='_blank'),
        ],
    )

    caption = '''![PSR-logo](http://pldindustries.com/wave/logo_footer-1.png)<br>
    Developed By Team PSR.'''
    q.page['footer'] = ui.footer_card(
        box='1 11 10 2',
        caption=caption,
        items=[
            ui.inline(justify='end', items=[
                ui.links(label='Contact Us', width='200px', items=[
                    ui.link(label='Shamil Prematunga', path='https://www.linkedin.com/in/shamil-prematunga-139b51158/', target='_blank'),
                    ui.link(label='Pasan Dharmasiri', path='https://www.linkedin.com/in/pasanld/', target='_blank'),
                    ui.link(label='Ranush Wickramarathne', path='https://www.linkedin.com/in/ranushw/', target='_blank'),
                ]),
            ]),
        ]
    )

    if(q.args.historyBtn or q.args.showHistoryBtn):
        deletePages(q)
        df_history = pd.DataFrame(
            {
                "Lat":latitude_list,
                "Long":longitude_list,
                "Score":severity_list,
                "Color": severity_clr
            }
        )
        locations = df_history[['Lat', 'Long']]
        locationlist = locations.values.tolist()
        if (len(locationlist) == 0):
            q.page['history_error'] = ui.form_card(
                box='1 6 10 4',
                items=[
                    ui.text_xl('History data unavailable'),
                ],
            )
        else:
            map = folium.Map(location=[45.33, -107.95], zoom_start=4)
            for point in range(0, len(locationlist)):
                # print(locationlist[point])
                folium.Marker(locationlist[point], popup=df_history['Score'][point], icon=folium.Icon(color=df_history["Color"][point])).add_to(map)
            q.page['history_map'] = ui.form_card(
                box='1 6 10 4',
                items=[
                    ui.frame(content=map._repr_html_(), height='400px'),
                ]
            )
        q.page['history_tab'] = ui.form_card(
            box='1 10 10 1',
            items=[
                ui.inline(justify='end', items=[
                    ui.button(name='clearhistorytab', label='Clear History',primary=True),
                    ui.button(name='exithistorytab', label='Exit',primary=False),
                ])
            ]
        )

    elif (q.args.exithistorytab):
        deletePages(q)
        await loadPage(q)

    elif (q.args.clearhistorytab):
        deletePages(q)
        latitude_list.clear()
        longitude_list.clear()
        severity_list.clear()
        severity_clr.clear()
        await loadPage(q)

    elif (q.args.aboutBtn):
        q.page['about'] = ui.form_card(
            box='1 6 10 5',
            items=[
                ui.text_xl('About:'),
                ui.text('''
This application has been mainly developed to demonstrate the capability of effectively predicting wildlife using certain weather parameters and previous wildfire related data.

Please note that following limitations are set in the application. 

1. US region dataset has ONLY been used to train the ML model thus geo-points that can be entered are only within a limited area. (Latitude: 17.9397 to 70.3306 | Longitude: -178.8026 to -65.2569)

2. Automatic LIVE weather data acquisition function has not been implemented. Hence, valid dates which can be entered to the app is from 07.01.2021 to 01.12.2021
                '''),
                ui.text_xl('Data Collection:'),
                ui.text('The data collected via two sources to train the model.'),
                ui.link(label='1. US Wildfire Data Collection', path='https://www.kaggle.com/rtatman/188-million-us-wildfires', target='_blank'),
                ui.link(label='2. Power Nasa Data', path='https://power.larc.nasa.gov/data-access-viewer/', target='_blank'),
            ],
        )
    elif (q.args.refreshBtn):  
        await loadPage(q)
    else:
        await loadPage(q)
        # print(q.app.initialized)
    await q.page.save()

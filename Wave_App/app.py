from h2o_wave import Q, ui, app, main, data, pack
import folium
from fsplit.filesplit import Filesplit
import pickle
import numpy as np
import datetime
import os
# import io
# import base64
# from matplotlib import colors
# import numpy as np
# import matplotlib.pyplot as plt
# from PIL import Image
# import time

# from autoML import load_page

async def viewError(q):
    q.page['error'] = ui.form_card(
        box='4 6 2 1',
        items=[
            ui.text_s('Fill All Blank Areas'),
        ],
    )
    await q.page.save()

async def viewOutOfRange(q):
    q.page['error'] = ui.form_card(
        box='4 6 2 1',
        items=[
            ui.text_s('Values Are Out of Range'),
        ],
    )
    await q.page.save()

async def showMap(q:Q, lat, long):
    m = folium.Map(location=[lat, long],tiles="Stamen Terrain", zoom_start=8)
    m.add_child(folium.LatLngPopup())
 
    q.page['map'] = ui.form_card(
        box='1 6 10 5', 
        items=[
            ui.text('Map'),
            ui.frame(content=m._repr_html_(), height='400px'),
        ]
    )
    await q.page.save()

async def showResult(q,lat, long):
    q.page['result'] = ui.form_card(
        box='1 6 10 3',
        items=[
            ui.text_l('Selected Point...'),
            ui.text('Latitude: '+ str(lat)),
            ui.text('Longitude: ' + str(long)),
            ui.text('Date: ' + str(q.args.date_boundaries)),
            ui.text('Severity: ' + '0.0')
        ],
    )
    await q.page.save()

def deletePages(q):
    pages = ['result', 'map', 'error']
    for page in pages:
        del q.page[page]

def cal2jd(date):
    fmt = '%Y-%m-%d'
    sdtdate = datetime.datetime.strptime(date, fmt)
    return sdtdate.toordinal() + 1721424.5


def showSeverity(lat, lon, date):
    if(not os.path.isfile('Appdata/W_Data_Dict.pickle')):
        fs = Filesplit()

        def merge_cb(f, s):
            print("file: {0}, size: {1}".format(f, s))
        fs.merge(input_dir="Appdata", callback=merge_cb)

    else:
        print('Data File Available')
    open_file_ = open("Appdata/W_Data_Dict.pickle", "rb")
    W_Data_Dict = pickle.load(open_file_)
    open_file_.close()

    # lons = np.linspace(-168.87, -65.25694444, num=600)
    # lats = np.linspace(17.93972222, 70.3306, num=300)
    lons = []
    lats = []
    keys = list(W_Data_Dict)
    for key in keys:
        temp = key.split(',')
        # lons.append(float(temp[0]))
        lats.append(float(temp[1]))
    lats = np.sort(np.array(lats))
    lat_cat = np.searchsorted(lats, lat)
    lat_cat = round(lats[lat_cat], 4)

    for key in keys:
        temp = key.split(',')
        if(float(temp[1]) == lat_cat):
            lons.append(float(temp[0]))

    lons = np.sort(np.array(lons))
    lon_cat = np.searchsorted(lons, lon)
    lon_cat = round(lons[lon_cat], 4)

    location = str('%.4f' % lon_cat)+','+str('%.4f' % lat_cat)
    print(location)
    w_data_year = W_Data_Dict[location]
    doy = datetime.datetime.strptime(date, '%Y-%m-%d').timetuple().tm_yday

    w_data_dict = {}
    header = ['YEAR', 'MO', 'DY', 'T2M', 'T2MDEW', 'T2MWET', 'TS', 'T2M_RANGE', 'T2M_MAX', 'T2M_MIN', 'QV2M', 'RH2M',
              'PRECTOTCORR', 'PS', 'WS10M', 'WS10M_MAX', 'WS10M_MIN', 'WS10M_RANGE', 'WS50M', 'WS50M_MAX', 'WS50M_MIN']
    for i in range(0, 7):
        w_data = w_data_year[doy-6+i]
        for ind, val in enumerate(header[3:], start=3):
            key = val+'_'+str(i)
            w_data_dict[key] = float(w_data[ind])
    entries_to_remove = ('T2M_RANGE_0', 'QV2M_0', 'QV2M_1', 'T2M_RANGE_2', 'QV2M_2',
                         'QV2M_3', 'T2M_RANGE_4', 'T2M_RANGE_5', 'PRECTOTCORR_5', 'T2M_RANGE_6')
    for k in entries_to_remove:
        w_data_dict.pop(k, None)
    final_list = [lon, lat, cal2jd(date)]+list(w_data_dict.values())

    return final_list
    
async def loadPage(q):
    q.page['inputLatLong'] = ui.form_card(
        box='1 2 10 4',
        items=[
            ui.textbox(name='latitude', label='Latitude', required=True, placeholder="Add a value in between 17.9397 and 70.3306 ", tooltip=""),
            ui.textbox(name='longitude', label='Longitude', required=True, placeholder="Add a value in between -178.8026 and -65.2569 ", tooltip=""),
            ui.date_picker(name='date_boundaries', label='Pick a Date', value='2021-01-07', min="2021-01-07", max="2021-12-01"),
            ui.buttons([
                ui.button(name='submit', label='Submit', primary=True),
                ui.button(name='showmap', label='Show Map'),
            ]),
        ],
    )
    if q.args.showmap:
        deletePages(q)
        await showMap(q, 45.33, -107.95)
    if q.args.submit:
        deletePages(q)
        if q.args.latitude and q.args.longitude:
            if ((float(q.args.latitude) > 17.9397) and (float(q.args.latitude) < 70.3306) and (float(q.args.longitude) > -178.8026) and (float(q.args.longitude) < -65.2569)):
                await showResult(q, float(q.args.latitude), float(q.args.longitude))
            else:
                await viewOutOfRange(q)
        else:
            await viewError(q)

    await q.page.save()


@app('/scrape')
async def serve(q:Q):
    q.page['meta'] = ui.meta_card(
        box='',
        themes=[
            ui.theme(
                name='my-awesome-theme',
                primary='#13ebe7',
                text='#e8e1e1',
                card='#12123b',
                page='#070b1a',
            )
        ],
        theme='my-awesome-theme'
    )
    q.page['head'] = ui.header_card(
        box='1 1 10 1',
        title='Wild Fire Check Application',
        subtitle='Click and Check',
        icon='ExploreData',
    )

    await loadPage(q)


    await q.page.save()
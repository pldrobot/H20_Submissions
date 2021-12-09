from h2o_wave import Q, ui, app, main, data, pack
import folium
import io
import base64
from matplotlib import colors
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import time

async def viewError(q):
    q.page['error'] = ui.form_card(
        box='2 5 8 1',
        items=[
            ui.text_s('Fill All Blank Areas'),
        ],
    )
    await q.page.save()

async def showMap(q:Q, lat, long):
    m = folium.Map(location=[lat, long],tiles="Stamen Terrain", zoom_start=10)
    m.add_child(folium.LatLngPopup())
 
    q.page['map'] = ui.form_card(
        box='1 5 10 5', 
        items=[
            ui.text('Map'),
            ui.frame(content=m._repr_html_(), height='400px'),
        ]
    )
    await q.page.save()

async def showResult(q,lat, long):
    q.page['result'] = ui.form_card(
        box='1 5 10 2',
        items=[
            ui.text_l('Selected Point...'),
            ui.text('Latitude: '+ str(lat)),
            ui.text('Longitude: ' + str(long)),
            ui.text('Severity: ' + '0.0')
        ],
    )
    await q.page.save()

def deletePages(q):
    pages = ['result', 'map', 'error']
    for page in pages:
        del q.page[page]

async def loadPage(q):
    q.page['inputLatLong'] = ui.form_card(
        box='1 2 10 3',
        items=[
            ui.textbox(name='latitude', label='Latitude', required=True),
            ui.textbox(name='longitude', label='Longitude', required=True),
            ui.button(name='submit', label='Submit', primary=True),
            ui.button(name='showmap', label='Show Map'),
        ],
    )
    if q.args.showmap:
        deletePages(q)
        await showMap(q, 30.193626, -85.683029)
    if q.args.submit:
        deletePages(q)
        if q.args.latitude and q.args.longitude:
            await showResult(q, float(q.args.latitude), float(-85.683029))
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
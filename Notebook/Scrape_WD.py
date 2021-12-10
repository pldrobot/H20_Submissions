from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import csv


def WaitforElement(path):
    return WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, path)))


driver = webdriver.Chrome('chromedriver')
driver.get("https://power.larc.nasa.gov/data-access-viewer/")

start_cb = WaitforElement('//*[@id="jimu_dijit_CheckBox_0"]/div[1]')
start_cb.click()
driver.implicitly_wait(5)

start_bt = WaitforElement('//*[@id="mysplash"]/div[2]/div[2]')
start_bt.click()
driver.implicitly_wait(5)

comm_select = WaitforElement('//*[@id="usercommunity"]')
comm_select = Select(comm_select)
comm_select.select_by_visible_text('Renewable Energy')

avg_select = WaitforElement('//*[@id="usertemporal"]')
avg_select = Select(avg_select)
avg_select.select_by_visible_text('Daily')

file_select = WaitforElement('//*[@id="userformat"]')
file_select = Select(file_select)
file_select.select_by_visible_text('CSV')

start_date = WaitforElement('//*[@id="datepickerstart"]')
start_date.clear()
start_date.send_keys("01/01/2021")

end_date = WaitforElement('//*[@id="datepickerend"]')
end_date.clear()
end_date.send_keys("11/27/2021")

WaitforElement('//*[@id="Temperatures"]/i').click()

WaitforElement('//*[@id="T2M_anchor"]/i[1]').click()
WaitforElement('//*[@id="T2MDEW_anchor"]/i[1]').click()
WaitforElement('//*[@id="T2MWET_anchor"]/i[1]').click()
WaitforElement('//*[@id="TS_anchor"]/i[1]').click()
WaitforElement('//*[@id="T2M_RANGE_anchor"]/i[1]').click()
WaitforElement('//*[@id="T2M_MAX_anchor"]/i[1]').click()
WaitforElement('//*[@id="T2M_MIN_anchor"]/i[1]').click()

WaitforElement('//*[@id="Humidity/Precipitation"]/i').click()

WaitforElement('//*[@id="QV2M_anchor"]/i[1]').click()
WaitforElement('//*[@id="RH2M_anchor"]/i[1]').click()
WaitforElement('//*[@id="PRECTOTCORR_anchor"]/i[1]').click()

WaitforElement('//*[@id="Wind/Pressure"]/i').click()

WaitforElement('//*[@id="PS_anchor"]/i[1]').click()
WaitforElement('//*[@id="WS10M_anchor"]/i[1]').click()
WaitforElement('//*[@id="WS10M_MAX_anchor"]/i[1]').click()
WaitforElement('//*[@id="WS10M_MIN_anchor"]/i[1]').click()
WaitforElement('//*[@id="WS10M_RANGE_anchor"]/i[1]').click()
WaitforElement('//*[@id="WS50M_anchor"]/i[1]').click()
WaitforElement('//*[@id="WS50M_MAX_anchor"]/i[1]').click()
WaitforElement('//*[@id="WS50M_MIN_anchor"]/i[1]').click()
# WaitforElement('//*[@id="WS50M_RANGE_anchor"]/i[1]').click()


def download_data_file(loc):
    lat = WaitforElement('//*[@id="latdaily"]')
    lat.clear()
    lat.send_keys(loc[0])
    lon = WaitforElement('//*[@id="londaily"]')
    lon.clear()
    lon.send_keys(loc[1])

    WaitforElement('//*[@id="testbuttondaily"]').click()
    WebDriverWait(driver, 600).until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="exportCSV"]'))).click()
    WaitforElement('//*[@id="ordermore"]').click()


with open('Data.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for index, row in enumerate(spamreader):
        if(index > 1000):
            break
        download_data_file(row)

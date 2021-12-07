from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import _thread
import time
import csv


def WaitforElement(path, driver):
    return WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, path)))


def download_data_file(loc, driver):
    lat = WaitforElement('//*[@id="latdaily"]', driver)
    lat.clear()
    lat.send_keys(loc[1])
    lon = WaitforElement('//*[@id="londaily"]', driver)
    lon.clear()
    lon.send_keys(loc[0])

    start_date = WaitforElement('//*[@id="datepickerstart"]', driver)
    start_date.clear()
    start_date.send_keys(loc[2])

    end_date = WaitforElement('//*[@id="datepickerend"]', driver)
    end_date.clear()
    end_date.send_keys(loc[3])

    # WebDriverWait(driver, 600).until(EC.element_to_be_clickable(
    #     (By.XPATH, '//*[@id="exportCSV"]'))).click()
    # down_csv = driver.find_element_by_xpath('//*[@id="exportCSV"]')
    # while(not down_csv.is_enabled()):
    #     WaitforElement('//*[@id="testbuttondaily"]', driver).click()
    #     driver.implicitly_wait(5)
    WaitforElement('//*[@id="testbuttondaily"]', driver).click()
    WebDriverWait(driver, 3600).until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="exportCSV"]'))).click()
    WaitforElement('//*[@id="ordermore"]', driver).click()


def get_data(data, index):
    driver = webdriver.Chrome('chromedriver')
    driver.get("https://power.larc.nasa.gov/data-access-viewer/")

    start_cb = WaitforElement(
        '//*[@id="jimu_dijit_CheckBox_0"]/div[1]', driver)
    start_cb.click()
    driver.implicitly_wait(5)

    start_bt = WaitforElement('//*[@id="mysplash"]/div[2]/div[2]', driver)
    start_bt.click()
    driver.implicitly_wait(5)

    comm_select = WaitforElement('//*[@id="usercommunity"]', driver)
    comm_select = Select(comm_select)
    comm_select.select_by_visible_text('Renewable Energy')

    avg_select = WaitforElement('//*[@id="usertemporal"]', driver)
    avg_select = Select(avg_select)
    avg_select.select_by_visible_text('Daily')

    file_select = WaitforElement('//*[@id="userformat"]', driver)
    file_select = Select(file_select)
    file_select.select_by_visible_text('CSV')

    WaitforElement('//*[@id="Temperatures"]/i', driver).click()

    WaitforElement('//*[@id="T2M_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="T2MDEW_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="T2MWET_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="TS_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="T2M_RANGE_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="T2M_MAX_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="T2M_MIN_anchor"]/i[1]', driver).click()

    WaitforElement('//*[@id="Humidity/Precipitation"]/i', driver).click()

    WaitforElement('//*[@id="QV2M_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="RH2M_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="PRECTOTCORR_anchor"]/i[1]', driver).click()

    WaitforElement('//*[@id="Wind/Pressure"]/i', driver).click()

    WaitforElement('//*[@id="PS_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="WS10M_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="WS10M_MAX_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="WS10M_MIN_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="WS10M_RANGE_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="WS50M_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="WS50M_MAX_anchor"]/i[1]', driver).click()
    WaitforElement('//*[@id="WS50M_MIN_anchor"]/i[1]', driver).click()
    # WaitforElement('//*[@id="WS50M_RANGE_anchor"]/i[1]',driver).click()
    for cnt, row in enumerate(data):
        download_data_file(row, driver)
        print("%d: %d out of %d" % (index, cnt, len(data)))
    driver.close()


Data_List = []

with open('Data.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for index, row in enumerate(spamreader):
        # download_data_file(row)
        Data_List.append(row)

step = int(len(Data_List)/4)
Data_List_parts = [Data_List[x:x+step] for x in range(0, len(Data_List), step)]

#_thread.start_new_thread(get_data, (Data_List_parts[0],))
for index, data in enumerate(Data_List_parts):
    _thread.start_new_thread(get_data, (data, index,))
    time.sleep(10)

while(1):
    pass

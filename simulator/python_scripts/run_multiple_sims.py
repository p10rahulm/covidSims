#Copyright [2020] [Indian Institute of Science, Bangalore]
#SPDX-License-Identifier: Apache-2.0

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from tqdm import trange

def set_text_field(driver, id_name, value):
    element = driver.find_element_by_id(id_name)
    element.clear()
    element.send_keys(str(value))
    return (True)

def set_drop_field(driver, id_name, value):
    select = Select(driver.find_element_by_id(id_name))
    #element.clear()
    select.select_by_value(str(value))
    return (True)

def click_on_button(driver, id_name):
    element = driver.find_element_by_id(id_name)
    element.click()
    return (True)    

download_dir = '/Users/nihesh/Desktop/'
options = Options()
options.add_experimental_option("prefs", {
  "download.default_directory": download_dir,
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True,
  "profile.content_settings.exceptions.automatic_downloads.*.setting": 1 
})

driverLocation = '/Users/nihesh/Desktop/markov_simuls/simulator/chromedriver'
driver = webdriver.Chrome(executable_path=driverLocation, options=options)

NO_INTERVENTION = 0
CASE_ISOLATION = 1
HOME_QUARANTINE = 2
LOCKDOWN = 3
CASE_ISOLATION_AND_HOME_QUARANTINE = 4
CASE_ISOLATION_AND_HOME_QUARANTINE_SD_70_PLUS = 5
LOCKDOWN_21_CI_HQ_SD_70_PLUS_21_CI = 6
LOCKDOWN_21 = 7

for i in trange(2):
    flag = 1
    driver.get('http://localhost:8000')
    set_text_field(driver, 'numDays', 100)
    set_text_field(driver, 'Incubation', 4.5)
    set_text_field(driver, 'asymptomaticMean', 0.5)
    set_text_field(driver, 'symptomaticMean', 5)
    set_text_field(driver, 'symtomaticFraction', 0.5)
    set_text_field(driver, 'meanHospitalPeriod', 8)
    set_text_field(driver, 'meanICUPeriod', 8)
    set_text_field(driver, 'betaHouse', 0.47)
    set_text_field(driver, 'betaWork', 0.376)
    set_text_field(driver, 'betaSchools', 0.752)
    set_text_field(driver, 'betaCommunity', 0.3395)
    set_text_field(driver, 'initFrac', 0.0001)
    set_text_field(driver, 'compliance', 0.9)
    set_drop_field(driver, 'interventions', NO_INTERVENTION)
    click_on_button(driver, 'run_button')
    while(flag):
        if (os.path.exists(download_dir+'my_data.csv') and os.path.exists(download_dir+'my_data_all_together.csv')):
            os.rename(download_dir+'my_data_all_together.csv', download_dir+'my_data_all_together_'+str(i)+'.csv')
            os.rename(download_dir+'my_data.csv', download_dir+'my_data_'+str(i)+'.csv')
            flag = 0

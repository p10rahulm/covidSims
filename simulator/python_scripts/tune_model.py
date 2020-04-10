#Copyright [2020] [Indian Institute of Science, Bangalore]
#SPDX-License-Identifier: Apache-2.0

from calculate_means import calculate_means
from calculate_r0 import calculate_r0
from calibrate import calibrate
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
from tqdm import trange

def clear_dir(directory):
    file_list = os.listdir(directory)
    for file_name in file_list:
        os.remove(directory+file_name)
    return (True)

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

download_dir = '/home/niheshkumarr/Documents/COVID-19/sim_data/temp_files/'
result_dir = './data/'

options = Options()
options.add_argument('--headless')
options.add_experimental_option("prefs", {
  "download.default_directory": download_dir,
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True,
  "profile.content_settings.exceptions.automatic_downloads.*.setting": 1 
})

driverLocation = '/home/niheshkumarr/Downloads/chromedriver'

NO_INTERVENTION = 0
CASE_ISOLATION = 1
HOME_QUARANTINE = 2
LOCKDOWN = 3
CASE_ISOLATION_AND_HOME_QUARANTINE = 4
CASE_ISOLATION_AND_HOME_QUARANTINE_SD_70_PLUS = 5
LOCKDOWN_21_CI_HQ_SD_70_PLUS_21_CI = 6
LOCKDOWN_21 = 7

NUM_SIM = 100
MULT_FACTOR = 1
EPSILON = 0.025

continue_run = True

target_r0 = 2.473
count = 1

BETA_HOUSE = 0.47
BETA_WORK = 0.47
BETA_SCHOOL = 0.94
BETA_COMMUNITY =  0.097*3.5
BETA_SCALE_FACTOR = 1
INIT_FRAC_SCALE_FACTOR = 1

number_of_days = 27 # number of days to calibrate
resolution = 4 # number of steps per day

while (continue_run):
    
    clear_dir(download_dir)
    driver = webdriver.Chrome(executable_path=driverLocation, options=options)
    driver.get('http://localhost:8000')
    file_count = 0    

    for i in trange(NUM_SIM):
        driver.refresh()
        set_text_field(driver, 'numDays', 70)
        set_text_field(driver, 'Incubation', 4.5)
        set_text_field(driver, 'asymptomaticMean', 0.5)
        set_text_field(driver, 'symptomaticMean', 5)
        set_text_field(driver, 'symtomaticFraction', 0.5)
        set_text_field(driver, 'meanHospitalPeriod', 8)
        set_text_field(driver, 'meanICUPeriod', 8)
        set_text_field(driver, 'betaHouse', BETA_HOUSE*BETA_SCALE_FACTOR)
        set_text_field(driver, 'betaWork', BETA_WORK*BETA_SCALE_FACTOR)
        set_text_field(driver, 'betaSchools', BETA_SCHOOL*BETA_SCALE_FACTOR)
        set_text_field(driver, 'betaCommunity', BETA_COMMUNITY*BETA_SCALE_FACTOR)
        set_text_field(driver, 'betaPT', 0)
        set_text_field(driver, 'initFrac', 0.0001*INIT_FRAC_SCALE_FACTOR)
        set_text_field(driver, 'compliance', 0.9)
        set_drop_field(driver, 'interventions', NO_INTERVENTION)
        click_on_button(driver, 'run_button')
        time.sleep(2)
                
        try:
            os.rename(download_dir+'my_data_all_together.csv', download_dir+'my_data_all_together_'+str(i)+'.csv')
            os.rename(download_dir+'my_data.csv', download_dir+'my_data_'+str(i)+'.csv')
            file_count += 1
        except:
            pass

    driver.quit()
    
    calculate_means(download_dir, result_dir)
    # sim_r0 = calculate_r0(10, 27, 4) 
    # error_r0 = target_r0 - sim_r0
    
    
    [flag, init_frac_mult_factor, step_beta_h, step_beta_w, step_beta_c, delay] = calibrate(resolution,count)
    count+=1    
    if flag == True:
        continue_run = False
    else:
        BETA_HOUSE = BETA_HOUSE + step_beta_h
        BETA_WORK = BETA_WORK + step_beta_w
        BETA_SCHOOL = BETA_SCHOOL + step_beta_w
        BETA_COMMUNITY = BETA_COMMUNITY + step_beta_c
        #BETA_SCALE_FACTOR = beta_mult_factor
        INIT_FRAC_SCALE_FACTOR = INIT_FRAC_SCALE_FACTOR*init_frac_mult_factor

    print ('Flag: ', flag, 'BETA_HOUSE ', BETA_HOUSE, 'BETA_WORK',BETA_WORK, 'BETA_SCHOOL:', BETA_SCHOOL, 'BETA_COMMUNITY:', BETA_COMMUNITY )
    print ('Successfully created ', file_count, ' simulation files..')   
    

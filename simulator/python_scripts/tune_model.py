#Copyright [2020] [Indian Institute of Science, Bangalore]
#SPDX-License-Identifier: Apache-2.0

from calculate_means import calculate_means
from calculate_r0 import calculate_r0
from calibrate import calibrate
from joblib import Parallel, delayed
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time

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

def run_sim(driverLocation, options, simNum, params): 
    driver = webdriver.Chrome(executable_path=driverLocation, options=options)
    driver.get('http://localhost:9000')
    set_text_field(driver, 'simNum', simNum)
    set_text_field(driver, 'numDays', params['numDays'])
    set_text_field(driver, 'Incubation', params['incubation'])
    set_text_field(driver, 'asymptomaticMean', params['asymptomaticMean'])
    set_text_field(driver, 'symptomaticMean', params['symptomaticMean'])
    set_text_field(driver, 'symtomaticFraction', params['symtomaticFraction'])
    set_text_field(driver, 'meanHospitalPeriod', params['meanHospitalPeriod'])
    set_text_field(driver, 'meanICUPeriod', params['meanICUPeriod'])
    set_text_field(driver, 'betaHouse', params['betaHouse'])
    set_text_field(driver, 'betaWork', params['betaWork'])
    set_text_field(driver, 'betaSchools', params['betaSchools'])
    set_text_field(driver, 'betaCommunity', params['betaCommunity'])
    set_text_field(driver, 'betaPT', params['betaPT'])
    set_text_field(driver, 'initFrac', params['initFrac']*params['initFracScaleFactor'])
    set_text_field(driver, 'compliance', params['compliance'])
    set_drop_field(driver, 'interventions', params['interventions'])
    click_on_button(driver, 'run_button')
    time.sleep(2) 
    driver.quit()
    return (True)

cur_dir = os.getcwd()
folder_tree = cur_dir.split('/')
download_dir = ''
chrome_binary_location = ''
driverLocation = ''

for i in range(len(folder_tree)-2):
    download_dir += (folder_tree[i] + '/')
    chrome_binary_location += (folder_tree[i] + '/')
    driverLocation +=  (folder_tree[i] + '/')   

download_dir += 'sim_data/'
chrome_binary_location += 'Chrome_standalone/ChromePortableGCPM/data/chrome'
driverLocation += 'chromedriver'

result_dir = './data/'

options = Options()
options.binary_location = chrome_binary_location
options.add_argument('--headless')
options.add_experimental_option("prefs", {
  "download.default_directory": download_dir,
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True,
  "profile.content_settings.exceptions.automatic_downloads.*.setting": 1 
})

NO_INTERVENTION = 0
CASE_ISOLATION = 1
HOME_QUARANTINE = 2
LOCKDOWN = 3
CASE_ISOLATION_AND_HOME_QUARANTINE = 4
CASE_ISOLATION_AND_HOME_QUARANTINE_SD_70_PLUS = 5
LOCKDOWN_21_CI_HQ_SD_70_PLUS_21_CI = 6
LOCKDOWN_21 = 7
LD_21_CI_HQ_SD70_SC_21_SC_42 = 8
LD_21_CI_HQ_SD70_SC_21 = 9    
LD_21_CI_HQ_SD70_SC_OE_30 = 10 

# Calibration setting... 
NUM_SIM = 48
continue_run = True
count = 1
number_of_days = 27 # number of days to calibrate
resolution = 4 # number of steps per day
num_cores = 6

# Simulation parameters...
NUM_DAYS = 150
INCUBATION = 4.5
ASYMPTOTIC_MEAN = 0.5
SYMPTOTIC_MEAN = 5
SYMTOMATIC_FRACTION = 0.66
MEAN_HOSPITAL_PERIOD = 8
MEAN_ICU_PERIOD = 8
BETA_HOUSE = 1.2410 
BETA_WORK = 0.9289
BETA_SCHOOL = 2*BETA_WORK #1.8387
BETA_COMMUNITY = 0.2319
BETA_PT = 0
INIT_FRAC = 0.001
BETA_SCALE_FACTOR = 1
INIT_FRAC_SCALE_FACTOR = 1
COMPLIANCE = 0.9
INTERVENTION = NO_INTERVENTION

while (continue_run):
    
    clear_dir(download_dir)
    
    params = { 'numDays': NUM_DAYS, 'incubation': INCUBATION, 'asymptomaticMean':  ASYMPTOTIC_MEAN, 'symptomaticMean': SYMPTOTIC_MEAN,
               'symtomaticFraction': SYMTOMATIC_FRACTION, 'meanHospitalPeriod': MEAN_HOSPITAL_PERIOD, 'meanICUPeriod': MEAN_ICU_PERIOD,
               'betaHouse': BETA_HOUSE, 'betaWork': BETA_WORK, 'betaSchools': BETA_SCHOOL, 'betaCommunity': BETA_COMMUNITY, 'betaPT': BETA_PT,
               'initFrac': INIT_FRAC, 'initFracScaleFactor': INIT_FRAC_SCALE_FACTOR, 'compliance': COMPLIANCE, 'interventions': INTERVENTION }   
    
    print ('Parameter:', params)    

    processed_list = Parallel(n_jobs=num_cores)(delayed(run_sim)(driverLocation, options, simNum, params) for simNum in range(NUM_SIM))
     
    calculate_means(download_dir, result_dir) 
    
    [flag, BETA_SCALE_FACTOR, step_beta_h, step_beta_w, step_beta_c, delay] = calibrate(resolution,count)
    count+=1    
    if flag == True:
        continue_run = False
    else:
        print ('BETA_HOUSE ', BETA_HOUSE, 'BETA_WORK',BETA_WORK, 'BETA_SCHOOL:', BETA_SCHOOL, 'BETA_COMMUNITY:', BETA_COMMUNITY )
 
        BETA_HOUSE = max(BETA_HOUSE + step_beta_h,0)*BETA_SCALE_FACTOR
        BETA_WORK = max(BETA_WORK + step_beta_w,0)*BETA_SCALE_FACTOR
        BETA_SCHOOL = max(BETA_SCHOOL + step_beta_w,0)*BETA_SCALE_FACTOR
        BETA_COMMUNITY = max(BETA_COMMUNITY + step_beta_c,0)*BETA_SCALE_FACTOR
        #INIT_FRAC_SCALE_FACTOR = INIT_FRAC_SCALE_FACTOR*init_frac_mult_factor

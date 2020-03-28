#Copyright [2020] [Indian Institute of Science, Bangalore]
#SPDX-License-Identifier: Apache-2.0

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import trange

options = Options()
options.add_experimental_option("prefs", {
  "download.default_directory": '/Users/nihesh/Desktop/Sim_data/No_interventions',
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True,
  "profile.content_settings.exceptions.automatic_downloads.*.setting": 1 
})

driverLocation = '/Users/nihesh/Documents/COVID-19/markov_simuls/simulator/chromedriver'
driver = webdriver.Chrome(executable_path=driverLocation, options=options)

for i in trange(100):
    driver.get('http://localhost:8000')
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime
import numpy as np
import time
import os

from sqlalchemy import create_engine, MetaData # database connection
import datetime as dt
from zipfile import ZipFile
from nsefolder2pickle import NseFolder2Pickle; 

class NseAutoDwn:
    def __init__(self,csvfolder_path="D:/SoftwareWebApps/Python/python_wb/Stocks/Data/NSE/",
                 pickle_path='D:\SoftwareWebApps\Python\python_wb\Stocks\Data\stock_pickle\\'):
        self.csvfolder_path=csvfolder_path
        self.pickle_path=pickle_path
        
    def getbhavbydate(self,driver,datestr):
        driver.get("https://www.nseindia.com/products/content/equities/equities/archieve_eq.htm")
        report_eleme = Select(driver.find_element_by_id('h_filetype'))
        report_eleme.select_by_visible_text('Bhavcopy')
        datefield =  driver.find_element_by_id('date')
        datefield.send_keys(datestr)
        time.sleep(2)
        # datefield.perform()
        dayfield=driver.find_elements(By.CLASS_NAME, '  ui-datepicker-current-day')
        dayfield[0].click()

        time.sleep(1)

        getdata=driver.find_elements(By.CLASS_NAME, 'getdata-button')

        getdata[0].click()
        time.sleep(2)
        try:
            filelink=driver.find_element_by_xpath("//table/tbody/tr/td/a")
            filelink.click()
            return True
        except:
            print("File doen't exists")
            return False

    def main(self):
        # n=NseFolder2Pickle(self.csvfolder_path,self.pickle_path);
        # dirlist_written=n.load_pkl(self.pickle_path+'wrtitten_files.pkl')

        files_downloaded=np.array(os.listdir(self.csvfolder_path))
        dts=[datetime.strptime(fname[2:11],'%d%b%Y') for fname in files_downloaded]
        # print(np.argsort(dts).astype(np.uint32))
        files_downloaded=files_downloaded[np.argsort(dts)]
        
        d=dt.datetime.strptime(files_downloaded[-1],'cm%d%b%Ybhav.csv.zip')
        
        dtthen=dt.datetime.now()
        recentdate=dt.datetime.now().toordinal()
        olddate=d.toordinal()+1
        
        if(olddate>recentdate): 
            print("Nothing to be downloaded...")
            return
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory" : self.csvfolder_path}

        chromeOptions.add_experimental_option("prefs",prefs)
        chromedriver = "D:/Installations/chromedriver.exe"
        driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)


        for i in range(olddate,recentdate+1,1): #728110
            dtcurrent=dt.datetime.now()
            d = dt.date.fromordinal(i)    
            if (d.strftime('%a')!='Sun'):
                print(d.strftime("%d-%m-%Y %a"))
                self.getbhavbydate(driver,d.strftime("%d-%m-%Y"))
                print("time took to download this file is {}".format(dt.datetime.now()-dtcurrent))
        print("time took to download all files {}".format(dt.datetime.now()-dtthen))
        driver.close()
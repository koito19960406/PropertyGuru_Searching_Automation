#!/usr/bin/env python
# coding: utf-8

# In[8]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import datetime
import csv
import openpyxl
from openpyxl import Workbook
import pandas as pd
import smtplib
import config 
import schedule
import time


# In[9]:


# get a list of url for listings that were released within 1 week
def get_url(url):

    #open chrome in incognito mode
    options = webdriver.ChromeOptions()
    options.add_argument(' -- incognito')
    browser = webdriver.Chrome(chrome_options=options)
    browser.get(url)

    # wait for browser to open for 10 sec
    timeout = 10
    try:
        WebDriverWait(browser, timeout).until(
        EC.visibility_of_element_located(
        (By.XPATH, '//*[@id="search-results-container"]/div[2]/div[1]/div[2]/div[2]/section/div[1]/div/div[2]/div[1]')
        )
        )
    except TimeoutException:
        print('Timed Out Waiting for page to load')
        browser.quit()

    # go through the pages
    url_list=[]
    while True:
        listing_list=browser.find_elements_by_xpath('//*[@id="search-results-container"]/div[2]/div[1]/div[2]/div[2]/section/div[2]/div')
        # get URL of listing
        for listing in listing_list:
            try:
                recency=listing.find_element_by_css_selector('div.listing-recency').text.strip()
                if int(recency[0])>1 and recency[1]=='w':
                    break
                else:
                    url=listing.find_element_by_class_name('nav-link').get_attribute('href')
                    url_list.append(url)
            except NoSuchElementException:
                pass

        # click the next button  
        try:
            next_btn=browser.find_element_by_class_name('pagination-next')
            next_btn.click()
        except ElementNotInteractableException:
            break

    browser.quit()
    return url_list

# get the listing that has no owner
def get_no_owner(url_list):
    no_owner_url_list=[]
    for url in url_list:
        #open chrome in incognito mode
        options = webdriver.ChromeOptions()
        options.add_argument(' -- incognito')
        browser = webdriver.Chrome(chrome_options=options)
        browser.get(url)

        # wait for browser to open for 10 sec
        timeout = 10
        try:
            WebDriverWait(browser, timeout).until(
            EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="details"]/div/div[2]')
            )
            )
        except TimeoutException:
            print('Timed Out Waiting for page to load')
            browser.quit()
        
        desc=browser.find_element_by_class_name('listing-details-text').text.strip()
        low_case_desc=desc.lower()
        no_owner='no owner'
        if no_owner in low_case_desc:
            no_owner_url_list.append(url)

        browser.quit()
    
    return no_owner_url_list

def send_email(subject,msg):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(config.EMAIL_ADDRESS_SENDER, config.PASSWORD)
        message = 'Subject: {}\n\n{}'.format(subject, msg)
        server.sendmail(config.EMAIL_ADDRESS_SENDER, config.EMAIL_ADDRESS_RECEIVER, message)
        server.quit()
        print("Success: Email sent!")
    except:
        print("Email failed to send.")

def main():
    url = "https://www.propertyguru.com.sg/property-for-rent?district_code%5B%5D=D05&market=residential&freetext=D05+Buona+Vista+%2F+West+Coast+%2F+Clementi+New+Town&district_code%5B%5D=D05&minprice=900&maxprice=1200&lease_term%5B%5D=ST&lease_term%5B%5D=FL&furnishing%5B%5D=FULL&newProject=all&unselected=DISTRICT%7CD05"
    url_list=get_url(url)
    no_owner_url_list=get_no_owner(url_list)
    if len(no_owner_url_list)>0:
        msg=''
        for i,no_owner_url in enumerate(no_owner_url_list):
            msg+=str(i+1)+'. '+no_owner_url+'\n'
        send_email("New Housing List!", msg)


# In[15]:


if __name__ == '__main__':
    main()


# In[ ]:





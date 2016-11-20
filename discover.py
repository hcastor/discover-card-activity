import time
import random
import csv
import sqlite3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome("chromedriver.exe", chrome_options = chrome_options)
driver.implicitly_wait(20) # seconds

driver.get("https://www.discovercard.com")
time.sleep(random.uniform(3, 4))

user_id = driver.find_element_by_id('userid-content')
user_id.send_keys('')
password = driver.find_element_by_id('password-content')
password.send_keys('')
login = driver.find_element_by_id('log-in-button')
action = webdriver.common.action_chains.ActionChains(driver)
action.move_to_element_with_offset(password, 0, 197)
action.click()
action.perform()

time.sleep(5)

driver.find_elements_by_xpath("//*[contains(text(), 'Activity & Payments')]")[0].click()
driver.find_elements_by_xpath("//*[contains(text(), 'Spend Analyzer')]")[0].click()
time.sleep(10)
questions = driver.find_elements_by_xpath("//*[contains(text(), 'Questions?')]")[0]
action = webdriver.common.action_chains.ActionChains(driver)
action.move_to_element_with_offset(questions, 100, 105)
action.click()
action.perform()


conn = sqlite3.connect('example.db')
c = conn.cursor()
# Create table
c.execute('''CREATE TABLE if not exists discover
             (category text, description text, amount real, post_date date, trans_date date)''')

# c.execute('SELECT trans_date FROM discover ORDER BY trans_date DESC LIMIT 1')
# print c.fetchone()[0]

# today = datetime.now()
# this_month = (datetime(year=today.year, month=today.month, day=1).date(),)
# c.execute('SELECT trans_date FROM discover WHERE trans_date >= ? ORDER BY trans_date DESC', this_month)
# print c.fetchall()[-1]

new_transations = []
with open('../Downloads/Discover-Spend-Analyzer-.csv', 'r') as csv_input:
	reader = csv.DictReader(csv_input)
	
	new_data_found = False
	for row in reader:
		row['Amount'] = float(row['Amount'])
		post_date = datetime.strptime(row['Post Date'], "%m/%d/%Y").date()
		trans_date = datetime.strptime(row['Trans. Date'], "%m/%d/%Y").date()
		row_tuple = (row['Category'], row['Description'], row['Amount'], post_date, trans_date)
		if not new_data_found:
			c.execute('SELECT * FROM discover WHERE category=? AND description=? AND amount=? AND post_date=? AND trans_date=?', row_tuple)
			row_exists = c.fetchone()
			if row_exists:
				continue
			else:
				new_data_found = True

		new_transations.append(row_tuple)

c.executemany('INSERT INTO discover VALUES (?,?,?,?,?)', new_transations)
conn.commit()

conn.close()
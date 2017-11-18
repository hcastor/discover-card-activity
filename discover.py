import datetime
import os
import random
import time
import traceback

from selenium import webdriver

from secrets import PASSWORD, USERNAME


def get_csv_count():
    """
    Returns the total number of csvs in /data
    Used to determine if a csv was downloaded or not
    """
    return len([each for each in os.listdir('/data') if each.endswith('.csv')])


def init_selenium(implicitly_wait=20, page_load_timeout=10):
    """
    Creates a browsermob-proxy and selenium driver
    """

    # Waits 2 seconds to let selenium start up
    time.sleep(2)

    try:
        # create firefox profile
        # alls automatic downloads
        fp = webdriver.FirefoxProfile()
        # fp.set_preference("plugin.state.flash", 2)
        fp.set_preference('browser.download.folderList', 2)
        fp.set_preference('browser.download.manager.showWhenStarting', False)
        fp.set_preference('browser.download.dir', '/data')
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/csv;charset=ISO-8859-1")
        dc = webdriver.DesiredCapabilities.FIREFOX
        dc['firefox_profile'] = fp.encoded
        driver = webdriver.Remote(
            command_executor=r"http://selenium-server:4444/wd/hub",
            desired_capabilities=dc,
        )
        driver.implicitly_wait(implicitly_wait)
        driver.set_page_load_timeout(page_load_timeout)

        return driver
    except:
        raise Exception(
            "Error starting selenium: traceback: {0}".format(
                traceback.format_exc()
            )
        )


def main():
    """
    Logins into discover.com
    Downloads spendanalyzer csv for 2014-currentmonth
    TODO: allow params to be set in discover url to get other dates
    """

    csv_count = get_csv_count()

    driver = init_selenium()

    driver.get("https://www.discovercard.com")
    time.sleep(random.uniform(3, 4))

    # Login
    login_div = driver.find_element_by_class_name('content-login')
    user_id = login_div.find_element_by_id('userid-content')
    user_id.send_keys(USERNAME)
    password = login_div.find_element_by_id('password-content')
    password.send_keys(PASSWORD)
    login_div.find_element_by_id('log-in-button').click()
    time.sleep(random.uniform(2, 4))

    # Hit spendanalyzer csv url directly
    # It will always time out since firefox doesnt see any response
    try:
        start_date = 20140101
        # hack to get end_date currentYearcurrentMonthEndOfMonth
        next_month = datetime.datetime.now().date().replace(day=28) + datetime.timedelta(days=4)  # this will never fail
        end_date = str(next_month - datetime.timedelta(days=next_month.day)).replace('-', '')
        driver.get(
            f'https://card.discover.com/cardmembersvcs/spendanalyzer/app/spend.csv?date={start_date}&endDate={end_date}&outputFormat=csv&sortCol=transDate&sortAsc=Y&submit=Download'
        )
    except:
        pass

    if not get_csv_count() > csv_count:
        raise Exception('Error, did not download a csv')

    print('Downloaded csv')

    # unused code
    # This code goes to spend Analyzer and clicks to download the csv
    # most have flash installed

    # driver.find_elements_by_xpath("//*[contains(text(), 'Activity & Payments')]")[0].click()
    # driver.find_elements_by_xpath("//*[contains(text(), 'Spend Analyzer')]")[0].click()
    # time.sleep(30)
    # driver.save_screenshot('/data/spend_analysier.png')
    # questions = driver.find_elements_by_xpath("//*[contains(text(), 'Questions?')]")[0]
    # action = webdriver.common.action_chains.ActionChains(driver)
    # action.move_to_element_with_offset(questions, 100, 105)
    # action.click()
    # action.perform()
    # time.sleep(1)
    # driver.save_screenshot('/data/spend_analysier1.png')
    # action.move_by_offset(-370, 250)
    # action.click()
    # action.perform()
    # time.sleep(1)
    # driver.save_screenshot('/data/spend_analysier2.png')
    # action.move_by_offset(-170, 70)
    # action.click()
    # action.perform()
    # driver.save_screenshot('/data/spend_analysier3.png')


if __name__ == '__main__':
    main()

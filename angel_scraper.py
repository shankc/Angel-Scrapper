# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import json
import selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from validate_email import validate_email 
from google import search
from googleapiclient.discovery import build
from lxml import html
import pandas as pd


COOKIE = '__utma=242977874.1904356093.1467698421.1475821922.1475824953.46; __utmv=242977874.|2=created_at=20150802=1^3=investor=false=1^4=talent%20profile=true=1^5=q=3=1; mp_6a8c8224f4f542ff59bd0e2312892d36_mixpanel=%7B%22distinct_id%22%3A%20%221431679%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22utm_source%22%3A%20%22top_nav_home%22%2C%22%24username%22%3A%20%22mayuukh-varshney%22%2C%22angel%22%3A%20false%2C%22candidate%22%3A%20true%2C%22roles%22%3A%20%5B%0A%20%20%20%20%22developer%22%2C%0A%20%20%20%20%22mobile_developer%22%0A%5D%2C%22quality_ceiling%22%3A%20%223%22%2C%22utm_medium%22%3A%20%22email%22%2C%22utm_campaign%22%3A%20%22talent-startup_interested_email%22%2C%22utm_content%22%3A%20%22startup-name%22%2C%22utm_term%22%3A%20%22fabulyst%22%2C%22%24search_engine%22%3A%20%22google%22%7D; fs_uid=www.fullstory.com`1JRNY`6571243146838016:5724160613416960`1431679`; ajs_anonymous_id=%225f2f7e7a6ccb1e6db65bf2f382bae6e5%22; _gat=1; _angellist=23acd08ea83d15a4ac7a6a540cd00eba; _ga=GA1.2.1904356093.1467698421; _gid=GA1.2.1900087845.1511886962; ajs_group_id=null; ajs_user_id=%221431679%22; amplitude_idangel.co=eyJkZXZpY2VJZCI6ImZkZmY2OGUyLTk4ZTYtNDBhZi1hOTViLTQwYjIyZWJiYzcwZlIiLCJ1c2VySWQiOiIxNDMxNjc5Iiwib3B0T3V0IjpmYWxzZSwic2Vzc2lvbklkIjoxNTEyNDAwMzU1MjAyLCJsYXN0RXZlbnRUaW1lIjoxNTEyNDAwNTEzNjUyLCJldmVudElkIjoxNDc1LCJpZGVudGlmeUlkIjo4NjQsInNlcXVlbmNlTnVtYmVyIjoyMzM5fQ=='

headers = {
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Cookie': COOKIE,
	'Host': 'angel.co',
	'Origin': 'https://angel.co',
	'Referer': 'https://angel.co/companies',
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
	'X-CSRF-Token': 'zIvGnKYNL9xHjri+7fuqGIz0/7bvm6xEmDE2QtD5jTBmK6v5Oo63+n6jYTZIoXJjxEGVQGik2l0vCKN6wN7z9A==',
	'X-Requested-With': 'XMLHttpRequest'
}

# driver = webdriver.PhantomJS()
ANGEL_SEARCH_IDS_URL = 'https://angel.co/company_filters/search_data'
ANGEL_SEARCH_COMPANIES_URL='https://angel.co/companies/startups?'
PARAM_STRING = '&total={0}&page={1}&sort=signal&new=false&hexdigest={2}'
STARTUP_ID_PARAM = 'ids%5B%5D='
ANGEL_LIST_URL ='https://angel.co/'
startup_dict = {}
GOOGLE_POSITION_TEXT = " ceo linkedin"
ANGEL_LIST_SEARCH_QUERY_LIMIT = 20
API_KEY = 'AIzaSyCjcyL0WEcZN_Se7RdMFFFBQjBN4UpUUK0'
SEARCH_ENGINE_ID = '012122631653900561876:twjbsqmjf1m'
DOMAIN_SEARCH_LINK = 'https://autocomplete.clearbit.com/v1/companies/suggest?query='

driver = webdriver.Chrome('/Users/mayuukhvarshney/documents/ChromeWebDriver/chromedriver')


def google_search(search_term,**kwargs):
    service = build("customsearch", "v1", developerKey=API_KEY)
    res = service.cse().list(q=search_term, cx=SEARCH_ENGINE_ID, **kwargs).execute()
    return res['items']

def post_response_for_page_no(page):
    
    response = requests.post(ANGEL_SEARCH_IDS_URL , data={u'sort': u'signal', u'page': page}, headers=headers)
    return json.loads(response.text)

def build_search_result_url(post_response):
    
    id_param_string= STARTUP_ID_PARAM + str(post_response ['ids'][0])
    
    for id in post_response ['ids'][1:]:
        id_param_string = id_param_string + '&' + STARTUP_ID_PARAM  + str(id)
        
    return id_param_string
    
def build_param_string(post_response):
    
    page_param_string= PARAM_STRING.format(post_response['total'], post_response ['page'], post_response['hexdigest'])
    
    return page_param_string

def build_final_startup_search_url(id_param_string,page_param_string):
    
    return ANGEL_SEARCH_COMPANIES_URL+ id_param_string + page_param_string

def element_exisits(xpath):
    try:
        driver.find_element_by_class_name(xpath)
    except NoSuchElementException:
        return False
    return True

def get_startup_detail_html(startups_list_url):
    
    startup_details = requests.get(startups_list_url)
    html = json.loads(startup_details.text)['html']
    
    return BeautifulSoup(html)

def Linkedin_login():

    driver.find_element_by_xpath('//*[@id="join-form"]/p[3]/a').click()

    username = driver.find_element_by_class_name('login-email')
    password = driver.find_element_by_class_name('login-password')

    username.send_keys('username')
    password.send_keys('password')

    driver.find_element_by_xpath('//*[@id="login-submit"]').click()

    return get_designation()

def get_designation():
    
    profile_information = {}
    WebDriverWait(driver,3).until(lambda driver: driver.find_element_by_class_name('background-details').is_displayed())
    position = driver.find_element_by_class_name('background-details').find_element_by_tag_name('h3')
    name = driver.find_element_by_css_selector('div.pv-top-card-section__body').find_element_by_tag_name('h1')

    profile_information['name'] = name.text
    profile_information['position'] = position.text

    return profile_information
    


def get_data_from_linkedin(url):
    
    driver.get(url)

    if element_exisits('reg-form'):
        return Linkedin_login()

    elif element_exisits('background-details'):
        return get_designation()
    else:
        return "Something went wrong"

def get_linkedin_profile_links():
    print "searching linkedin profiles"
    for i in startup_dict:
        for j in google_search(i+GOOGLE_POSITION_TEXT,num=5):
            if '/in/' in j:
                startup_dict[i]['linkedin_profile'] = j
                break

def get_name_and_position_from_linkedin():
    for i in startup_dict:
        profile_info = get_data_from_linkedin(startup_dict[i]['linkedin_profile'])
        startup_dict[i]['name'] = profile_info['name']
        startup_dict[i]['position'] = profile_info['position']

def get_first_and_last_name(name):
    names = {}
    index = name.index(' ')
    first_name = name[:index]
    last_name = name[index:]

    names['first_name'] = first_name
    names['last_name'] = last_name

    return names

def get_all_name_prefixes(input_string):
  length = len(input_string)
  return [input_string[:j+1] for j in xrange(length)]   


def create_combination_array(first_name,last_name):
    possible_combinations = []
    for i in get_all_name_prefixes(first_name):
        possible_combinations.append(i)

    for i in get_all_prefixes(last_name):
        possible_combinations.append(i)
    return possible_combinations

def get_combinations(arr):
    data = []
    name_combinations = []
    combinations(data,0,0,False,False)

    return name_combinations

def insert_at_index(arr,index,element):
    if not arr:
        arr.append(element)
    elif len(a)> index:
        arr[index] = element
    else:
        arr.insert(index,element)

def combinations(data,index,i,first_name_flag,second_name_flag):
    if index == r:
        print data
        name_combinations.append(data)
        return

    if i >=len(arr):
        return
    
    if arr[i] in first_name and first_name_flag == False:
        insert_at_index(data,index,arr[i])
        combinations(data,index+1,i+1,True,second_name_flag)
    elif arr[i] in last_name and second_name_flag == False:
        insert_at_index(data,index,arr[i])
        combinations(data,index+1,i+1,first_name_flag,True)
        
    combinations(data,index,i+1,first_name_flag,second_name_flag)

def get_domain_name(company_name):
    domain_url= DOMAIN_SEARCH_LINK+company_name
    response = requests.get(domain_url)
    return json.loads(response.text)[0]['domain']


def check_email_validity(first_and_last_name_combinations,company_domain):
    for i in first_and_last_name_combinations:
        email_combination_1 = i[0]+i[1]+"@"+company_domain
        email_combination_2 = i[1]+i[0]+"@"+company_domain
        email_combination_3 = i[0]+"-"+i[1]+"@"+company_domain
        email_combination_4 = i[1]+"-"+i[0]+"@"+company_domain
        email_combination_5 = i[0]+"_"+i[1]+"@"+company_domain
        email_combination_6 = i[1]+"_"+i[0]+"@"+company_domain

        if validate_email(email_combination_1):
            return email_combination_1
        elif validate_email(email_combination_2):
            return email_combination_2
        elif validate_email(email_combination_3):
            return email_combination_3
        elif validate_email(email_combination_4):
            return email_combination_4
        elif validate_email(email_combination_5):
            return email_combination_5
        elif validate_email(email_combination_6):
            return email_combination_6

    return "email not found"


def get_founder_email():
    for i in startup_dict:
        names = get_first_and_last_name(startup_dict[i]['name'])
        name_combinations = create_combination_array(names['first_name'],names['last_name'])

        first_and_last_name_combinations = get_combinations(name_combinations)

        company_website = startup_dict[i]['website']

        if company_website:
            return check_email_validity(first_and_last_name_combinations,company_website)
        else:
            company_domain_name = get_domain_name(i)
            if company_domain_name:
                return check_email_validity(first_and_last_name_combinations,company_domain_name)
            else:
                print "company's domain name not found"       

def export_as_xlsx(data):
    df = pd.DataFrame(data)
    df = (df.T)
    df.to_excel('AngelListScrappedData.xlsx')

def scrape(page):

    post_response = post_response_for_page_no(page)

    id_param_string= build_search_result_url(post_response)
    page_param_string = build_param_string(post_response)
     
    startups_list_url = build_final_startup_search_url(id_param_string,page_param_string)

    soup = get_startup_detail_html(startups_list_url)

    base_startup = soup.select('div.base.startup' )

    for i in base_startup:
        value_dict = {}
        
        startup_name = i.find('div',{'class':'company column'}).find('div',class_='name').a
        company_id = startup_name['data-id']
        location= i.select_one('div.column.location').select_one('div.value')
        market = i.select_one('div.column.market').select_one('div.value')
        website = i.select_one('div.column.website').select_one('div.value')
        company_size = i.select_one('div.column.company_size').select_one('div.value')
        stage = i.select_one('div.column.stage').select_one('div.value')
        raised= i.select_one('div.column.raised').select_one('div.value')
        
        value_dict['company_id'] = str(company_id)
        value_dict['location'] = location.text
        value_dict['market'] = market.text
        value_dict['company_size']=company_size.text
        value_dict['stage'] = stage.text
        value_dict['website'] = website.text
        value_dict['amount_raised'] = raised.text 
        
        startup_dict[startup_name.text] = value_dict


def scrape_angel_list(search_results):

    if search_results > 400:
        print "Angel list does not allow greater than 400 per query"
    else:
        number_of_pages_to_be_scraped = int(search_results/ANGEL_LIST_SEARCH_QUERY_LIMIT)
        if number_of_pages_to_be_scraped == 0:
            number_of_pages_to_be_scraped = 1

        for i in range(0,number_of_pages_to_be_scraped):
            scrape(i)

        print "scrapping done..."





scrape_angel_list(100)

if len(startup_dict) > 0:
   
    get_linkedin_profile_links()

    get_name_and_position_from_linkedin()

    get_founder_email()

    export_as_xlsx()

else:
    print "Angel list has not been scrapped"


    
    


    


    
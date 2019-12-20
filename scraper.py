# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

# import scraperwiki
# import lxml.html
#
# # Read in a page
# html = scraperwiki.scrape("http://foo.com")
#
# # Find something on the page using css selectors
# root = lxml.html.fromstring(html)
# root.cssselect("div[align='left']")
#
# # Write out to the sqlite database using scraperwiki library
# scraperwiki.sqlite.save(unique_keys=['name'], data={"name": "susan", "occupation": "software developer"})
#
# # An arbitrary query against the database
# scraperwiki.sql.select("* from data where 'name'='peter'")

# You don't have to do things with the ScraperWiki and lxml libraries.
# You can use whatever libraries you want: https://morph.io/documentation/python
# All that matters is that your final data is written to an SQLite database
# called "data.sqlite" in the current working directory which has at least a table
# called "data".

import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3

def item_scrapping(name):
	iter = 0
	items = pd.read_csv(name)
	url_number = 1
	total = len(items['url'])
	url = items['url']
	item_no = 0
	while item_no <= total-1:
		try:
			try:
				
				
				response = requests.get(url=url[item_no],timeout= 10)		
				soup = BeautifulSoup(response.text, 'html.parser')
				title           =   soup.find('span',{'id':"ctl00_PlaceHolderMain_pdTopControl_uc_ProductDetailsTitleControl_lab_Title"}).getText()
				VPN             =   str(soup.find('span',{'id':"ctl00_PlaceHolderMain_pdTopControl_uc_ProductDetailsVPNSummaryControl_lab_VPNValue"}).getText()).replace(":","").strip()
				Brand           =   soup.find('a',{'id':"ctl00_PlaceHolderMain_pdTopControl_uc_ProductDetailsTitleControl_lnk_VendorLink"}).getText()
				price           =   soup.find('span',{'id':"ctl00_PlaceHolderMain_pdTopControl_uc_PricingControl_rrpLabel"}).getText()
				category        =   soup.find('a',{'id':"ctl00_PlaceHolderMain_pdTopControl_uc_ProductDetailsTitleControl_lnk_CatSearch"}).getText()
				sub_category    =   soup.find('a',{'id':"ctl00_PlaceHolderMain_pdTopControl_uc_ProductDetailsTitleControl_lnk_SubCatSearch"}).getText()
				Description 	=	soup.find('span',{'id':"ctl00_PlaceHolderMain_pdTopControl_uc_ProductDetailsDescriptionControl_lab_AbridgedDescription"}).getText()
				SKU				=	str(url[item_no]).split("=")[1]
				UPC				=	str(soup.find('div',{'class':"info-codes-hidden hide"}).findAll('span')[3].getText())
				Packaging_info	=	soup.find('div',{'class':"packaging-data-parent"}).getText()

				Specs			= ""
				Warranty		= ""
				check = 0
				tables	=	soup.find('div',{'class':"extended pi"}).findAll('table')
				for tab in tables:
					text = tab.getText()

					if 'Basic' in text:
						Specs= ' '.join(str(text.replace('\n',' ').strip()).split())
						check += 1
					elif 'Limited Warranty' in text:
						Warranty = ' '.join(str(text.replace('\n',' ').strip()).split())
						check += 1
					if check >= 2:
						break
				

				if not Description:
					Description = str(soup.find('div',{'class',"product-summary-descr-new"}).find('div',{'id':"pnl_FullDescription"}).getText()).replace("\n"," ").replace("Read More","").replace(">","").strip()

				images_all = soup.find_all('a',{'id':"aProductImage"})
				try:
					images = [img.get('href') for img in images_all]
					image_urls = ', '.join(images)
				except:
					image_urls = ""

				product = soup.find_all('div',{'class':"adj-height"})
				try:
					related_product_VPN = [vpn.find('p',{'class':"vpn-num vpn_breakword"}).find('span').getText() for vpn in product]
					related_produts = ', '.join(related_product_VPN)
				except:
					related_produts = ""

				df = pd.DataFrame([[title,VPN,Brand,price,Description,image_urls,category,sub_category,related_produts,url[item_no],SKU,UPC,Warranty,Packaging_info,Specs]],columns=['Title','Procut_VPN','Brand','Price','Description','Images','Category','Sub_Category','Related_Products_VPN','URL','SKU','UPC','Warranty','Packaging_info','Specificaiton'])
				if iter == 0:
					df.to_csv('Scrapped_Data_'+str(name)+'.csv',index=False)
					
					iter = 1
				else:
					df.to_csv('Scrapped_Data_'+str(name)+'.csv', index=False,header=False,mode='a')

				item_no += 1
				url_number += 1
			except requests.ConnectionError:
				
				while True:
					try:
						requests.get('https://www.google.com/')
							
						break
					except requests.ConnectionError:
						continue

		except:
			
			item_no += 1
			url_number += 1

item_scrapping("files6.csv")
data = pd.read_csv('Scrapped_Data_files6.csv.csv')
conn = sqlite3.connect("data.sqlite")

conn.execute("CREATE TABLE if not exists data ('Title','Prodcut_VPN','Brand','Price','Description','Images','Category','Sub_Category','Related_Products_VPN','URL','UPC','Warranty','Packaging_info','Specificaiton')")

data.to_sql("data", conn, if_exists='replace', index=False)

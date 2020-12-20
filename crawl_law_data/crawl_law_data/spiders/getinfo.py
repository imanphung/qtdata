import os, random, sys, time
import scrapy
from ..items import CrawlLawDataItem
import json
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser
import pandas as pd

class getInfoSpider(scrapy.Spider):
	name = 'getinfo'
	allowed_domains = ['nhanlucnganhluat.vn']
	login_url = "https://nhanlucnganhluat.vn/tai-khoan/dang-nhap-tai-khoan.html?dangNhapCongTy=1&viewArea=ntd"
	cv_data = []

	def start_requests(self):
		yield scrapy.Request(self.login_url, callback=self.login)

	def login(self, response):
		url = 'https://nhanlucnganhluat.vn/Account/Account/DangNhapCongTy?Length=7'
		data = {
			'url': '',
			'UserName': 'info.qtdata@gmail.com',
			'Password': 'qttuyendung',
		}
		yield scrapy.FormRequest(url=url, formdata=data, callback=self.get_url)

	def get_url(self, response):
		file = open('./URL.txt')
		lines = file.readlines()
		for url in lines:
			yield scrapy.Request(url=url, callback=self.parse_pages)

	def parse_pages(self, response):
		for i in range(1,16):
			url = response.xpath("//div[@id='tdTimUngVienContent']/div[2]/div[{0}]/div/a/@href".format(i)).extract_first()
			yield scrapy.Request(url=url, callback=self.parse)

		next_button_url = response.xpath("//div[@id='tdTimUngVienContent']/div[3]/ul/li[last()]/a/@href").extract_first()
		print(next_button_url)
		if next_button_url is not None:
			yield scrapy.Request(url = next_button_url, callback=self.parse_pages)

	def parse(self, response):
		print(response.url)
		#item = CrawlLawDataItem()
		#open_in_browser(response)
		item = {
			'link' : response.url,
			'name' : response.xpath("//div[@id='thongTinCoBan']/div/div/h6/text()").extract_first().strip(),
			'email' : response.xpath("//div[@id='thongTinCoBan']/div[2]/div[4]/span/text()").extract_first().strip(),
			'phone_number' : response.xpath("//div[@id='thongTinCoBan']/div[2]/div[2]/span/text()").extract_first().strip(),
			'birth' : response.xpath("//div[@id='thongTinCoBan']/div[2]/div[1]/span/text()").extract_first().strip(),
			'major' : response.xpath("//div[@class='bg-white box-thong-tin-co-ban']/div/div[3]/div[2]/div[7]/a/text()").extract(),
			'salary' : response.xpath("//div[@class='bg-white box-thong-tin-co-ban']/div/div[3]/div[2]/div[6]/span/text()").extract_first(),
			'experience' : response.xpath("//div[@class='bg-white box-thong-tin-co-ban']/div/div[3]/div[2]/div/span/text()").extract_first(),
			'location' : response.xpath("//div[@id='thongTinCoBan']/div[2]/div[3]/span/span/text()").extract_first().strip(),
		}
		self.cv_data.append(item)
		x = pd.DataFrame(self.cv_data, columns=['location','name','experience','salary','major','link','email','phone_number','birth',])
		yield x.to_csv("CV_Crawl.csv",sep=",",index = False, encoding='utf-8-sig')
		
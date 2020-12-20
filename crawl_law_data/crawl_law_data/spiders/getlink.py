import scrapy
from ..items import CrawlLawDataItem

class getLinkSpider(scrapy.Spider):
	name = 'getlink'
	allowed_domains = ['nhanlucnganhluat.vn']
	start_urls = []
	for i in range(1, 50):
		start_urls.append('https://nhanlucnganhluat.vn/tim-ung-vien.html?MaLinhVucs=2&MaNoiLamViecs=256&trang=''{0}'.format(i))

	for i in range(1, 50):
		start_urls.append('https://nhanlucnganhluat.vn/tim-ung-vien.html?MaLinhVucs=2&MaNoiLamViecs=265&trang=''{0}'.format(i))

	for i in range(1, 260):
		start_urls.append('https://nhanlucnganhluat.vn/tim-ung-vien.html?MaLinhVucs=2&MaNoiLamViecs=255&trang=''{0}'.format(i))

	def parse(self, respone):
		item = CrawlLawDataItem()
		tmp_data = []
		data_resp = scrapy.Selector(respone)
		for i in range(1,16):
			tmp_url = data_resp.xpath("//div[@id='tdTimUngVienContent']/div[2]/div[{0}]/div/a/@href".format(i)).extract_first()
			tmp_data.append(tmp_url)
		item['per_link'] = tmp_data
		yield item
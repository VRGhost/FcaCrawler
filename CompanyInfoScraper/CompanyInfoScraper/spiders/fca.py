# -*- coding: utf-8 -*-
import re
import urlparse
import pprint

import scrapy
from ukpostcodeutils import validation as UkPostcodes

from .. import items

class FcaSpider(scrapy.Spider):
    name = "fca"
    allowed_domains = ["register.fca.org.uk"]
    start_urls = ['http://register.fca.org.uk/']

    searchTerm = None

    def __init__(self, regNumber, *args, **kwargs):
    	super(FcaSpider, self).__init__(*args, **kwargs)
    	self.searchTerm = regNumber
        print "SEARCH TERM > {!r} <".format(regNumber)

    def parse(self, response):
    	# Initial index.html parse leads here


    	formdata = {
        	"AJAXREQUEST": "_viewRoot",
        }

        # Add salesforce data
        for sales in response.xpath("//input[contains(@id, 'com.salesforce')]"):
        	name = sales.xpath("@name").extract_first()
        	value = sales.xpath("@value").extract_first()
        	assert name is not None and value is not None
        	formdata[name] = value

        moreDetailsInput = response.xpath("//input[contains(@id, 'moreDetails_HP')]/@id").extract_first()
       	assert moreDetailsInput
       	formdata[moreDetailsInput] = ""
        
    	# Locate the search form
    	form = response.xpath(
    		"//div[@class='RegisterSearchContainer']//form[contains(@name, 'registersearch')]")
        assert len(form) == 1, len(form)
        form = form[0]
        formName = form.xpath("@name").extract_first()
        formId = form.xpath("@id").extract_first()
        assert formId
        formdata.update({
        	formId: formId,
        	formId + ":searchBox": self.searchTerm,
        	formId + ":moreDetails_HP": "",
        	"searchBox": "",
        })

        # Locate the submit button
        button = response.xpath("//input[@type='submit' and contains(@id, 'registersearch') and not(contains(@class, 'advSearchBtn'))]")
        assert len(button) == 1, button.extract()
        buttonId = button.xpath("@id").extract_first()
        assert buttonId
        formdata[buttonId] = buttonId
               	
        print response.meta

        yield scrapy.FormRequest.from_response(response,
        	formname=formName,
        	formdata=formdata,
        	callback=self.parseSearchRedirict,
        )

    def parseSearchRedirict(self, response):
    	url = re.findall(r"/shpo_searchresults[A-Z0-9=?&]+", response.body, flags=re.I)
    	assert len(url) == 1

    	return scrapy.Request(
    		urlparse.urljoin(response.url, url[0]),
    		callback=self.parseSearchResults
    	)

    def parseSearchResults(self, response):
    	for tr in response.xpath(r"//div[@class='SearchResultsContainer']//tbody//tr"):
    		href = tr.xpath(".//td[@class='ResultName']/a/@href").extract_first()
    		companyType = tr.xpath("./td[3]/p/text()").extract_first()

    		if companyType.strip().lower() == "firm":
    			yield scrapy.Request(href, callback=self.parseFirmInfo)

    def parseFirmInfo(self, response):
    	data = {}

    	name = response.xpath("//h1[@class='RecordName']/text()").extract()
    	assert len(name) == 1
    	data["name"] = name[0].strip()

    	status = response.xpath("//span[@class='statusbox']/text()").extract()
    	assert len(status) == 1
    	data["status"] = status[0].strip()

    	# "Contact details" section
    	for section in response.xpath("//div[contains(@class, 'addresssection')]"):
    		subSections = section.xpath(".//div[contains(@class, 'addresssection')]")
    		if len(subSections) > 0:
    			continue # the crawler will recurse into subsections

    		label = section.xpath(".//span[@class='addresslabel']//text()").extract()
    		value = section.xpath(".//span[@class='addressvalue' or @class='addressline']//text()").extract()
    		assert label, (label, value)
    		label = (" ".join(label)).strip()
    		value = [el.strip() for el in value]

    		label = label.lower().strip().strip(":")
    		data[label] = "\n".join(value)

    	# "Basic details" section
    	for section in response.xpath("//div[contains(@id, 'FirmBasicDetails')]/div/span"):
    		titleEl = section.xpath(".//h4")
    		assert titleEl
    		title = titleEl.xpath("./text()").extract_first()
    		for valueSelector in [
    			"../p/b/text()",
    			"../p/span/text()",
    			"../p/text()",
    			"../text()",
    		]:
    			value = titleEl.xpath(valueSelector).extract()
    			if value:
    				break
    		if title and value:
    			data[title.lower().strip()] = (" ".join(value)).strip()

    	for line in data.get("address", "").splitlines():
    		line = line.strip()
    		checkLine = "".join(line.split()).upper()
    		if UkPostcodes.is_valid_postcode(checkLine):
    			data["postcode"] = line
    			break

    	return items.CompanyInfoItem(
    		name = data.get("name"),
		    address = data.get("address"),
		    postcode = data.get("postcode"),
		    phone = data.get("phone"),
		    email = data.get("email"),
		    website = data.get("website"),
		    houseNumber = data.get("companies house number"),
		    effectiveDate = data.get("effective date"),
		    status = data.get("status")
    	)


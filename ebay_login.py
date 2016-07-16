from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import random
import time

from ebay_credentials import credentials

keywords = [
    "cool",
    "banana",
    "underwear",
    "microcontroller",
    "sexy",     # if it costs one pound it won't actually be sexy, more likely hilarious or tragic
    "quote",
    "electronic",
    "calculator",
    "funny",
    "charming",     # Engrish!
    "cd",
    "crafts"
]

def ebay_search_url(searchtext, max_price = -1, free_shipping = False, buy_it_now = False):
    return "http://www.ebay.co.uk/sch/i.html?_nkw=" + searchtext +\
        ("&_udhi=%d" % max_price if max_price > 0 else "") +\
        ("&LH_FS=1" if free_shipping else "") +\
        ("&LH_BIN=1" if buy_it_now else "")

browser = webdriver.Firefox()
print("Navigating to eBay...")
browser.get("http://signin.ebay.co.uk")

print("Logging in...")
flds = browser.find_elements_by_class_name("fld")

assert(len(flds) >= 4)

un = flds[2]
pw = flds[3]

un.send_keys(credentials["username"])
pw.send_keys(credentials["password"])
pw.submit()
# Skip past any additional questions by simply navigating to main page
print("Searching...")
browser.get(ebay_search_url(random.choice(keywords), max_price = 1, free_shipping = True, buy_it_now = True))

print("Getting price list...")
prices = browser.find_elements_by_class_name("prc")
# Cull anything with a range of prices so that we don't accidentally buy something more expensive
print("Culling non-fixed prices...")
prices = [p for p in prices if p.text.find("to") == -1]

print("Attempting to click link...")
# Navigate to a random item
element = random.choice(prices)
# Navigate upward with xpath("..") until we find an element with a link, then click it.
while len(element.find_elements_by_tag_name("a")) < 1:
    element = element.find_element_by_xpath("..")
print("Chosen element with text \"%s\"..." % element.text)
element.find_element_by_tag_name("a").click()

print("Saving screenshot...")
#browser.save_screenshot(time.strftime("suggestions/suggestion_%d-%m-%Y_%H.%M.%S.png"))

# Select first item in all option dropdowns
dropdowns = browser.find_element_by_id("CenterPanel").find_elements_by_tag_name("select")
for d in dropdowns:
    d.click() # focus on dropdown
    d.send_keys(Keys.DOWN)

print("Clicking Buy it now...")
browser.find_element_by_id("binBtn_btn").click()
#browser.find_element_by_id("cta-btn").click()


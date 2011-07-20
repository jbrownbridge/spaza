from django.core.management.base import BaseCommand, CommandError

from BeautifulSoup import BeautifulSoup
import urllib2, re, json

from decimal import *

WHOLESALERS = {
  "Makro" : {
    "Groceries": {
      "Carbonated Soft Drinks" : "http://www.makro.co.za/live/content.php?SortBy=1&ItemsPerPage=9999&Region=1&Action=catalog&Cat=58&Gifts=&catId=&Start=0&Images=0&Query=&ShowAll=1&Brand=&Extended=&Reduced=&Promo=&Session_ID=f9850a12c1942df9c77866b3bbf22654",
      "Confectionary & Beverage" : {
        "Snack" : "http://www.makro.co.za/live/content.php?SortBy=1&ItemsPerPage=9999&Region=1&Action=catalog&Cat=82&Gifts=&catId=&Start=0&Images=0&Query=&ShowAll=&Brand=&Extended=&Reduced=&Promo=&Session_ID=f9850a12c1942df9c77866b3bbf22654",
        "Confectionery": "http://www.makro.co.za/live/content.php?SortBy=1&ItemsPerPage=9999&Region=1&Action=catalog&Cat=84&Gifts=&catId=&Start=0&Images=0&Query=&ShowAll=1&Brand=&Extended=&Reduced=&Promo=&Session_ID=f9850a12c1942df9c77866b3bbf22654",
      }
    }
  },
  "Woolworths" : {
    "Food & Household" : {
      "Beverages" : {
        "Carbonated Drinks" : {
          "Cans" : "http://www.woolworths.co.za/store/browse/category.jsp?q_docSort=&categoryId=cat420030&addFacet=9004%3Acat420030&howMany=99999&q_pageNum=1&viewAll=false",
        }
      },
      "Snacks, Sweets & Biscuits" : {
        "Chips & Other Snacks" : {
          "Chips / Crisps" : "http://www.woolworths.co.za/store/browse/category.jsp?q_docSort=&categoryId=cat420218&addFacet=9004%3Acat420218&howMany=99999&q_pageNum=1&viewAll=false",
          "Snack Bars": "http://www.woolworths.co.za/store/browse/category.jsp?q_docSort=&categoryId=cat420220&addFacet=9004%3Acat420220&howMany=99999&q_pageNum=1&viewAll=false",
        },
        "Chocolate Bars & Boxes" : {
          "Boxes" : "http://www.woolworths.co.za/store/browse/category.jsp?q_docSort=&categoryId=cat420226&addFacet=9004%3Acat420226&howMany=99999&q_pageNum=1&viewAll=false",
          "Chocolate Bars" : "http://www.woolworths.co.za/store/browse/category.jsp?q_docSort=&categoryId=cat420224&addFacet=9004%3Acat420224&howMany=99999&q_pageNum=1&viewAll=false",
        },
        "Dried Fruit" : "http://www.woolworths.co.za/store/browse/category.jsp?q_docSort=&categoryId=cat200032&addFacet=9004%3Acat200032&howMany=99999&q_pageNum=1&viewAll=false",
        "Nuts" : "http://www.woolworths.co.za/store/browse/category.jsp?q_docSort=&categoryId=cat200026&addFacet=9004%3Acat200026&howMany=99999&q_pageNum=1&viewAll=false",
        "Popcorn": "http://www.woolworths.co.za/store/browse/category.jsp?q_docSort=&categoryId=cat200024&addFacet=9004%3Acat200024&howMany=99999&q_pageNum=1&viewAll=false",
      },
    }
  }
}

class Command(BaseCommand):
  args = '<output_file>'
  help = 'This command generates a json file which will eventually turn into a fixture file for import into database'

  def __init__(self, *args, **kwargs):
    super(Command, self).__init__(*args, **kwargs)
    self.opener = urllib2.build_opener()
    self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]

  def parseMakroPage(self, url):
    soup = None
    import httplib
    while soup is None:
      # For some reason I kept getting IncompleteRead errors, this fixed it.
      try:
        page = self.opener.open(url)
        soup = BeautifulSoup(page.read())
        page.close()
      except (httplib.IncompleteRead, httplib.BadStatusLine), err:
        from time import sleep
        print "Read error occurred, sleeping for 1s then I will try again!"
        sleep(1)
    products = soup.findAll('table', attrs = { "background" : "/live/images/product_back.gif"})
    suffix = "http://www.makro.co.za"
    data = []
    for product in products:
      try:
        brand = product.find(attrs={'class' : 'style4'}).contents[0]
        # At least one product data entry is broken
        if len(brand) > 0:
          brand = brand.contents[0].strip()
        else:
          brand = ""
        variation = product.find(attrs={'class' : 'style4'}).contents[1].strip()
        sku = str(Decimal(product.find(attrs={"class" : "style20"})['href'].split('Sku=')[1].split('|')[0]))
        product_id = product.find(attrs={"class" : "style20"})['href'].split('ProdId=')[1].split('&')[0]
        link = "%s/%s" % (suffix, product.find(attrs={'class' : 'style4'})['href'].split('&')[0][1:])
        price = product.find(attrs={'class' : 'style5'}).contents[0].strip().split(' ')[1].strip()
      except IndexError:
        import pdb
        pdb.set_trace()
      price = str(Decimal(price).quantize(Decimal('.01'), rounding=ROUND_DOWN))
      print "%s [%s]:%s - %s R %s (%s)" % (product_id, sku, brand, variation, price, link) 
      data.append({
        'brand' : brand,
        'variation' : variation,
        'sku' : sku,
        'product_id' : product_id,
        'link' : link,
        'price' : price,
      })
    return data
      
  def parseWoolworthsPage(self, url):
    page = self.opener.open(url)
    soup = BeautifulSoup(page.read())
    page.close()
    products = soup.findAll('div', attrs = { "class" : "itemcontainerWW" })
    suffix = "http://www.woolworths.co.za"
    data = []
    for product in products:
      name = product.find(attrs = { "class" : "itemheader" }).a.contents[0].strip()
      link = "%s/%s" % (suffix, product.find(attrs = { "class" : "itemheader" }).a['href'][1:])
      product_id = link.split('=')[1]
      price = product.find(attrs = { "class" : "itemprice_strike" }).contents[0].strip().split(' ')[1].strip()
      price = str(Decimal(price).quantize(Decimal('.01'), rounding=ROUND_DOWN))
      print "%s: %s R %s (%s)" % (product_id, name, price, link) 
      data.append({
        'name' : name,
        'link' : link,
        'product_id' : product_id,
        'price' : price,
      })
    return data

  def recurseWholesalers(self, obj, parse_callback, categories=[], products = []):
    if isinstance(obj, dict):
      for k in obj.keys():
        new_categories = list(categories)
        new_categories.append(k)
        self.recurseWholesalers(obj[k], parse_callback, new_categories, products)
    else:
      newProducts = parse_callback(obj)
      for product in newProducts:
        product['categories'] = categories
      products.extend(newProducts)

  def handle(self, *args, **options):
    if len(args) == 1:
      woolworthsProducts = []
      makroProducts = []
      self.recurseWholesalers(WHOLESALERS['Woolworths'], self.parseWoolworthsPage, [], woolworthsProducts)
      self.recurseWholesalers(WHOLESALERS['Makro'], self.parseMakroPage, [], makroProducts)
      products = {
        'Woolworths': woolworthsProducts,
        'Makro': makroProducts,
      }
      filename = args[0]
      with open(filename, mode='w') as f: 
        json.dump(products, f, indent=2)
    else:
      print "You need to specify the output filename"

      

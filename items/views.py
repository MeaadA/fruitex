from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template import Context, loader
from items.models import Store, Item
import json
from category import category

TAX_RATE = 0.13

labels = {
  'Produce': 'cate_label_produce.png',
  'Home & Lifestyle': 'cate_label_home.png',
  'Groceries': 'cate_label_grocery.png', 
  'Snacks & Candies': 'cate_label_candy.png',
  'Beverages':'cate_label_beverage.png',
  'Pet Care':'cate_label_pet.png',
}


def itemlist(request):
    template = loader.get_template('itemlist.html')
    context = Context({
      'category' : json.dumps(category),
      'labels' : json.dumps(labels)
      })
    return HttpResponse(template.render(context))

def toStructuredItem(it):
  return {'name' : it.name, 'price' : it.price, 'category' : it.category, 
      'store' : it.store.id, 'id' : it.id, 'tax_class' : it.tax_class, 'sku' : it.sku} 

import re
def extractCate(query):
  patterns = ["cate:'([^']*)'", "cate:([^ ]*)",]
  cate = []
  r = query
  for p in patterns:
    cate.extend(re.findall(p, r))
    r = re.sub(p, '', r)
  return cate, r

def getItemsByRange(query, startId, num):
  cates,keyword = extractCate(query)
  if len(cates) > 0:
    cate = cates[0]
  else:
    cate = ''
  keyword = re.sub(r'^\s*|\s*$', '', keyword)
  return map(toStructuredItem, 
      Item.objects.all().filter(name__icontains=keyword)
      .filter(category__icontains=cate)[startId : startId + num])

def getItemsByIds(ids):
  return map(toStructuredItem, Item.objects.filter(id__in = ids))

def computeTax(item):
  if item['tax_class'] == 'zero-rate':
    return 0
  elif item['tax_class'] == 'standard-rate':
    return TAX_RATE * item['price']

def computeDelivery(item):
  return 4.0

import urllib2
@csrf_exempt
def getItems(request):
  if request.method == 'POST':
    if 'startId' in request.POST:
      query = request.POST['query']
      query = urllib2.unquote(query.encode("utf8"))
      print query
      startId = int(request.POST['startId'])
      num = int(request.POST['num'])
      return HttpResponse(json.dumps(getItemsByRange(query, startId, num)))
    elif 'ids' in request.POST:
      ids = json.loads(request.POST['ids'])
      return HttpResponse(json.dumps(getItemsByIds(ids)))
    else:
      return HttpResponse('error')
  else:
    return HttpResponse('error')

@csrf_exempt
def computeSummary(request):
  if request.method == 'POST':
    ids = json.loads(request.POST['ids'])
    items = getItemsByIds(ids)
    d = computeDelivery(items)
    s = 0.0
    t = 0.0
    for item in items:
      ct = ids.count(item['id'])
      s += item['price'] * ct
      t += computeTax(item) * ct
    res = {'sum' : s, 'tax' : t, 'delivery' : d, 'total' : s + t + d}
    return HttpResponse(json.dumps(res))
  else:
    return HttpResponse('error')
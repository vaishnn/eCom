import requests

response = requests.get("https://www.reliancedigital.in/ext/raven-api/catalog/v1.0/products", params={
    'page_id':1,
    'page_size':100,
    'q':'iPhone 16 256 GB'
})
data = response.json()
items = data.get('items', [])
for item in items:
    if item.get('type', 'Unknown') == 'product':
        product_details = item.get('_custom_json', {})
        name = product_details.get('name', 'Unknown')
        type = product_details.get('type', 'Unknown')
        mrp = product_details.get('mrp', 'Unknown')
        offer_price = product_details.get('offer_price', 'Unknown')
        print(f"Name: {name}, Type: {type}, MRP: {mrp}, Offer Price: {offer_price}")

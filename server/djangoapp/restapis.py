import requests
import json
from .models import CarDealer, DealerReview, CarModel, CarMake
from requests.auth import HTTPBasicAuth
import datetime

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url,**kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
    # Call get method of requests library with URL and parameters
        if "api_key" in kwargs:
            api_key= kwargs["api_key"]
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except Error as val:
        # If any error occurs
        print("Network exception occurred", val)

        
    status_code = response.status_code
    if status_code!=200:
        print("Server Error")
    print("With status {}".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, payload, **kwargs):
    print("POST Request from ", url)
    # try:
    response = requests.post(url, params=kwargs, json=payload)
# except:
    # If any error occurs
    print("Network exception occurred")
    status_code = response.status_code
    print("With status {}".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(**kwargs):
    results = []
    url = "https://7a6d4448.us-south.apigw.appdomain.cloud/api/dealership"
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if "dealerships" in json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["dealerships"]
        # For each dealer object
        for dealer in dealers:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"], state=dealer["state"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_by_state_from_cf(url, state_code):
# - Call get_request() with specified arguments 
    # query = {'state':state_code}
    url = 'https://7a6d4448.us-south.apigw.appdomain.cloud/api/dealership'
    json_response = get_request(url, state=state_code)

    results = []
# - Parse JSON results into a DealerView object list
    if json_response:
        dealers = json_response["dealerships"]
        # For each dealer object
        for dealer in dealers:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"], state=dealer["state"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)

    return results 

def get_dealer_reviews_from_cf(dealerId):
    url = 'https://7a6d4448.us-south.apigw.appdomain.cloud/api/review'
    json_response = get_request(url,dealerId=dealerId)
    results = []
    if "reviews" in json_response:
        reviews = json_response["reviews"]
        for review in reviews:
            review_object = DealerReview(dealership=review["dealership"],name = review["name"],
            purchase = review["purchase"], review = review["review"], purchase_date = review["purchase_date"],
            car_make = review["car_make"], car_model = review["car_model"],car_year=review["car_year"],
            id = review["id"])
            carmake = CarMake.objects.get_or_create(name = review["car_make"], description = review["car_make"])[0]
            car = CarModel.objects.create(dealerId=dealerId,name=review['car_model'],make=carmake, year=datetime.date(int(review["car_year"]),1,1), Type="Sedan")
            sentiment = analyze_review_sentiments(review_object.review)
            if "error" in sentiment:
                review_object.sentiment = "neutral"
            else:
                review_object.sentiment=sentiment["sentiment"]["document"]["label"]
            results.append(review_object)
    else: 
        return 500
    return results

        

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    version = '2021-03-25'
    features = {"sentiment" }
    return_analyzed_text =True
    url = ''
    api_key = ''
    response = get_request(url, text = text, version=version, features = features, return_analyzed_text = return_analyzed_text, api_key=api_key)
    return response
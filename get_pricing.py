'''
Find total cost of running aws instances. 
Output should include:
1. EC2 instance IDs 
2. EC2 Instance type
3. Dockerize this code 
4. Put this in a repo and share with us
'''

import json
import requests
import boto3
import datetime
import os

PRICING_URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json"
PRICING_FILE = "pricing.json"
MAC_CACHE_AGE = 10

LOCATION = "US West (Oregon)" # Can change this to relevant location

def is_pricing_stale():
  # The pricing file is >1GB so it may not need to be downloaded every day.
  # If stale, return True, otherwise return False
  
  last_mod = os.path.getmtime(PRICING_FILE)
  curr_time = datetime.now()
  time_diff = curr_time - last_mod
  
  if time_diff.days > MAX_CACHE_AGE:
    return True
  return False

def update_pricing():
  response = requests.get(PRICING_URL)
  data = response.json()
  
  with open(PRICING_FILE, 'w') as f:
    json.dump(data, f)

def get_pricing(instance_types):
  if is_pricing_stale():
    update_pricing()
  
  # Pricing data is structured as described here:
  # https://aws.amazon.com/blogs/aws/new-aws-price-list-api/
  
  # Map instance type to price and sku
  price_info = {}
    
  with open(PRICING_FILE, 'r') as f:
    data = json.load(f)
    
    for product in data['products']:
      instance = product['attributes']['instanceType']
      location = product['attributes']['location']
      if instance in instance_types and location == LOCATION:
        price_info[instance] = {}
        price_info[instance]['sku'] = product['sku']
        instance_types.remove(instance)
  
    for k, v in price_info.items():
      sku = v['sku']
      price_info[k]['price'] = product['pricing'][sku]['priceDimensions']['pricePerUnit']['USD']
      
   # We could add logic to cache price_info as well
   return price_info
  
def get_instances():
  curr_time = datetime.now()
  
  instance_types = set() # List of instance types we need to get pricing for
  
  curr_instances = {} # Mapping of InstanceID: {'type': <type>, uptime: <uptime>}
  
  client = boto3.client('ec2')
  
  # Response format shown here:
  # https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instances.html
  response = client.describe_instances()
  
  for reservation in response['Reservations']:
    for instance in reservation['Instances']:
      i_id = instance['InstanceId']
      curr_instances[i_id] = {}
      curr_instances[i_id]['type'] = instance['InstanceType']
      instance_types.add(instance['InstanceType'])
      
      # Calculate how long this has been up in the last day
      
      # Time is formatted like "2018-05-10T08:05:20.000Z"
      launch_time_str = curr_instances[i_id]['LaunchTime'].split('.')[0] + '+0000' # Format date to a parseable value
      
      launch_time = datetime.strptime(launch_time_str, "%Y-%m-%dT%H:%M:%S%z")
      uptime = curr_time - launch_time
      # Convert uptime to hours, and measure at most 24 hours in the past day.
      uptime = max(24, uptime.seconds / 3600.0)
      curr_instances[i_id]['uptime'] = uptime    
  
  return curr_instances, instance_types
  
def calculate_costs(instances, pricing_info):
  for i_id, data in instances.items():
    i_type = data['type']
    instances[i_id]['cost'] = pricing_info[i_type]['price'] * instances[i_id]['uptime']
     
  return instances

def output_data(instances):
  # This can be adjusted to write to a DB or output as needed.
  print(str(instances))

if __name__ == "__main__":
  instances, instance_types = get_instances()
  pricing_info = get_pricing(instance_types)
  instances = calculate_costs(instances, pricing_info)
  output_data(instances)

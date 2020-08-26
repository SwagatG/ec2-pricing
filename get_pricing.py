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
import subprocess

PRICING = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json"

INSTANCES_COMMAND = "aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId]' --filters Name=instance-state-name,Values=running --output text".split(' ')

def get_pricing():
  # TODO
  
  pass
  
def get_instances():
  subprocess.run(INSTANCES_COMMAND, , stdout=subprocess.PIPE).stdout.decode('utf-8')
  
  

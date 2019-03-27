#Facebook custom audience load api by Joel Sacco
#for documentation see here - https://developers.facebook.com/docs/marketing-api/audiences-api
#Warning - I'm not a programmer. This code is probably gross to read but it's the best I could do
#you can get the python sdk here https://github.com/facebook/facebook-python-ads-sdk
#On linux - save facebookads folder to usr/local/lib/python2.7/dist-packages
#On Windows - I just saved the facebookads folder to the c:/python27 folder where my scripts lived
#---
#run by doing "python *thisfilename*.py for windows. 

#additional changes

from facebookads.api import FacebookAdsApi
from facebookads.adobjects.adaccountuser import AdAccountUser
from facebookads.adobjects.adaccount import AdAccount
from facebookads.adobjects.customaudience import CustomAudience
from facebookads.adobjects import campaign
import argparse
import csv
import hashlib

#take in the arguments from the command
#when you execute the command it should be like the following:
#python scriptname.py audname "auddesc" filename.csv
#ex - python fb_audiencetest.py name_of_audience "here is a description of the audience" test.csv
parser = argparse.ArgumentParser()
parser.add_argument("audname", help="what you wish to name your audience")
parser.add_argument("auddesc", help="brief description of this audience")
parser.add_argument("filename", help="file name of raw data csv. Must be csv file")
args = parser.parse_args()

audname = args.audname
auddesc = args.auddesc
filename = args.filename

#Initialize a new Session and instantiate an Api object
#You will need a facebook account for your organization. go to developers.facebook.com
#there's a box on the top right that says my apps. Click there and make your first app. 
#follow the steps here https://developers.facebook.com/docs/marketing-apis 
#under "Creating an App with Marketing API"

my_app_id = 'APPIDGOESHERE'
my_app_secret = 'APPSECRETGOESHERE'
my_access_token = 'APPTOKENGOESHERE' 
#this particular access token expires and will need to be replaced
#follow these instructions for an updated token under obtain access token
#https://developers.facebook.com/docs/marketing-api/quickstart
#https://developers.facebook.com/docs/marketing-api/audiences-api for more help

FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)

me = AdAccountUser(fbid='me')
my_account = me.get_ad_accounts()[0]

#the below line should return your ad account info
print 'my account id is' ;
print  my_account.get_id_assured();
print"";

#below creates a new blank custom audience using the parameters defined above
audience = CustomAudience(parent_id= my_account.get_id_assured())
audience[CustomAudience.Field.subtype] = CustomAudience.Subtype.custom
audience[CustomAudience.Field.name] = audname
audience[CustomAudience.Field.description] = auddesc

audience.remote_create()
caid = audience[CustomAudience.Field.id]
print 'my new custom audience id is:';
print  caid;
print""

#send records to audience.
audience = CustomAudience(caid)
#below line is for testing records. Userz is actual code for loading csv. 
#users = ['test1@example.com', 'test2@example.com', 'test3@example.com']
userz = []
with open(filename, 'rb') as f:
    reader = csv.reader(f)

    for row in reader:
        userz.append(row[0].lower().replace(" ",""))

audadd = audience.add_users(schema=CustomAudience.Schema.email_hash, users=userz, pre_hashed=False)
#this line will hash the data and add it to the custom audience. 


#below should print all custom audiences in the specified account id. 
#should show your new audience in there as well with approximate record count and audience ID
print "all custom audineces with this account";
ad_account = AdAccount(my_account.get_id_assured())
custom_audiences = ad_account.get_custom_audiences(fields=[
    CustomAudience.Field.name, CustomAudience.Field.id, CustomAudience.Field.approximate_count
])
for custom_audience in custom_audiences:
    print(custom_audience[CustomAudience.Field.name],custom_audience[CustomAudience.Field.id],custom_audience[CustomAudience.Field.approximate_count])
print "";

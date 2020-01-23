#Facebook Custom Audience Middleware App by Joel Sacco
#For API version 3.3 Q4 2019 and Python 3.7
#updated to version 4.0 1/21/2020
#update 1/22 - prompt for share id 

#basic import things for how I want the script to work
import argparse #parses argments passed with script execution
import csv #allows script to read csv files
import hashlib #adds sha256 hashing functionality
import datetime #adds date functionality
import shutil #adds ability to move files
import os #adds ability to do os things
import requests #adds ability to do HTTP requests (needed for sharing)

#for the below you need to install the facebook sdk
#with python easiest way to do this is via PIP
#CD to your python directory run "python37 pip -m facebook_business" from your command line
#you can also just download the sdk from the github - https://github.com/facebook/facebook-python-business-sdk
	#note - will need to import sys to reference libraries on disk. Not sure how to do this. 
#additional documentation  - https://developers.facebook.com/docs/business-sdk/getting-started
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adaccountuser import AdAccountUser
from facebook_business.adobjects.customaudience import CustomAudience
from facebook_business.api import FacebookAdsApi


#0 - gets ad accounts for sharing. Will be utilized later. 
shareid = input('Enter your sharing account ID: \n')

#confirming
print ('audience will be shared with ' + shareid);


#TO RUN THIS SCRIPT YOU RUN THE FOLLOWING:
#python37.exe fb_custaud2.py 


#1 - this section effectively "logs in"

'''
BEFORE YOU MAKE THIS SECTION YOU MUST COMPLETE THE FOLLOWING
- get access to the business manager - business.facebook.com
- create an ad account / acquire your ad account ID which will be hosting the custom audiences
- create a new app at developers.facebook.com
- pair app to a business manager (required to use custom audience functionality) - in advanced app settings

At this point you can start development but in order to move to production you will need to fill out everything in the basic settings and submit the app for review. 
Corrdinate with the Social and Legal teams on this. 

'''

#things needed to instantiate the session
#get this at https://developers.facebook.com/tools/explorer/
#you want a user access token
#You can create a long lived token that will last 3 months. otherwise will only last 30 minutes
access_token = ''


#below are just in the fb app settings
#to find the app_secret, look in your app settings under "basic"
app_secret = ''

#to find the app_id, look in your app settings under "basic"
app_id = ''

#below is the ad account ID that you will be pushing the audiences in to
#get this by logging in to business.facebook.com. 
#Ad accounts should be in the middle of the page. 
#click on the ad account to copy it to the clipboard. 
#audience id must be in the format "act_YOURACCOUNTIDHERE"
my_account = '' 

#The below code  effectively logs in using the info above
FacebookAdsApi.init(app_id, app_secret, access_token)

maindir = os.getcwd()
sourcedir = maindir + '/SOURCE'
filelist = (os.listdir(sourcedir))
movedir = maindir + '/ARCHIVE'
apipath = maindir + '/SOURCE/'
filecount = 0
totalrecords = 0

print ('Lets get started');
print ('Source Directory: ' + sourcedir);
print ('Archive Directory: ' + movedir);
for index, filenamez in enumerate(filelist):
	#if os.path.splitext(filename)[-1].lower() == '.csv':
	#3 - create a blank custom audience
	filename = str(filenamez)
	print ('filename is ' + filename);
	audience = CustomAudience(parent_id=my_account)
	audience[CustomAudience.Field.subtype] = CustomAudience.Subtype.custom
	audience[CustomAudience.Field.name] = filename[:-4]
	audience[CustomAudience.Field.description] = filename[:-4]
	audience[CustomAudience.Field.customer_file_source] = 'USER_PROVIDED_ONLY' 
	
	#the below command actually creates the custom audience
	audience.remote_create()
	#remote_create is being depricated soon. Will need to migrate to 
	#AdAccount(api=self._api, fbid=parent_id).create_custom_audience(fields, params, batch, success, failure, pending)
	#not sure how to use this yet. 
	
	caid = audience[CustomAudience.Field.id]
	print ('my new custom audience id is: ' + caid);

	#4 - add records to the blank custom audience
	# will push with a pid and will use multi key matching. 
	#update - Facebook confirmed "is_raw = True" will automatically hash data.  
	schema = [
		CustomAudience.Schema.MultiKeySchema.extern_id, #send your external id here
		CustomAudience.Schema.MultiKeySchema.fn,
		CustomAudience.Schema.MultiKeySchema.ln,
		CustomAudience.Schema.MultiKeySchema.ct,
		CustomAudience.Schema.MultiKeySchema.st,
		CustomAudience.Schema.MultiKeySchema.zip,
		CustomAudience.Schema.MultiKeySchema.email,
		CustomAudience.Schema.MultiKeySchema.email,
		CustomAudience.Schema.MultiKeySchema.email,
		CustomAudience.Schema.MultiKeySchema.phone,
		CustomAudience.Schema.MultiKeySchema.phone,
		CustomAudience.Schema.MultiKeySchema.country
	]
	
	starttime = datetime.datetime.now()
	counter = 0
	processedrows = 0
	totalrow = 0
	userz = []
	contactfile = apipath+filename
	
	with open(contactfile, 'r') as zz:
		prereader = csv.reader(zz)
		filerowz = sum(1 for row in prereader)
	
	with open(contactfile, 'r') as openfile:
		print('Start time: ' + str(starttime))
		reader = csv.reader(openfile)
		for row in reader:
			userz.append(row)
			counter += 1
			processedrows +=1
			totalrow += 1
			
			if counter == 10000:
				audience.add_users(schema, userz, is_raw=True, pre_hashed=False)
				print(str(totalrow) + ' Records added successfully')
				counter = 0
				userz = []
				
			elif counter > 0 and counter < 10000 and processedrows == filerowz:
				audience.add_users(schema, userz, is_raw=True, pre_hashed=False)
				print(str(totalrow) + ' Records added successfully')
				counter = 0
				userz = [] 
				
	print('Upload complete. Added ' + str(totalrow) + ' records.')
	endtime = datetime.datetime.now()
	print('End time: ' + str(endtime))

	shutil.move(apipath+filename, movedir+'/'+filename)
	filecount = filecount + 1
	totalrecords = totalrecords + totalrow
	
	#share the file with the requested account id
	#need to handle exceptions here and make code dynamically accept 0 or more audiences to share with. 
	
	sharing_account_id = shareid
	relationship_type = 'Audience Info Provider'
	
	print('Sharing audience ' + caid + ' with other account ' + sharing_account_id )
	
	url = f"https://graph.facebook.com/v4.0/" + caid + "/adaccounts"
	querystring = {"adaccounts":sharing_account_id,"relationship_type":relationship_type,"access_token":access_token}
	response = requests.request("POST", url, params=querystring)
	print(response.text)
	
	print("Audience has been shared!")
	
	#below is the lookalike code for later...
	#need to handle gracefully if not enough records
	#maybe also output which lals were skipped due to insufficient records in the concluding statement
	
	#lookalike = CustomAudience(parent_id=my_account)
	#lookalike.update({
	#	CustomAudience.Field.name: filename[:-4] + '_lookalike',
	#	CustomAudience.Field.subtype: CustomAudience.Subtype.lookalike,
	#	CustomAudience.Field.origin_audience_id: caid,
	#	CustomAudience.Field.lookalike_spec: {
	#			'type': 'similarity',
	#			'ratio': 0.05,
	#			'country': 'US',
	#		},
	#})
	
	#lookalike.remote_create()
	#laid = lookalike[CustomAudience.Field.id]
	#print ('my new lookalike audience id is: ' + laid);
	#print(lookalike)
	
	
print('ALL uploads complete. Added ' + str(totalrecords) + ' records across ' + str(filecount) + ' files shared to ' + str(shareid) +'.')




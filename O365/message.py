from O365 import Attachment
import logging
import json
import requests

logging.basicConfig(filename='o365.log',level=logging.DEBUG)

log = logging.getLogger(__name__)

class Message( object ):
	att_url = 'https://outlook.office365.com/api/v1.0/me/messages/{0}/attachments'
	send_url = 'https://outlook.office365.com/api/v1.0/me/sendmail'
	update_url = 'https://outlook.office365.com/api/v1.0/me/messages/{0}'

	def __init__(self, json=None, auth=None):
		'''
		Wraps all the informaiton for receiving messages.
		'''
		if json:
			self.json = json
			self.hasAttachments = json['HasAttachments']

		else:
			self.json = {}
			self.hasAttachments = False
	
		self.auth = auth
		self.attachments = []
		self.reciever = None

#		if json:
#			log.debug('translating message information into local variables.')
#			self.messageId = json['Id']
#			self.sender = json['Sender']['EmailAddress']['Name']
#			self.address = json['Sender']['EmailAddress']['Address']
#			self.subject = json['Subject']
#			self.body = json['Body']['Content']


	def fetchAttachments(self):
		if not self.hasAttachments:
			log.debug('message has no attachments, skipping out early.')
			return False

		response = requests.get(self.att_url.format(self.json['Id']),auth=self.auth)
		log.info('response from O365 for retriving message attachments: %s',str(response))
		json = response.json()

		for att in json['value']:
#			try:
			self.attachments.append(Attachment(att))
#				log.debug('successfully downloaded attachment for: %s.',self.auth[0])
#			except Exception as e:
#				log.info('failed to download attachment for: %s', self.auth[0])

		return len(self.attachments)

	def sendMessage(self):
		if not self.receiver:
			return False

		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		message = {}
		message['Subject'] = self.subject
		message['Body'] = {'ContentType':'Text','Content':self.body}
		message['ToRecipients'] = [{'EmailAddress':{'Address':self.receiver}}]

		dat = {'Message':message,'SaveToSentItems':'true'}

		data = json.dumps(dat)
#		data = json.dumps(self.json)
		print data

		response = requests.post(self.send_url,data,headers=headers,auth=self.auth)
		print response

		return True
		
	def markAsRead(self):
		read = '{"IsRead":true}'
		headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
#		try:
		response = requests.patch(self.update_url.format(self.json['Id']),read,headers=headers,auth=self.auth)
#		except:
#			return False
		print response
		return True


	def getSender(self):
		return self.json['Sender']

	def getSenderEmail(self):
		return self.json['Sender']['EmailAddress']['Address']
	
	def getSenderName(self):
		return self.json['Sender']['EmailAddress']['Name']

	def getSubject(self):
		return self.json['Subject']

	def getBody(self):
		return self.json['Body']['Content']

	def setRecipients(self,val):
		if isinstance(val,list):
			self.json['ToRecipients'] = val
		elif isinstances(val,dict):
			self.json['ToRecipients'] = [val]
		elif isinstance(val,string):
			if '@' in val:
				self.json['ToRecipients'] = []
				self.addRecipient(None,val)
		else:
			return False
		return True

	def addRecipient(self,name,address):
		self.json['ToRecipients'].append({'EmailAddress':{'Address':address,'Name':name}})

	def setSubject(self,val):
		self.json['Subject']

	def setBody(self,val):
		self.json['Body']['Content']

#To the King!
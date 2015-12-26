#! /usr/bin/env python

# fix path for submodules
import sys
sys.path.insert(1, 'imgurpython/')
sys.path.insert(2, 'requests/')

import time

from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError

# get API-keys from config
from config import client_id, client_secret

client = ImgurClient(client_id, client_secret)

authorization_url = client.get_auth_url('pin')

print "Please visit %s to get the access pin for your account"%authorization_url

pin = raw_input("Pin: ")

credentials = client.authorize(pin, 'pin')
client.set_user_auth(credentials['access_token'], credentials['refresh_token'])

user = raw_input("Enter username to upvote: ")

total_comments = client.get_account_comment_count(user)
comment_pages=total_comments/50

print "Trying to upvote %s comments with following limits: %s"%(total_comments, client.credits)

comments=list()
comments_full = comments

for Z in range(0,comment_pages+1):
	comments.extend(client.get_account_comment_ids(user, page=Z))

co_d=dict()

lengths=(len(comments), len(co_d))
while comments:
	print "Comments to process: %s. Credits: %s"%(str(lengths), str(client.credits))
	if client.credits['UserRemaining'] != None and len(comments) > int(client.credits['UserRemaining']):
		print "Breaking due to limits: %s"%str(client.credits)
		break
	for idx,comment in enumerate(comments):
		try:
			if not co_d.has_key(comment):
				co_d[comment] = client.get_comment(comment)
			if co_d[comment].vote != u'up':
				client.comment_vote(comment, vote='up')
				print "Upvoted comment id: %s, idx: %s"%(comment, idx)
			else:
				print "Comment already upvoted id: %s, idx: %s"%(comment, idx)
			comments.remove(comment)
		except ImgurClientError as error:
			time.sleep(0.5)
			print "Request failed for comment id: %s, idx: %s"%(comment, idx)
		except TypeError as te:
			print "Creating comment-object failed for comment id: %s, idx: %s"%(comment, idx)
	new_lengths=(len(comments), len(co_d))
	if new_lengths == lengths:
		break
	else:
		lengths = new_lengths
print client.credits

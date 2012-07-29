#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dbus, sys, os
from subprocess import call
from subprocess import check_output

def main():
	sessionBus = dbus.SessionBus()

	# Check if Skype is running
	systemServiceList = sessionBus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus').ListNames()
	skypeApiFound = 0

	for service in systemServiceList:
		if service == 'com.Skype.API':
			skypeApiFound = 1
			break

	if not skypeApiFound:
		#sys.exit('Skype with DBus support running not found.')
		os.spawnl(os.P_NOWAIT, '/usr/bin/skype')

	skypeService = sessionBus.get_object('com.Skype.API', '/com/Skype')
	answer = skypeService.Invoke('Name SkypeApiClient')

	if answer != 'OK':
		sys.exit('Could not bind to Skype client.')

	answer = skypeService.Invoke('PROTOCOL 8')

	if answer != 'PROTOCOL 8':
		sys.exit('This test program only supports Skype API protocol version 1.')	
	
	i = 0

	for arg in sys.argv:
		if arg == 'manualMode':
			while True:
				cmd = raw_input('Введите команду: ')

				if cmd == '' or cmd == '^[':
					break

				result = skypeService.Invoke(cmd.upper())
				print result + "\n"

		if arg == 'hangUpAll':
			result = skypeService.Invoke('SEARCH ACTIVECALLS')

			if result[0:6] == 'CALLS ':
				for id in result[6:].split(' '):
					skypeService.Invoke('SET CALL ' + str(id) + ' STATUS FINISHED')
		elif arg == 'pickUp':
			result = skypeService.Invoke('SEARCH ACTIVECALLS')

			if result[0:6] == 'CALLS ':
				for id in result[6:].split(' '):
					skypeService.Invoke('ALTER CALL ' + str(id) + ' ANSWER')
		elif arg == 'firstMissedChat':
			result = skypeService.Invoke('SEARCH MISSEDCHATS')
			missedChats = ''

			if result[0:6] == 'CHATS ':
				missedChats = result[6:].split(', ')

			if len(missedChats) and len(missedChats[0]):
				skypeService.Invoke('OPEN CHAT ' + str(missedChats[0]))
		elif arg == 'recentChat':
			result = skypeService.Invoke('SEARCH RECENTCHATS')

			if result[0:6] == 'CHATS ':
				recentChats = result[6:].split(', ')

				if len(recentChats) and len(recentChats[0]):
					skypeService.Invoke('OPEN CHAT ' + str(recentChats[0]))
		elif arg == 'showContacts':
			try:
				username = sys.argv[i+1]
			except IndexError:
				print('Skype username is not defined.')
				return 1

			focusedWindowId = check_output('xdotool getwindowfocus', shell=True)
			result = skypeService.Invoke('GET WINDOWSTATE')

			if result != 'WINDOWSTATE NORMAL':
				skypeService.Invoke('SET WINDOWSTATE NORMAL')

			contactsWindowId = check_output('xdotool search --name "' + str(username) + ' - Skype."', shell=True)

			if focusedWindowId == contactsWindowId:
				skypeService.Invoke('SET WINDOWSTATE HIDDEN')
			else:
				call('xdotool search --name "khaimovmr - Skype." windowactivate', shell=True)
		else:
			skypeService.Invoke(arg)

		i += 1

if __name__ == '__main__':
	main()
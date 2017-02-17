# -*- coding: utf-8 -*-
import requests
import time
import json

token = ''
app_id = ''
loop_rate = 120
loop_times = loop_rate

#获取应用状态
def get_status(token, api_url, app_id):
	app_state = 'unknown'
	response = requests.get(api_url + app_id, headers = {'Authorization' : token})
	if response.status_code == 200:
		content = response.json()
		app_state = content['state']

	global loop_times, loop_rate
	if loop_times >= loop_rate:
		log('app %s is %s' % (app_id, app_state))
		loop_times = 0
	loop_times = loop_times + 1

	return app_state

#唤醒应用
def wakeup_app(token, api_url, app_id):
	action_id = 'unknown'
	response = requests.post(api_url + app_id + '/actions/start', headers = {'Authorization' : token})
	if response.status_code == 200:
		content = response.json()
		action_id = content['action_id']

	log('wake up app %s' % (app_id))

	return action_id

#获取事件状态
def get_action_state(token, api_url, app_id, action_id):
	action_state = 'unknown'
	response = requests.get(api_url + app_id + '/actions/' + action_id, headers = {'Authorization' : token})
	if response.status_code == 200:
		content = response.json()
		action_state = content['state']

	log('action %s %s' % (action_id, action_state))

	return action_state

#开始监控
def start_watch():
	headers = {'Authorization' : token}
	api_url = 'https://openapi.daocloud.io/v1/apps/'

	app_state = get_status(token, api_url, app_id)
	if app_state == 'stopped':
		action_id = wakeup_app(token, api_url, app_id)
		if action_id != 'unknown':
			action_success = False
			while action_success == False:
				action_state = get_action_state(token, api_url, app_id, action_id)
				if action_state != 'in_process':
					action_success = True
				else:
					time.sleep(15)
	time.sleep(1)
	start_watch()

# 读取配置文件
def load_config():
	config_file = open('config.json')
	config = json.load(config_file)
	return config

# 输出日志
def log(content):
	time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	print time_str, ':', content

if __name__ == "__main__":
	log('read config file')
	config = load_config()
	token = config['token']
	app_id = config['appid']
	log('token is %s' % (token))
	log('app id is %s' % (app_id))
	start_watch()
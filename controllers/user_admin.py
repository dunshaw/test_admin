#coding:utf-8
import os,time
import os.path
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
import datetime
import urllib
import hashlib
import ConfigParser
from flask import Flask,url_for,request,session,make_response
from mysql.database import HANDLE
from mysql.dbhelper import DBHelper
from mysql.database import DB
from mysql.tables.paic_admin import ad_users,task_data,phone_brand,phone_model
from werkzeug.security import generate_password_hash, check_password_hash
from common.encrypt_helper import *


def nowtime():
	return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class UsersAdmin():

	def __init__(self):
		get_cf = ConfigParser.ConfigParser()
		cf_path = os.path.split(os.path.realpath(__file__))[0] + '/config'
		# cf_path = os.path.dirname(os.path.abspath(__file__)) + '\config.ini'
		get_cf.read(cf_path)
		# print cf_path
		self.path=get_cf.get("database","datapath")


	def pwd_encrypt(self,pwd):
		# 对密码进行加密
		return generate_password_hash(pwd, method='pbkdf2:sha1:1000', salt_length=24)


	def check_ecrypt_pwd(self,en_pwd, pwd):
		# 判断加密后的密码和加密前的密码是否相同  en_pwd:加密后的密码   pwd：加密前的密码
		return check_password_hash(en_pwd, pwd)


	def get_session(self,name):
		# print name
		return DBHelper(ad_users).get_by(ad_user_name=name).ad_user_token

	def check_token(self,name,token):
		print name,token
		if self.get_session(name) == token:
			return True
		else:
			self.login_out()
			return False

	def judge_user(self,request):
		user = request.form.get('logUser')
		pwd = request.form.get('logPwd')
		print pwd,user

		# _adusers = ad_users.handle()
		# sql = 'SELECT * FROM paic_admin.ad_users where ad_user_name = "{0}"'.format(user)
		# result = HANDLE('paic_admin', sql).submit()
		# if result:
		# 	if pwd ==result.ad_user_password:
		# 		return {'data':result.ad_user_family}
		# 	else:
		# 		return {'data':'密码错误，请重新输入密码！'}
		# else:
		# 	return {'data':'此账号不存在，请注册后登录!'}
			
			

		if DBHelper(ad_users).get_by(ad_user_name=user):
			data = DBHelper(ad_users).get_by(ad_user_name=user)
			if data.ad_user_try ==5:
				if self.unlocktime(data.ad_user_time):
					return self.jg_password(data,user,pwd)
				else:
					return {'data':'您的账号被锁定1小时，请于 {0} 后再尝试登录!'.format(data.ad_user_time),'status':201}
			else:
				return self.jg_password(data,user,pwd)
		else:
			return {'data':'此账号不存在，请注册后登录!','status':202}

	def unlocktime(self,datatime):
		print datatime,nowtime()
		if datatime < nowtime():
			DBHelper(ad_users).set({'ad_user_time':nowtime(),'ad_user_try':0},dict(ad_user_name=user))
			return True
		else:
			return False

	def jg_password(self,data,user,pwd):
		if self.check_ecrypt_pwd(data.ad_user_password,pwd):
				session_id = Encrypt_Helper().makeSessionId(user)
				DBHelper(ad_users).set({"ad_user_token":session_id,'ad_user_time':nowtime(),'ad_user_try':0},dict(ad_user_name=user))
				self.set_session(user,session_id,data.ad_user_family)
				return {'data':data.ad_user_family,'status':200,'username':user}
		else:
			if data.ad_user_try < 4:
				DBHelper(ad_users).set({'ad_user_time':nowtime(),'ad_user_try':data.ad_user_try+1},dict(ad_user_name=user))
				return {'data':'密码错误，请重新输入密码,您还有{0}次尝试的机会,5次错误账号将锁定1小时!'.format(4-data.ad_user_try),'status':201}
			elif data.ad_user_try == 4:
				unlocktime = datetime.datetime.now()+datetime.timedelta(hours=1)
				DBHelper(ad_users).set({'ad_user_time':unlocktime.strftime("%Y-%m-%d %H:%M:%S"),'ad_user_try':data.ad_user_try+1},dict(ad_user_name=user))
				return {'data':'您的账号将锁定1小时，请于 {0} 后再尝试登录!'.format(unlocktime.strftime("%Y-%m-%d %H:%M:%S")),'status':201}


	def set_session(self,username,sessions,family):
		if family == 0:
			session['userform'] = 'admin'
		else:
			session['userform'] = 'user'
		session['username'] = username
		session[username] = sessions
		return

	def login_out(self):
		name = session.pop('username')
		session.pop('userform')
		session.pop(name)
		DBHelper(ad_users).set({"ad_user_token":''},dict(ad_user_name=name))
		return 

	def account_ver(self,user,pwd,comeform):
		if user not in DBHelper(ad_users).find_col_by('ad_user_name'):
			safepwd = self.pwd_encrypt(pwd)
			DBHelper(ad_users).new(ad_user_name=user,ad_user_password=safepwd,ad_user_family=comeform)
			return {'status':200,'msg':''}
		else:
			return {'msg':'账号已存在，请登录或联系管理员.','status':101}


	def send_register_info(self,request):
		user = request.form.get('logUser')
		pwd = request.form.get('logPwd')

		if user=='admin':
			msg = self.account_ver(user,pwd,0)
		else:
			msg = self.account_ver(user,pwd,1)

		return msg

# 修改密码
	def send_repair_info(self,request):
		user = request.form.get('logUser')
		oldpwd = request.form.get('oldPwd')
		newpwd = request.form.get('newPwd')

		# print user,oldpwd,newpwd
		if DBHelper(ad_users).get_by(ad_user_name=user):
			data = DBHelper(ad_users).get_by(ad_user_name=user)
			if self.check_ecrypt_pwd(data.ad_user_password,oldpwd):
				DBHelper(ad_users).set({'ad_user_password':self.pwd_encrypt(newpwd)}, {'ad_user_name':user})
				return {'msg':'密码修改成功!','status':200}
			else:
				return {'msg':'原密码错误，请输入正确的原密码!','status':202}
		else:
			return {'msg':'此账号错误，请稍后再试或联系服务人员!','status':201}




	# 第一次上传文件处理
	def upload_tast_data(self,request):
		try:
			taskname = request.form['taskname']
			models = request.form['modellist'].split(',')
			# print models
			Apx_filename = request.form['file_APK']
			Excel_filename = request.form['file_Excel']
			user = request.form['username']
			remarks = request.form['taskremarks']

			# print Apx_filename,type(Excel_filename)
			ApkFile = False
			ExcelFile = False
			if str(Apx_filename) !='0':
				ApkFile = request.files['fileAPK']
				
			if str(Excel_filename) !='0':
				ExcelFile = request.files['fileTest']
			upload_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			


			apk_result = excel_result = ''
			# 处理APK文件
			if ApkFile:
				apk_result = self.apk_file_save(ApkFile,Apx_filename)

			# 处理Excel文件
			if ExcelFile:
				excel_result = self.excel_file_save(ExcelFile,Excel_filename)

			# 存入数据
			self.uploaddata_save(apk_result,excel_result,taskname,models,user,remarks)
			
			return {"status":200,"message":"上传成功"}
		except Exception,e:
			return {"status":101,"message":"上传失败,失败原因:{0}".format(e)}


	# apk保存
	def apk_file_save(self,file,filename):
		upload_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
		newname = "{0}({1}).{2}".format(filename.split('.')[0],upload_time,filename.split('.')[1])
		# path = u'F:/PingAn_Technolog/November_2018/test_admin/static/files/Apk-files/{0}'.format(newname)
		path = os.path.join(self.path,'Apk-files/{0}'.format(newname))
		file.save(unicode(path,'utf-8'))
		# file.save(path)
		return newname


	# 用例文件保存
	def excel_file_save(self,file,filename):
		upload_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
		newname = "{0}({1}).{2}".format(filename.split('.')[0],upload_time,filename.split('.')[1])
		# path = u'F:/PingAn_Technolog/November_2018/test_admin/static/files/TestCase-files/{0}'.format(newname)
		path = os.path.join(self.path,'TestCase-files/{0}'.format(newname))
		# file.save(path)
		file.save(unicode(path,'utf-8'))
		return newname


	#   储存数据库-记录
	def uploaddata_save(self,apk_result,excel_result,taskname,models,user,remarks):
		uploadtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		# print '-------------'
		userid = DBHelper(ad_users).get_by(ad_user_name=user).id

		DBHelper(task_data).new(user_id=userid,task_name=taskname,apk_data='{0}'.format(apk_result),case_data='{0}'.format(excel_result),
			task_models=','.join(models),task_remarks=remarks,upload_time=uploadtime)





	#   查看用户数据
	def ckeck_user_reports(self,request):
		user = request.args.get('logUser')
		# print user

		data = []
		# 数据库获取数据

		downloadpath= u'/static/files/'

		userid = DBHelper(ad_users).get_by(ad_user_name=user).id
		datas = DBHelper(task_data).find_by(user_id=userid)

		for item in datas:
			itemtime = item.upload_time.split(' ')[0]
			itemreport = item.task_report
			itemJournal  = item.task_journal
			if itemreport and itemJournal:
				result = True
				reportpath = downloadpath+'Report-files/'+itemreport
				journalpath = downloadpath+'Journal-files/'+itemJournal
			else:
				result = False
				reportpath = ''
				journalpath = ''
			data.append({'Number':item.id,'Taskname':item.task_name,'Uploadtime':itemtime,'Result':result,'Reportpath':reportpath,'Journalpath':journalpath})

		return {"data":data}

		

	# 更新文件
	def update_test_data(self,request):
		try:
			taskNumber = request.form['task_Numb']
			Apx_filename = request.form['file_APK']
			Excel_filename = request.form['file_Excel']
			# print Apx_filename,Excel_filename
			ApkFile = False
			ExcelFile = False
			if str(Apx_filename) !='0':
				ApkFile = request.files['update_APKfile']
			if str(Excel_filename) !='0':
				ExcelFile = request.files['update_Casefile']
			upload_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

			# print ApkFile,ExcelFile

			# 获取数据并且覆盖删除原文件
			# self.delete_user_data
			
			# 处理APK文件
			if ApkFile:
				apk_result = self.apk_file_save(ApkFile,Apx_filename)
				self.delete_user_data(taskNumber,'apk')
				self.updata_save(taskNumber,apk_result,upload_time,'apk')

			# 处理Excel文件
			if ExcelFile:
				excel_result = self.excel_file_save(ExcelFile,Excel_filename)
				self.delete_user_data(taskNumber,'case')
				self.updata_save(taskNumber,excel_result,upload_time,'case')

			# 更新数据库数据
			# self.updata_save
			
			return {"status":200,"message":"上传成功"}
		except Exception,e:
			return {"status":101,"message":"上传失败,失败原因:{0}".format(e)}


	def delete_user_data(self,Number,style):
		# 通过任务ID获取信息并且操作
		task = DBHelper(task_data).get_by(id=Number)
		if style == 'apk':
			if task.apk_data:
				self.delete_apk_data('Apk-files',task.apk_data)
		elif style == 'case':
			if task.case_data:
				self.delete_apk_data('TestCase-files',task.case_data)



	def delete_apk_data(self,file,filename):
		path = os.path.join(self.path,'{0}/{1}'.format(file,filename))
		# path = u'F:/PingAn_Technolog/November_2018/test_admin/static/files/{0}/{1}'.format(file,filename)
		os.remove(unicode(path,'utf-8'))



	# 更新数据
	def updata_save(self,Number,filename,Times,style):
		if style =='apk':
			DBHelper(task_data).set({'apk_data':filename,'upload_time':Times}, {'id':Number})
		elif style == 'case':
			DBHelper(task_data).set({'case_data':filename,'upload_time':Times}, {'id':Number})



	# 获取手机品牌和型号
	def get_phone_brand(self):
		brands=[]
		for item in DBHelper(phone_brand).find_by(remark=u'1'):
			models = self.get_brand_model(item.id)
			brands.append({"id":item.id,'name':item.brand_name,'name_ch':item.brand_name_ch,'model_total':models})

		return {'data':brands}

	def get_brand_model(self,brandid):
		# print brandid
		_phonemd = phone_model.handle()
		sql = 'SELECT * FROM paic_admin.phone_model where phone_brand_id = "{0}"'.format(brandid)
		result = HANDLE('paic_admin', sql).submit()
		model = []
		for item in result:
			# tuple只能用数组方式[0]获取
			# imgpath = self.fixpath(item[8])
			model.append({'modelid':item[0],'modelname':item[2],'screen':item[4],'resolving':item[5],'cpu':item[6],"system":item[7],'image':str(item[8])})
		return model

	# def fixpath(self,imgname):
	# 	basic_path = u'F:/PingAn_Technolog/test_admin/static/phones'
	# 	filepath = url_for('static',filename='phones/'+str(imgname))
	# 	return filepath


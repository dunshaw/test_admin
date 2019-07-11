#coding:utf-8
import os,time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
import datetime
import urllib
import ConfigParser
from mysql.database import HANDLE
from mysql.dbhelper import DBHelper
from mysql.database import DB
from mysql.tables.paic_admin import ad_users,task_data,phone_brand,phone_model





class AdminController():

	def __init__(self):
		get_cf = ConfigParser.ConfigParser()
		cf_path = os.path.split(os.path.realpath(__file__))[0] + '/config'
		get_cf.read(cf_path)
		# print cf_path
		self.path=get_cf.get("database","datapath")


	def get_admin_check(self,request):
		user = request.args.get('logUser')

		APK_files=u'/static/files/Apk-files/'
		Test_files = u'/static/files/TestCase-files/'

		datas = DBHelper(task_data).all()

		data = []

		if user=='admin':
			for item in datas:
				apkpath = testpath = False
				if item.apk_data:
					apkpath = APK_files+item.apk_data
				if item.case_data:
					testpath = Test_files+item.case_data
				timeshare = item.upload_time.split(' ')[0]
				report = False
				journal= False
				Remarks = False
				if item.task_remarks and item.task_remarks != ' ':
					Remarks = True
				if item.task_report:
					report = True
				if item.task_journal:
					journal = True
				data.append({'Number':item.id,'Taskname':item.task_name,'Uploadtime':timeshare,'APK':apkpath,'TestCase':testpath,'Report':report,'remarks':Remarks,'Journal':journal})	

		return {'data':data}



	def admin_check_msg(self,request):
		Number = request.args.get('id')
		data = DBHelper(task_data).get_by(id=Number).task_remarks
		return {'data':data}


	def admin_check_phone(self,request):
		Number = request.args.get('id')
		data = []
		for item in DBHelper(task_data).get_by(id=Number).task_models.split(','):
			print int(item)
			model = DBHelper(phone_model).get_by(id=int(item)).phone_model_name_ch
			data.append(model)
		return {'data':data}



	def admin_upload_report(self,request):
		try:
			taskNumb = request.form['tast_numb']
			file = request.files['adminfile']
			fileName = request.form['file_name']
			tasktype = request.form['task_type']
			# print tasktype
			upload_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
			newname = "{0}({1}).{2}".format(fileName.split('.')[0],upload_time,fileName.split('.')[-1])
			if int(tasktype) == 0:
				paths = os.path.join(self.path,'Report-files/{0}'.format(newname))
			else:
				paths = os.path.join(self.path,'Journal-files/{0}'.format(newname))
			
			

			file.save(unicode(paths,'utf-8'))
			# 存入数据
			self.reportdata_save(taskNumb,newname,tasktype)
			
			return {"status":200,"message":"上传成功"}
		except Exception,e:
			return {"status":101,"message":"上传失败,失败原因:{0}".format(e)}


	def reportdata_save(self,taskNumb,filename,tasktype):
		data = DBHelper(task_data).get_by(id=taskNumb)
		if int(tasktype) == 0:
			if data.task_report:
				# print data.task_report
				self.delete_report_data(data.task_report,'Report-files')
			DBHelper(task_data).set({'task_report':filename},{'id':taskNumb})
		else:
			if data.task_journal:
				self.delete_report_data(data.task_journal,'Journal-files')
			DBHelper(task_data).set({'task_journal':filename},{'id':taskNumb})

	def delete_report_data(self,file,pathname):
		path = os.path.join(self.path,'{0}/{1}'.format(pathname,file))
		os.remove(unicode(path,'utf-8'))
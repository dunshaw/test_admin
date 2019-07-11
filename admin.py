#coding:utf-8
'''
Created on 2018-11-29

@author:SuMo_

'''

from flask import Flask,abort,request,session,render_template,request,send_from_directory,json,jsonify,redirect,url_for,make_response
from common.utils import *
import os.path

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'

@app.errorhandler(404)
def page_not_found(error):
	return render_template('./new_index.html',response = "登录超时或过期!"),404


@app.before_request
def process_request():
    # print '================================='
    name = session.get('username')
    form = session.get('userform')
    token = session.get(name)
    print name,token
    if name and token:
      if request.path =='/':
        if form =='user':
          return render_template('./user/user_page.html',username=name)
        else:
          return render_template('./admin/admin_page.html',username=name)
      else:
        if UsersAdmin().check_token(name,token):
          return None
        else:
          abort(404)
    # print request.cookies.get(name)
    # print request.path
    # print str(request.headers).rstrip()
    # print '================================='


@app.route("/")
def index():
	return render_template('./new_index.html')

@app.route("/log_out")
def log_out():
	UsersAdmin().login_out()
	return redirect(url_for('login_page'))

@app.route("/login_page")
def login_page():
	return render_template('./ci/login_page.html')


@app.route("/courses_page",methods=['Post'])
def courses_page():
	return render_template('./ci/courses_page.html',username=session.get('username'),userform=session.get('userform'))

# @app.route("/courses_pages_admin/<string:name>",methods=['Post'])
# def courses_pages_admin(name):
# 	return render_template('./ci/courses_page.html',username=name,userform='admin')

# @app.route("/courses_pages/<string:name>",methods=['Post'])
# def courses_pages(name):
# 	return render_template('./ci/courses_page.html',username=name,userform='user')

# @app.route("/pricing_pages_admin/<string:name>",methods=['Post'])
# def pricing_pages_admin(name):
# 	return render_template('./ci/prices_page.html',username=name,userform='admin')

# @app.route("/pricing_pages/<string:name>",methods=['Post'])
# def pricing_pages(name):
# 	return render_template('./ci/prices_page.html',username=name,userform='user')

@app.route("/pricing_page",methods=['Post'])
def pricing_page():
	return render_template('./ci/prices_page.html',username=session.get('username'),userform=session.get('userform'))

# @app.route("/contact_page_admin/<string:name>",methods=['Post'])
# def contact_page_admin(name):
# 	return render_template('./ci/contact_page.html',username=name,userform='admin')

# @app.route("/contact_pages/<string:name>",methods=['Post'])
# def contact_pages(name):
# 	return render_template('./ci/contact_page.html',username=name,userform='user')

@app.route("/contact_page",methods=['Post'])
def contact_page():
	return render_template('./ci/contact_page.html',username=session.get('username'),userform=session.get('userform'))
	

#---------------------------------------------------------------------------------------#
#                                                                                       #
#                           admin_user                                                  #
#                                                                                       #
#---------------------------------------------------------------------------------------#
from controllers.user_admin import UsersAdmin
from controllers.admin_controller import AdminController
from datetime import timedelta

@app.route("/send_login_info",methods=['Post'])
def send_login_info():
  session.permanent = True
  app.permanent_session_lifetime = timedelta(minutes=60) 
  return jsonify(UsersAdmin().judge_user(request))


@app.route("/send_register_info",methods=['Post'])
def send_register_info():
	return jsonify(UsersAdmin().send_register_info(request))


@app.route("/admin_page",methods=['Post'])
def admin_page():
	return render_template('./admin/admin_page.html',username=session.get('username'))


@app.route("/admin_operation",methods=['Post'])
def admin_operation():
	return render_template('./admin/admin_page_operation.html',username=session.get('username'))


@app.route("/user_page",methods=['Post'])
def user_page():
	return render_template('./user/user_page.html',username=session.get('username'))

@app.route("/upload_operation",methods=['Post'])
def upload_operation():
	return render_template('./user/user_page_upload.html',username=session.get('username'))


@app.route("/upload_tast_data",methods=['Post'])
def upload_tast_data():
	return jsonify(UsersAdmin().upload_tast_data(request))


@app.route("/check_operation",methods=['Post'])
def check_operation():
	return render_template('./user/user_page_check.html',username=session.get('username'))

@app.route("/repair_count",methods=['Post'])
def repair_count():
	name = request.args.get("name")
	return render_template('./ci/repair_count.html',username=session.get('username'))

@app.route("/send_repair_info",methods=['Post'])
def send_repair_info():
	return jsonify(UsersAdmin().send_repair_info(request))


@app.route("/update_test_data",methods=['Post'])
def update_test_data():
	return jsonify(UsersAdmin().update_test_data(request))


@app.route("/ckeck_user_reports",methods=['get'])
def ckeck_user_reports():
	return jsonify(UsersAdmin().ckeck_user_reports(request))

@app.route("/get_phone_brand",methods=['get'])
def get_phone_brand():
	return jsonify(UsersAdmin().get_phone_brand())


@app.route("/get_admin_check",methods=['get'])
def get_admin_check():
	return jsonify(AdminController().get_admin_check(request))


@app.route("/admin_upload_report",methods=['Post'])
def admin_upload_report():
	return jsonify(AdminController().admin_upload_report(request))


@app.route("/admin_check_msg",methods=['get'])
def admin_check_msg():
	return jsonify(AdminController().admin_check_msg(request))

@app.route("/admin_check_phone",methods=['get'])
def admin_check_phone():
	return jsonify(AdminController().admin_check_phone(request))










def main():
	app.run(
		'11.240.99.70',
		9002,
		# get_host_info()[0],
		# 9002,
		threaded = True,
		debug = True
		)

if __name__ == '__main__':
	main()

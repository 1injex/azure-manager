import threading
from flask import Flask, render_template, request, url_for, redirect, flash, make_response
import function

app = Flask(__name__)
app.jinja_env.filters['zip'] = zip
# 请将 xxx 替换为随机字符
app.config['SECRET_KEY'] = 'c2jf932hibfiuebvwievubheriuvberv'


@app.route('/')
def index():
    # 获取cookie账号信息
    account = request.cookies.get('account')
    return render_template('index.html', account=account)


@app.route('/account/add', methods=['GET', 'POST'])
def accountadd():
    if request.method == 'POST':  # 判断是否是 POST 请求
        # 获取表单数据
        account = request.form.get('account')
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')
        tenant_id = request.form.get('tenant_id')
        subscription_id = request.form.get('subscription_id')
        # 验证数据
        if not account or not client_id or not client_secret or not tenant_id or not subscription_id:
            flash('输入错误')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        # 保存表单数据到cookie
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('account', account)
        resp.set_cookie('client_id', client_id)
        resp.set_cookie('client_secret', client_secret)
        resp.set_cookie('tenant_id', tenant_id)
        resp.set_cookie('subscription_id', subscription_id)
        flash('添加管理账户成功')
        return resp
    account = request.cookies.get('account')
    return render_template('account.html', account=account)


@app.route('/account/delete')
def accountdel():
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie('account')
    resp.delete_cookie('client_id')
    resp.delete_cookie('client_secret')
    resp.delete_cookie('tenant_id')
    resp.delete_cookie('subscription_id')
    flash('删除账户成功')
    return resp


@app.route('/account/list')
def list():
    account = request.cookies.get('account')
    client_id = request.cookies.get('client_id')
    client_secret = request.cookies.get('client_secret')
    tenant_id = request.cookies.get('tenant_id')
    subscription_id = request.cookies.get('subscription_id')
    credential = function.create_credential_object(tenant_id, client_id, client_secret)
    dict = function.list(subscription_id, credential)
    return render_template('list.html', dict=dict, account=account)


@app.route('/account/vm/create', methods=['GET', 'POST'])
def create_vm():
    if request.method == 'POST':
        client_id = request.cookies.get('client_id')
        client_secret = request.cookies.get('client_secret')
        tenant_id = request.cookies.get('tenant_id')
        subscription_id = request.cookies.get('subscription_id')
        credential = function.create_credential_object(tenant_id, client_id, client_secret)
        tag = request.form.get('tag')
        location = request.form.get('location')
        size = request.form.get('size')
        os = request.form.get('os')
        set = request.form.get('set')
        ## 此处为VM默认登陆密码
        username = "defaultuser"
        password = "Thisisyour.password1"
        for i in range(int(set)):
            name = (tag + str(i + 1))
            function.create_resource_group(subscription_id, credential, name, location)
            threading.Thread(target=function.create_or_update_vm, args=(
            subscription_id, credential, name, location, username, password, size, os)).start()
        flash('创建中，请耐心等待VM创建完成，大约需要1-3分钟')
    account = request.cookies.get('account')
    return render_template('vm.html', account=account)


@app.route('/account/vm/delete/<string:tag>')
def delete_vm(tag):
    client_id = request.cookies.get('client_id')
    client_secret = request.cookies.get('client_secret')
    tenant_id = request.cookies.get('tenant_id')
    subscription_id = request.cookies.get('subscription_id')
    credential = function.create_credential_object(tenant_id, client_id, client_secret)
    threading.Thread(target=function.delete_vm, args=(subscription_id, credential, tag)).start()
    flash("删除中，请耐心等待1-3分钟")
    return redirect(url_for('list'))


@app.route('/account/vm/start/<string:tag>')
def start_vm(tag):
    client_id = request.cookies.get('client_id')
    client_secret = request.cookies.get('client_secret')
    tenant_id = request.cookies.get('tenant_id')
    subscription_id = request.cookies.get('subscription_id')
    credential = function.create_credential_object(tenant_id, client_id, client_secret)
    threading.Thread(target=function.start_vm, args=(subscription_id, credential, tag)).start()
    flash("开机中，请耐心等待1-3分钟")
    return redirect(url_for('list'))


@app.route('/account/vm/stop/<string:tag>')
def stop_vm(tag):
    client_id = request.cookies.get('client_id')
    client_secret = request.cookies.get('client_secret')
    tenant_id = request.cookies.get('tenant_id')
    subscription_id = request.cookies.get('subscription_id')
    credential = function.create_credential_object(tenant_id, client_id, client_secret)
    threading.Thread(target=function.stop_vm, args=(subscription_id, credential, tag)).start()
    flash("关机中，请耐心等待1-3分钟")
    return redirect(url_for('list'))


@app.route('/account/vm/changeip/<string:tag>')
def changeip_vm(tag):
    client_id = request.cookies.get('client_id')
    client_secret = request.cookies.get('client_secret')
    tenant_id = request.cookies.get('tenant_id')
    subscription_id = request.cookies.get('subscription_id')
    credential = function.create_credential_object(tenant_id, client_id, client_secret)
    try:
        threading.Thread(target=function.change_ip, args=(subscription_id, credential, tag)).start()
        flash("更换IP进行中，请耐心等待1-3分钟")
        return redirect(url_for('index'))
    except:
        flash("出现未知错误，请重试")


if __name__ == '__main__':
    app.run(port=8888, host='0.0.0.0')

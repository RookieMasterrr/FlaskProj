import datetime
from flask import Blueprint,request,current_app
from flask.json import jsonify
from .dbm import db,userTable,followTable,chatTable
import os
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .func import localURL, return_msgjson,return_userjson,return_videojson,paginate
from sqlalchemy import and_,or_

bp = Blueprint('users_module', __name__)
projectPath=os.path.dirname(__file__)

@bp.route('/hello')
def hello():
    return "HelloFromUsers"

@bp.route('/action/register',methods=["POST"])
def user_register():
    # 判断请求是否正确
    if (not 'userName' in request.form.keys()) or (not 'userEmail' in request.form.keys()) or (not 'userPassword' in request.form.keys()):
        return jsonify(data='',code=1,note='表单中未填写userName或userEmail或userPassword')


    # 判断是否重复用户
    thisUser=userTable.query.filter_by(userEmail=request.form.get('userEmail')).first()
    if (thisUser!=None):
        return jsonify(data='',code=1,note='邮箱已被使用')

        # 判断是否为空表
    if userTable.query.first()==None:
        lastUserId=0
    else:
        lastUserId=userTable.query.order_by(userTable.userId.desc()).first().userId
    userId=lastUserId+1

    
    # 获取头像
    avatarFile=request.files.get('avatarFile')
    if (avatarFile==None):
        avatarURL=(os.path.join(localURL,'static','avatars','0.jpg'))
    else:
        avatarURL=saveFileAndReturnURL(file=avatarFile,id=userId,subpath='avatars')

    userId=userId
    userPassword = request.form.get('userPassword')
    userName = request.form.get('userName')

    

    userVideosNum = 0
    userTweetsNum = 0
    userSelfDescribe = "该用户很懒，什么也没有留下"
    userAvatarPath = avatarURL
    userFollowNumber = 0
    userFansNumber = 0
    userEmail = request.form.get('userEmail')
    userRegisterDate = datetime.datetime.now()
    userState = 0
    userRank = 0

    # 构造记录
    newUser = userTable(userId=userId,userPassword=userPassword ,userName=userName ,userVideosNum=userVideosNum ,userTweetsNum=userTweetsNum ,userSelfDescribe=userSelfDescribe ,
    userAvatarPath=userAvatarPath,userFollowNumber=userFollowNumber ,userFansNumber=userFansNumber ,
    userEmail=userEmail ,userRegisterDate=userRegisterDate ,userState=userState ,userRank=userRank )
    # 插入数据库
    db.session.add(newUser)
    db.session.commit()

    user_json=return_userjson(newUser)
    # 构造响应
    return jsonify(data={'user':user_json},code=200)

@bp.route('/action/login',methods=['POST'])
def user_login():
    if (not 'userEmail' in request.form.keys()) or (not 'userPassword' in request.form.keys()):
        return jsonify(data='',code=1,note='表单中未填写userEmail或userPassword')

    userEmail = request.form.get('userEmail')
    userPassword = request.form.get('userPassword')
    user=userTable.query.filter_by(userEmail=userEmail).first()
    if (user==None):
        return "no this user"
    if(user.userPassword==userPassword):
        token = get_token(userEmail,userPassword)
        user_json=return_userjson(user)
        return jsonify(data={'user':user_json,'token':token},code=200,note="")
    else:
        return "password error"

@bp.route('/action/follow/<int:vlogerId>',methods=['POST'])
def user_follow(vlogerId):

    # 先判断有没有这个用户存在
    vlogerIfExist=userTable.query.get(vlogerId)
    if(vlogerIfExist==None):
        return jsonify(data='',code=1,note='关注目标不存在')


    token=request.headers.get('token')
    token_result = judge_token(token)
    if token_result == False:
        return jsonify(data='',code=1,note='登录令牌错误')
    
    userEmail=token_result['userEmail']

    fan=userTable.query.filter_by(userEmail=userEmail).first()
    vloger=userTable.query.get(vlogerId)




    thisUserFollowList=followTable.query.filter_by(fanId=fan.userId).all()
    for followItem in thisUserFollowList:
        if(followItem.vlogerId==vloger.userId):
            db.session.delete(followItem)

            vloger.userFansNumber-=1
            fan.userFollowNumber-=1 

            db.session.commit()
            # "cancle collect"
            fan_json=return_userjson(fan)
            vloger_json=return_userjson(vloger)
            return jsonify(data={'fan':fan_json,'vloger':vloger_json,'record':None},code=200,note='')


    aFollowRequest=followTable(fanId=fan.userId,fanName=fan.userName,vlogerId=vloger.userId,vlogerName=vloger.userName,followDate=datetime.datetime.now())
    db.session.add(aFollowRequest)

    vloger.userFansNumber+=1
    fan.userFollowNumber+=1 

    db.session.commit()

    fan_json=return_userjson(fan)
    vloger_json=return_userjson(vloger)

    record={'fanId':aFollowRequest.fanId,'fanName':aFollowRequest.fanName,'vlogerId':aFollowRequest.vlogerId,
    'vlogerName':aFollowRequest.vlogerName,'followDate':aFollowRequest.followDate}
    return jsonify(data={'fan':fan_json,'vloger':vloger_json,'record':record},code=200,note='')

@bp.route('/action/search/orderbyFansNum',methods=["GET"])
def f_u_search_l():
    query=request.args.get('query')
    desc=request.args.get('desc',1)

    if(not 'query' in request.args.keys()) or query=='':
        return jsonify(data='',code=1,note='url中需要有query参数并且需要有值')

    result=userTable.query.whooshee_search(query).all()
    if(desc=='1'):
        # 降序
        result.sort(key=lambda item:item.userFansNumber,reverse=True)
    else:
        # 升序
        result.sort(key=lambda item:item.userFansNumber,reverse=False)

    data_list=[]
    for user in result:
        user_json=return_userjson(user)
        data_list.append({'user':user_json})


    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=data_list,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)







@bp.route('/action/sendMsg',methods=["POST"])
def f_sendMsg():
    '''
    私信函数
    '''
    token=request.headers.get('token')
    token_result = judge_token(token)
    if token_result == False:
        return jsonify(data='',code=1,note='登录令牌错误')
    
    userEmail=token_result['userEmail']
    
    From=userTable.query.filter_by(userEmail=userEmail).first()
    To=userTable.query.get((int)(request.form.get('userId')))
    if(To==None):
        return jsonify(data='',code=1,note='私信对象不存在')

    if (From==To):
        return jsonify(data='',code=1,note='不允许自己给自己发私信')
        
    MsgContent=request.form.get('MsgContent')

    if(MsgContent==None or MsgContent==''):
        return jsonify(data='',code=1,note='表单中需要有MsgContent字段并且不为空字符串')


    Msg=chatTable(MsgContent=MsgContent,From=From.userId,To=To.userId,Time=datetime.datetime.now(),ReadYet=False)
    db.session.add(Msg)
    db.session.commit()

    msg_json=return_msgjson(Msg)
    from_json=return_userjson(From)
    to_json=return_userjson(To)

    return jsonify(data={'msg':msg_json,'from':from_json,'to':to_json},code=200,note='')

@bp.route('/action/recMsgs/allWhoTalkToMe',methods=["GET"])
def f_recMsg_a():
    token=request.headers.get('token')
    token_result = judge_token(token)
    if token_result == False:
        return jsonify(data='',code=1,note='登录令牌错误')
    
    userEmail=token_result['userEmail']
    me=userTable.query.filter_by(userEmail=userEmail).first()

    meId=me.userId
    records=chatTable.query.filter(or_(chatTable.From==meId,chatTable.To==meId)).all()
    
    users=[]
    for record in records:
        if record.From==meId:
            users.append(record.To)
        else:
            users.append(record.From)
    result=(list)((set)(users))

    data_list=[]
    for one in result:
        aUser_jsonify=return_userjson(userTable.query.get(one))
        data_list.append(aUser_jsonify)
    # for aMsg in myMsgs:

    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=data_list,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)

@bp.route('/action/recMsgs/MsgHistoryWithSomeone/<int:userId>',methods=["GET"])
def f_recMsg_s(userId:int):
    token=request.headers.get('token')
    token_result = judge_token(token)
    if token_result == False:
        return jsonify(data='',code=1,note='登录令牌错误')
    
    userEmail=token_result['userEmail']

    me=userTable.query.filter_by(userEmail=userEmail).first()
    other=userTable.query.get(userId)
    if (other==None):
        return jsonify(data='',code=1,note='私信对象不存在')

    if (me==other):
        return jsonify(data='',code=1,note='自己与自己没有私信记录')
        
    meId=me.userId
    otherId=other.userId

    MsgWithSomeone=chatTable.query.filter(or_(and_(chatTable.From==meId,chatTable.To==otherId),and_(chatTable.From==otherId,chatTable.To==meId))).all()
    # MsgOtherSend=chatTable.query.filter_by(From=otherId,To=meId).all()
    for msg in MsgWithSomeone:
        msg.ReadYet=True
    db.session.commit()


    data_list=[]
    for aMsg in MsgWithSomeone:
        aMsg_json=return_msgjson(aMsg)
        data_list.append(aMsg_json)
    # for aMsg in myMsgs:
    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=data_list,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)






@bp.route('/test',methods=['POST'])
def f_test():
    token=request.headers.get('token')
    token_result = judge_token(token)
    if token_result == False:
        return "False"
    
    userEmail=token_result['userEmail']
    fan=userTable.query.filter_by(userEmail=userEmail).first()
    fan.userName='dddd'
    db.session.commit()
    print(fan)
    return "just test"

@bp.route('/')
def hellopage():
    return "Its user page"




#################################################################### 
def getExtensionNameWithDot(completeName:str)->str:
    '''
    return extension name with a dot

    :params completeName: the complete name of the file such as ofeasl.mp4
    '''
    alist=completeName.split(sep='/')
    return '.'+alist[1]

def saveFileAndReturnURL(file,id,subpath)->str:
    '''
    save the file in file system and return the absolute url
    :param file: the file object
    :param id: file id
    :param subpath: the folder under the static
    '''
    filename=(str)(id)+getExtensionNameWithDot(file.content_type)
    path=(os.path.join(projectPath,'static',subpath,filename))
    file.save(path)
    avatarURL=os.path.join(localURL,'static','avatars',filename)
    
    return avatarURL

# 返回token
def get_token(userEmail,userPassword):
    with current_app.app_context():
        s = Serializer(secret_key=current_app.config["SECRET_KEY"],expires_in=3600)
        token = s.dumps({"userEmail":userEmail,"userPassword":userPassword}).decode("ascii")
        return token

def judge_token(token):
    with current_app.app_context():
        try:
            s = Serializer(current_app.config["SECRET_KEY"],expires_in=3600)
            token_result = s.loads(token)
            return token_result
        except:
            return False
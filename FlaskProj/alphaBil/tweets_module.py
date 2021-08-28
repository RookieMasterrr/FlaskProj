from flask import Blueprint,request,jsonify,current_app
import os
from .dbm import db,userTable,likeORdislikeTable,followTable,tweetsTable,t_likeORdislikeTable,t_commentTable
import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .func import paginate, return_userjson,return_tweetjson,return_tComment


projectPath=os.path.dirname(__file__)



bp = Blueprint('tweets_module', __name__)


@bp.route('/',methods=['GET'])
def getAllTweets():
    '''
    return all videos url
    '''
    return 'tweets module'

@bp.route('/action/upload',methods=['POST'])
def upload_tweet():
    '''
    upload the video and return video/owner info
    '''
    # 验证表单
    if request.form.get('tweetContent') in [None,'']:
        return jsonify(data='',code=1,note='form表单参数里需要有tweetContent且不能为空字符串')

    # 验证登录
    token=request.headers.get('token')
    token_result = judge_token(token)
    if token_result == False:
        return jsonify(data='',code=1,note='登录令牌错误')
    
    userEmail=token_result['userEmail']
    uploader=userTable.query.filter_by(userEmail=userEmail).first()
    
    # 判断是否为空表
    if tweetsTable.query.first()==None:
        lastTweetId=0
    else:
    # 获取最后一条记录的ID
        lastTweetId=tweetsTable.query.order_by(tweetsTable.tweetId.desc()).first().tweetId
    # 获得新tweets的ID
    tweetId=lastTweetId+1


    # 构造参数
    tweetId = lastTweetId+1
    ownerId = uploader.userId
    ownerName = uploader.userName
    tweetContent = request.form.get('tweetContent')
    tweetLikeNum = 0
    tweetRetweetNum = 0 
    tweetDislikeNum = 0
    tweetUploadDate  = datetime.datetime.now()
    
    
    
    # 构造表
    tweet=tweetsTable(tweetId = tweetId,ownerId = ownerId,ownerName = ownerName,
    tweetContent = tweetContent,tweetLikeNum = tweetLikeNum,
    tweetRetweetNum = tweetRetweetNum, tweetDislikeNum = tweetDislikeNum,tweetUploadDate  = tweetUploadDate)


    db.session.add(tweet)

    uploader.userTweetsNum+=1
    
    db.session.commit()
    
    
    # 构造响应
    tweetjson=return_tweetjson(tweet)
    # find the user
    # aUser = userTable.query.get(ownerId)
    userjson=return_userjson(uploader)


    return jsonify(data={'user':userjson,'tweet':tweetjson},code=0,note='')




@bp.route('/action/return/all',methods=['GET'])
def get_all_tweets():
    '''
    return all tweets
    '''
    tweetlist=tweetsTable.query.all()
    datalist=[]
    for tweet in tweetlist:
        aTweet=return_tweetjson(tweet)
        userId=tweet.ownerId
        user=userTable.query.get(userId)
        aUser=return_userjson(user)
        datalist.append({'tweet':aTweet,'user':aUser})


    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=datalist,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)

@bp.route('/action/return/someone/<int:userId>',methods=['GET'])
def get_some_tweets(userId):
    '''
    return someones tweets
    '''
    if (userTable.query.get(userId)==None):
        return jsonify(data='',code=1,note='没有该用户')

    tweetlist=tweetsTable.query.filter_by(ownerId=userId).all()
    datalist=[]
    for tweet in tweetlist:
        aTweet_json=return_tweetjson(tweet)
        userId=tweet.ownerId
        user=userTable.query.get(userId)
        aUser_json=return_userjson(user)
        datalist.append({'tweet':aTweet_json,'owner':aUser_json})

    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=datalist,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)

@bp.route('/action/return/single/<int:tweetId>',methods=['GET'])
def get_single_tweets(tweetId):
    '''
    return single video
    '''
    if (tweetsTable.query.get(tweetId)==None):
        return jsonify(data='',code=1,note='没有该推文')

    
    tweet=tweetsTable.query.get(tweetId)
    ownerId=tweet.ownerId
    owner=userTable.query.get(ownerId)
        

    db.session.commit()
    tweet_json=return_tweetjson(tweet)
    user_json=return_userjson(owner)

    return jsonify(data={'owner':user_json,'tweet':tweet_json},code=200,note='')

@bp.route('/action/return/myfollow',methods=['GET'])
def get_myfollow_tweets():
    '''
    return someones tweets
    '''
    token=request.headers.get('token')
    token_result = judge_token(token)
    if token_result == False:
        return jsonify(data='',code=1,note='登录令牌错误')
    userEmail=token_result['userEmail']
    # who am i
    user=userTable.query.filter_by(userEmail=userEmail).first()
    
    datalist=[]
    # who i follow
    myFollowPeople=followTable.query.filter_by(fanId=user.userId).all()
    for followItem in myFollowPeople:
        vloger=userTable.query.get(followItem.vlogerId)
        tweets=tweetsTable.query.filter_by(ownerId=vloger.userId).all()
        for tweet in tweets:
            aTweet_json=return_tweetjson(tweet)
            aUser_json=return_userjson(vloger)
            datalist.append({'tweet':aTweet_json,'owner':aUser_json})


    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=datalist,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)




@bp.route('/action/likeORdislike/<int:tweetId>',methods=['POST'])
def like_tweet(tweetId):
    # 先判断有没有这个推文存在
    tweetIfExist=tweetsTable.query.get(tweetId)
    if(tweetIfExist==None):
        return jsonify(data='',code=1,note='该推文不存在')
        
    # 验证登录 
    token=request.headers.get('token')
    token_result = judge_token(token)
    if token_result == False:
        return jsonify(data='',code=1,note='登录令牌错误')


    userEmail=token_result['userEmail']
    user=userTable.query.filter_by(userEmail=userEmail).first()
    userId=user.userId
    
    tweet=tweetsTable.query.get(tweetId)

    likeORdislike = (int)(request.form.get('likeORdislike'))


    thisUserLikeList=t_likeORdislikeTable.query.filter_by(userId=userId).all()
     


    # 如果有记录
    for likeORdislikeItem in thisUserLikeList:
        if(likeORdislikeItem.tweetId==tweetId):
            if(likeORdislike==0 and likeORdislikeItem.likeORdislike==0):
                db.session.delete(likeORdislikeItem)
                tweet.tweetDislikeNum-=1
                db.session.commit()
                # 'you hated it but ok with it now'
                user_json=return_userjson(user)
                tweet_json=return_tweetjson(tweet)
                return jsonify(data={'user':user_json,'tweet':tweet_json,'record':None},code=200)
                
            if(likeORdislike==0 and likeORdislikeItem.likeORdislike==1):
                likeORdislikeItem.likeORdislike=0
                tweet.tweetLikeNum-=1
                tweet.tweetDislikeNum+=1
                db.session.commit()

                state_json={'userId':likeORdislikeItem.userId,'tweetId':likeORdislikeItem.tweetId,'likeORdislike':likeORdislikeItem.likeORdislike,'likeORdislikeDate':likeORdislikeItem.likeORdisplkeDate}

                user_json=return_userjson(user)
                tweet_json=return_tweetjson(tweet)
                # 'you liked it but hate it now'
                return jsonify(data={'user':user_json,'tweet':tweet_json,'record':state_json},code=200)

            if(likeORdislike==1 and likeORdislikeItem.likeORdislike==0):
                likeORdislikeItem.likeORdislike=1
                tweet.tweetLikeNum+=1
                tweet.tweetDislikeNum-=1
                db.session.commit()

                state_json={'userId':likeORdislikeItem.userId,'tweetId':likeORdislikeItem.tweetId,'likeORdislike':likeORdislikeItem.likeORdislike,'likeORdislikeDate':likeORdislikeItem.likeORdisplkeDate}

                'you hated it but like it now'
                user_json=return_userjson(user)
                tweet_json=return_tweetjson(tweet)
                return jsonify(data={'user':user_json,'tweet':tweet_json,'record':state_json},code=200)

            if(likeORdislike==1 and likeORdislikeItem.likeORdislike==1):
                db.session.delete(likeORdislikeItem)
                tweet.tweetLikeNum-=1
                db.session.commit()
                user_json=return_userjson(user)
                tweet_json=return_tweetjson(tweet)
                return jsonify(data={'user':user_json,'tweet':tweet_json,'record':None},code=200)
            
    # 如果没记录
    if(likeORdislike==0):#dislike
        aDislikeRequest=t_likeORdislikeTable(userId=userId,tweetId=tweetId,likeORdislike=0,likeORdisplkeDate=datetime.datetime.now())
        tweet.tweetDislikeNum+=1
        db.session.add(aDislikeRequest)
        db.session.commit()
        state_json={'userId':user.userId,'tweetId':tweet.tweetId,'likeORdislike':0,'likeORdislikeDate':datetime.datetime.now()}
        user_json=return_userjson(user)
        tweet_json=return_tweetjson(tweet)
        return jsonify(data={'user':user_json,'tweet':tweet_json,'record':state_json},code=200)

    if(likeORdislike==1):#like
        aLikeRequest=t_likeORdislikeTable(userId=userId,tweetId=tweetId,likeORdislike=1,likeORdisplkeDate=datetime.datetime.now())
        tweet.tweetLikeNum+=1
        db.session.add(aLikeRequest)
        db.session.commit()
        state_json={'userId':user.userId,'tweetId':tweet.tweetId,'likeORdislike':1,'likeORdislikeDate':datetime.datetime.now()}
        user_json=return_userjson(user)
        tweet_json=return_tweetjson(tweet)
        return jsonify(data={'user':user_json,'tweet':tweet_json,'record':state_json},code=200)

@bp.route('/action/likeORdislikeRecord',methods=["GET"])
def iflikeornot():
    userId=(int)(request.args.get('user'))
    tweetId=(int)(request.args.get('tweet'))
    
    user=userTable.query.get(userId)
    tweet=tweetsTable.query.get(tweetId)

    user_json=return_userjson(user)
    tweet_json=return_tweetjson(tweet)

    like=t_likeORdislikeTable.query.get([userId,tweetId])

    if(like==None):
        return jsonify(data={'user':user_json,'tweet':tweet_json,'record':None},code=200)
    record={'userId':like.userId,'tweetId':like.tweetId,'likeORdislike':like.likeORdislike,'likeORdislikeDate':like.likeORdisplkeDate}
    return jsonify(data={'user':user_json,'tweet':tweet_json,'record':record},code=200)

@bp.route('/action/search/',methods=["GET"])
def f_search_t():
    query=request.args.get('query')
    if(not 'query' in request.args.keys()) or query=='':
        return jsonify(data='',code=1,note='url中需要有query参数并且需要有值')
    result=tweetsTable.query.whooshee_search(query).all()


    data_list=[]
    for tweet in result:
        ownerId=tweet.ownerId
        user=userTable.query.get(ownerId)
        tweet_json=return_tweetjson(tweet)
        user_json=return_userjson(user)
        data_list.append({'tweet':tweet_json,'user':user_json})


    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=data_list,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)




@bp.route('/action/comment/<int:tweetId>',methods=['POST'])
def comment(tweetId):
    # 先判断有没有这个视频存在
    tweetIfExist=tweetsTable.query.get(tweetId)
    if(tweetIfExist==None):
        return jsonify(data='',code=1,note='该推文不存在')

    if (request.form.get('comment') in [None,'']):
        return jsonify(data='',code=1,note='form表单中需要有comment字段并且不为空字符串')


    token=request.headers.get('token')
    token_result = judge_token(token)
    if token_result == False:
        return jsonify(data='',code=1,note='登录令牌错误')
    
    userEmail=token_result['userEmail']

    user=userTable.query.filter_by(userEmail=userEmail).first()
    tweet=tweetsTable.query.get(tweetId)

    aComment=t_commentTable(tweetId=tweet.tweetId, userId=user.userId,
                 comment=request.form.get('comment'), date=datetime.datetime.now())
    db.session.add(aComment)
    db.session.commit()

    comment_json=return_tComment(aComment)

    return jsonify(data=comment_json,code=0,note='')

@bp.route('/action/show/comment/<int:tweetId>',methods=['GET'])
def show_comment(tweetId):
    # 先判断有没有这个视频存在
    tweetIfExist=tweetsTable.query.get(tweetId)
    if(tweetIfExist==None):
        return jsonify(data='',code=1,note='该推文不存在')

    data_list=[]
    comments=t_commentTable.query.filter_by(tweetId=tweetId)
    for comment in comments:
        user=userTable.query.get(comment.userId)
        data_list.append({'comment':return_tComment(comment),'user':return_userjson(user)})


    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=data_list,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)





###################Some Function Took##########################

def judge_token(token)->bool:
    with current_app.app_context():
        try:
            s = Serializer(current_app.config["SECRET_KEY"],expires_in=3600)
            token_result = s.loads(token)
            return token_result
        except:
            return False
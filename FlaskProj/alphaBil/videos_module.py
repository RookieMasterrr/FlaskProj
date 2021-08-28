from re import L
from flask import Blueprint,request,jsonify,current_app
import os
from .dbm import db,videosTable,userTable,likeORdislikeTable,collectTable,followTable,v_commentTable
import datetime
from moviepy.editor import VideoFileClip
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .func import localURL,return_userjson,return_videojson,paginate,return_vComment

projectPath=os.path.dirname(__file__)

bp = Blueprint('videos_module', __name__)

@bp.route('/',methods=['GET'])
def getAllVideos():
    '''
    return all videos url
    '''
    return 'videos module'




@bp.route('/action/upload',methods=['POST'])
def upload_video():
    '''
    upload the video and return video/owner info
    '''
    # 验证参数
    if ('videoFile' not in request.files.keys()) or ('videoName' not in request.form.keys()) or ('coverFile' not in request.files.keys()):
        return jsonify(data='',code=1,note='form表单中需要有videoFile和videoName和coverFile参数') 

    if (request.files.get('videoFile').content_type==None) or (request.form.get('videoName')=='') or (request.files.get('coverFile').content_type==None):
        return jsonify(data='',code=1,note='form表单中需要有videoFile和videoName和coverFile参数') 
    
    # 验证格式   
    LegalVideoExtensionName=['.mp4','.avi','.x-msvideo']
    print(getExtensionNameWithDot(request.files.get('videoFile').content_type))
    if getExtensionNameWithDot(request.files.get('videoFile').content_type) not in LegalVideoExtensionName:
        return jsonify(data='',code=1,note='视频文件仅支持mp4格式')

    LegalVideoExtensionName=['.jpg','.png','.jpeg']
    if getExtensionNameWithDot(request.files.get('coverFile').content_type) not in LegalVideoExtensionName:
        return jsonify(data='',code=1,note='图像文件仅支持jpg,png,jpeg格式')


    # 验证登录
    token=request.headers.get('token')
    token_result = judge_token(token)
    if token_result == False:
        return jsonify(data='',code=1,note='登录令牌错误')
    
    userEmail=token_result['userEmail']
    uploader=userTable.query.filter_by(userEmail=userEmail).first()
    
    # 判断是否为空表
    if videosTable.query.first()==None:
        lastVideoId=0
    else:
    # 获取最后一条记录的ID
        lastVideoId=videosTable.query.order_by(videosTable.videoId.desc()).first().videoId
    # 获得新视频的ID
    videoId=lastVideoId+1
    

    # 获得新视频的完整文件名并且保存
    videoFile=request.files.get('videoFile')

    videoFilename=(str)(videoId)+getExtensionNameWithDot(videoFile.content_type)
    videoPath=(os.path.join(projectPath,'static','videos',videoFilename))
    videoFile.save(videoPath)
    
    # 获得新视频封面的完整文件名并且保存
    coverFile=request.files.get('coverFile')
    coverFilename=(str)(videoId)+getExtensionNameWithDot(coverFile.content_type)
    coverPath=(os.path.join(projectPath,'static','videoCover',coverFilename))
    coverFile.save(coverPath)
    


    # 构造参数
    ownerId = uploader.userId
    ownerName = uploader.userName
    videoName = request.form.get('videoName')
    videoDescribe = request.form.get('videoDescribe')
    videoSize = getvideosize((str)(videoFilename))
    videoTimeLength = getvideostime((str)(videoFilename))
    videoCollectedNum = 0
    videoLikeNum = 0
    videoRetweetNum = 0
    videoDislikeNum = 0
    videoUploadDate = datetime.datetime.now()


    # 新视频url
    videoURL=os.path.join(localURL,'static','videos',videoFilename)
    coverURL=os.path.join(localURL,'static','videoCover',coverFilename)
    
    # 构造表
    video1=videosTable(videoId=videoId,ownerId=ownerId ,ownerName=ownerName ,videoName=videoName ,
    videoURL=videoURL,coverId=videoId,coverURL=coverURL,videoDescribe=videoDescribe ,videoViewNum=0, 
    videoSize=videoSize ,videoTimeLength=videoTimeLength ,videoCollectedNum=videoCollectedNum ,
    videoLikeNum=videoLikeNum ,videoRetweetNum=videoRetweetNum ,videoDislikeNum=videoDislikeNum ,videoUploadDate=videoUploadDate)
    db.session.add(video1)

    uploader.userVideosNum+=1
    
    db.session.commit()
    
    
    # 构造响应
    videojson=return_videojson(video1)
    # find the user
    # aUser = userTable.query.get(ownerId)
    userjson=return_userjson(uploader)


    return jsonify(data={'user':userjson,'video':videojson},code=0,note='')

@bp.route('/action/return/all',methods=['GET'])
def get_all_videos():
    '''
    return all videos
    '''
    videolist=videosTable.query.all()
    datalist=[]
    for info in videolist:
        aVideo=return_videojson(info)
        userId=info.ownerId
        user=userTable.query.get(userId)
        aUser=return_userjson(user)
        datalist.append({'video':aVideo,'user':aUser})


    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=datalist,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)

@bp.route('/action/return/someone/<int:userId>',methods=['GET'])
def get_some_videos(userId):
    '''
    return someones videos
    '''
    if (userTable.query.get(userId)==None):
        return jsonify(data='',code=1,note='没有该用户')
    videolist=videosTable.query.filter_by(ownerId=userId).all()
    datalist=[]
    for info in videolist:
        aVideo_json=return_videojson(info)
        userId=info.ownerId
        user=userTable.query.get(userId)
        aUser_json=return_userjson(user)
        datalist.append({'video':aVideo_json,'owner':aUser_json})


    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=datalist,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)

@bp.route('/action/return/single/<int:videoId>',methods=['GET'])
def get_single_videos(videoId):
    '''
    return single video
    '''
    if (videosTable.query.get(videoId)==None):
        return jsonify(data='',code=1,note='没有该视频')
    video=videosTable.query.get(videoId)
    ownerId=video.ownerId
    owner=userTable.query.get(ownerId)
    
    video.videoViewNum+=1
    

    db.session.commit()
    video_json=return_videojson(video)
    user_json=return_userjson(owner)

    return jsonify(data={'owner':user_json,'video':video_json},code=200,note='')

@bp.route('/action/return/myfollow',methods=['GET'])
def get_myfollow_videos():
    '''
    return someones videos
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
        videos=videosTable.query.filter_by(ownerId=vloger.userId).all()
        for video in videos:
            aVideo_json=return_videojson(video)
            aUser_json=return_userjson(vloger)
            datalist.append({'video':aVideo_json,'owner':aUser_json})


    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=datalist,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)

@bp.route('/action/return/mycollection',methods=['GET'])
def get_myCollection_videos():
    '''
    return someones videos
    '''
    token=request.headers.get('token')
    token_result = judge_token(token)
    if token_result == False:
        return jsonify(data='',code=1,note='登录令牌错误')
    userEmail=token_result['userEmail']
    # who am i
    user=userTable.query.filter_by(userEmail=userEmail).first()
    
    datalist=[]
    #  
    mycollection=collectTable.query.filter_by(userId=user.userId).all()
    for collectionItem in mycollection:
        vloger=userTable.query.get(collectionItem.userId)
        video=videosTable.query.get(collectionItem.videoId)
        aVideo_json=return_videojson(video)
        aUser_json=return_userjson(vloger)
        datalist.append({'video':aVideo_json,'owner':aUser_json})


    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=datalist,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)



@bp.route('/action/likeORdislike/<int:videoId>',methods=['POST'])
def like_video(videoId):
    # 先判断有没有这个视频存在
    videoIfExist=videosTable.query.get(videoId)
    if(videoIfExist==None):
        return jsonify(data='',code=1,note='该视频不存在')
        
    # 验证登录 
    token=request.headers.get('token')
    token_result = judge_token(token)
    if token_result == False:
        return jsonify(data='',code=1,note='登录令牌错误')


    userEmail=token_result['userEmail']
    user=userTable.query.filter_by(userEmail=userEmail).first()
    userId=user.userId
    
    video=videosTable.query.get(videoId)

    likeORdislike = (int)(request.form.get('likeORdislike'))

    thisUserLikeList=likeORdislikeTable.query.filter_by(userId=userId).all()
     


    # 如果有记录
    for likeORdislikeItem in thisUserLikeList:
        if(likeORdislikeItem.videoId==videoId):
            if(likeORdislike==0 and likeORdislikeItem.likeORdislike==0):
                db.session.delete(likeORdislikeItem)
                video.videoDislikeNum-=1
                db.session.commit()
                # 'you hated it but ok with it now'
                user_json=return_userjson(user)
                video_json=return_videojson(video)
                return jsonify(data={'user':user_json,'video':video_json,'record':None},code=200)
                
            if(likeORdislike==0 and likeORdislikeItem.likeORdislike==1):
                likeORdislikeItem.likeORdislike=0
                video.videoLikeNum-=1
                video.videoDislikeNum+=1
                db.session.commit()

                state_json={'userId':likeORdislikeItem.userId,'videoId':likeORdislikeItem.videoId,'likeORdislike':likeORdislikeItem.likeORdislike,'likeORdislikeDate':likeORdislikeItem.likeORdisplkeDate}

                user_json=return_userjson(user)
                video_json=return_videojson(video)
                # 'you liked it but hate it now'
                return jsonify(data={'user':user_json,'video':video_json,'record':state_json},code=200)

            if(likeORdislike==1 and likeORdislikeItem.likeORdislike==0):
                likeORdislikeItem.likeORdislike=1
                video.videoLikeNum+=1
                video.videoDislikeNum-=1
                db.session.commit()

                state_json={'userId':likeORdislikeItem.userId,'videoId':likeORdislikeItem.videoId,'likeORdislike':likeORdislikeItem.likeORdislike,'likeORdislikeDate':likeORdislikeItem.likeORdisplkeDate}

                'you hated it but like it now'
                user_json=return_userjson(user)
                video_json=return_videojson(video)
                return jsonify(data={'user':user_json,'video':video_json,'record':state_json},code=200)

            if(likeORdislike==1 and likeORdislikeItem.likeORdislike==1):
                db.session.delete(likeORdislikeItem)
                video.videoLikeNum-=1
                db.session.commit()
                user_json=return_userjson(user)
                video_json=return_videojson(video)
                return jsonify(data={'user':user_json,'video':video_json,'record':None},code=200)
            
    # 如果没记录
    if(likeORdislike==0):#dislike
        aDislikeRequest=likeORdislikeTable(userId=userId,videoId=videoId,likeORdislike=0,likeORdisplkeDate=datetime.datetime.now())
        video.videoDislikeNum+=1
        db.session.add(aDislikeRequest)
        db.session.commit()
        state_json={'userId':user.userId,'videoId':video.videoId,'likeORdislike':0,'likeORdislikeDate':datetime.datetime.now()}
        user_json=return_userjson(user)
        video_json=return_videojson(video)
        return jsonify(data={'user':user_json,'video':video_json,'record':state_json},code=200)

    if(likeORdislike==1):#like
        aLikeRequest=likeORdislikeTable(userId=userId,videoId=videoId,likeORdislike=1,likeORdisplkeDate=datetime.datetime.now())
        video.videoLikeNum+=1
        db.session.add(aLikeRequest)
        db.session.commit()
        state_json={'userId':user.userId,'videoId':video.videoId,'likeORdislike':1,'likeORdislikeDate':datetime.datetime.now()}
        user_json=return_userjson(user)
        video_json=return_videojson(video)
        return jsonify(data={'user':user_json,'video':video_json,'record':state_json},code=200)

@bp.route('/action/collect/<int:videoId>',methods=['POST'])
def collect_video(videoId):
    # 先判断有没有这个视频存在
    videoIfExist=videosTable.query.get(videoId)
    if(videoIfExist==None):
        return jsonify(data='',code=1,note='该视频不存在')


    token=request.headers.get('token')
    token_result = judge_token(token)
    if token_result == False:
        return jsonify(data='',code=1,note='登录令牌错误')
    
    userEmail=token_result['userEmail']
    user=userTable.query.filter_by(userEmail=userEmail).first()
    userId=user.userId
    
    video=videosTable.query.get(videoId)



    thisUserCollectList=collectTable.query.filter_by(userId=userId).all()
    for collectItem in thisUserCollectList:
        if(collectItem.videoId==videoId):
            db.session.delete(collectItem)
            video.videoCollectedNum-=1
            db.session.commit()
            # "cancle collect"
            user_json=return_userjson(user)
            video_json=return_videojson(video)
            return jsonify(data={'user':user_json,'video':video_json,'record':None},code=200,note='')



    aCollectRequest=collectTable(userId=userId,videoId=videoId,collectDate=datetime.datetime.now())

    db.session.add(aCollectRequest)
    video.videoCollectedNum+=1
    db.session.commit()

    user_json=return_userjson(user)
    video_json=return_videojson(video)
    
    record={'userId':aCollectRequest.userId,'videoId':aCollectRequest.videoId,'collectDate':aCollectRequest.collectDate}
    # "collect"
    return jsonify(data={'user':user_json,'video':video_json,'record':record},code=200,note='')

@bp.route('/action/likeORdislikeRecord',methods=["GET"])
def iflikeornot():
    userId=(int)(request.args.get('user'))
    videoId=(int)(request.args.get('video'))
    
    user=userTable.query.get(userId)
    video=videosTable.query.get(videoId)

    user_json=return_userjson(user)
    video_json=return_videojson(video)

    like=likeORdislikeTable.query.get([userId,videoId])
    if(like==None):
        return jsonify(data={'user':user_json,'video':video_json,'record':None},code=200)
    record={'userId':like.userId,'videoId':like.videoId,'likeORdislike':like.likeORdislike,'likeORdislikeDate':like.likeORdisplkeDate}
    return jsonify(data={'user':user_json,'video':video_json,'record':record},code=200)




@bp.route('/action/search/orderbyTimeLength',methods=["GET"])
def f_search_t():
    query=request.args.get('query')
    desc=request.args.get('desc')

    if(not 'query' in request.args.keys()) or query=='':
        return jsonify(data='',code=1,note='url中需要有query参数并且需要有值')


    result=videosTable.query.whooshee_search(query).all()
    if(desc=='1'):
        # 降序
        result.sort(key=lambda item:item.videoTimeLength,reverse=True)
    else:
        # 升序
        result.sort(key=lambda item:item.videoTimeLength,reverse=False)


    data_list=[]
    for video in result:
        ownerId=video.ownerId
        user=userTable.query.get(ownerId)
        video_json=return_videojson(video)
        user_json=return_userjson(user)
        data_list.append({'video':video_json,'user':user_json})


    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=data_list,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)

@bp.route('/action/search/orderbyLikeNum',methods=["GET"])
def f_search_l():
    query=request.args.get('query')
    desc=request.args.get('desc')

    if(not 'query' in request.args.keys()) or query=='':
        return jsonify(data='',code=1,note='url中需要有query参数并且需要有值')


    result=videosTable.query.whooshee_search(query).all()
    if(desc=='1'):
        # 降序
        result.sort(key=lambda item:item.videoLikeNum,reverse=True)
    else:
        # 升序
        result.sort(key=lambda item:item.videoLikeNum,reverse=False)

    data_list=[]
    for video in result:
        ownerId=video.ownerId
        user=userTable.query.get(ownerId)
        video_json=return_videojson(video)
        user_json=return_userjson(user)
        data_list.append({'video':video_json,'user':user_json})

    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=data_list,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)

@bp.route('/action/search/orderbyCollectNum',methods=["GET"])
def f_search_c():
    query=request.args.get('query')
    desc=request.args.get('desc')

    if(not 'query' in request.args.keys()) or query=='':
        return jsonify(data='',code=1,note='url中需要有query参数并且需要有值')


    result=videosTable.query.whooshee_search(query).all()
    if(desc=='1'):
        # 降序
        result.sort(key=lambda item:item.videoCollectedNum,reverse=True)
    else:
        # 升序
        result.sort(key=lambda item:item.videoCollectedNum,reverse=False)

    data_list=[]
    for video in result:
        ownerId=video.ownerId
        user=userTable.query.get(ownerId)
        video_json=return_videojson(video)
        user_json=return_userjson(user)
        data_list.append({'video':video_json,'user':user_json})


    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=data_list,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)

@bp.route('/action/search/orderbyViewNum',methods=["GET"])
def f_search_v():
    query=request.args.get('query')
    desc=request.args.get('desc')

    if(not 'query' in request.args.keys()) or query=='':
        return jsonify(data='',code=1,note='url中需要有query参数并且需要有值')


    result=videosTable.query.whooshee_search(query).all()
    if(desc=='1'):
        # 降序
        result.sort(key=lambda item:item.videoViewNum,reverse=True)
    else:
        # 升序
        result.sort(key=lambda item:item.videoViewNum,reverse=False)

    data_list=[]
    for video in result:
        ownerId=video.ownerId
        user=userTable.query.get(ownerId)
        video_json=return_videojson(video)
        user_json=return_userjson(user)
        data_list.append({'video':video_json,'user':user_json})


    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=data_list,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)

@bp.route('/<int:id>',methods=['DELETE'])
def deleteSingleVideos(id):
    '''
    delete single videos
    '''
    return 'deleteid='+(str)(id)

@bp.route('filetest',methods=['POST'])
def atest():
    file1=request.files.get('file')
    print(getExtensionNameWithDot(file1.content_type))

    file2=request.files.get('file2')
    print(getExtensionNameWithDot(file2.content_type))
    return "HEY"




@bp.route('/action/comment/<int:videoId>',methods=['POST'])
def comment(videoId):
    # 先判断有没有这个视频存在
    videoIfExist=videosTable.query.get(videoId)
    if(videoIfExist==None):
        return jsonify(data='',code=1,note='该视频不存在')

    if (request.form.get('comment') in [None,'']):
        return jsonify(data='',code=1,note='form表单中需要有comment字段并且不为空字符串')


    token=request.headers.get('token')
    token_result = judge_token(token)
    if token_result == False:
        return jsonify(data='',code=1,note='登录令牌错误')
    
    userEmail=token_result['userEmail']

    user=userTable.query.filter_by(userEmail=userEmail).first()
    video=videosTable.query.get(videoId)

    aComment=v_commentTable(videoId=video.videoId, userId=user.userId,
                 comment=request.form.get('comment'), date=datetime.datetime.now())
    db.session.add(aComment)
    db.session.commit()

    comment_json=return_vComment(aComment)

    return jsonify(data=comment_json,code=0,note='')

@bp.route('/action/show/comment/<int:videoId>',methods=['GET'])
def show_comment(videoId):
    # 先判断有没有这个视频存在
    videoIfExist=videosTable.query.get(videoId)
    if(videoIfExist==None):
        return jsonify(data='',code=1,note='该视频不存在')

    data_list=[]
    comments=v_commentTable.query.filter_by(videoId=videoId)
    for comment in comments:
        user=userTable.query.get(comment.userId)
        data_list.append({'comment':return_vComment(comment),'user':return_userjson(user)})


    peerpage=(int)(request.args.get('peerpage',5))
    page=(int)(request.args.get('page',1))
    funcResult=paginate(data=data_list,peerpage=peerpage,page=page)
    data=funcResult[0]
    pageInfo={'dataLength':funcResult[1],'peerpage':funcResult[2],'nowpage':funcResult[3],
    'maxPage':funcResult[4],'minPage':funcResult[5],'ifhavebefore':funcResult[6],'ifhavenext':funcResult[7]}
    return jsonify(data=data,code=200,pageInfo=pageInfo)





###################Some Function Took##########################

def getExtensionNameWithDot(completeName:str)->str:
    '''
    return extension name with a dot
    '''
    alist=completeName.split(sep='/')
    return '.'+alist[1]

def getvideosize(videofilename:str)->int:
    '''
    return the video size(int/megabyte)
    '''
    filereadpath=os.path.join(projectPath,'static','videos',videofilename)
    videosize=os.path.getsize(filereadpath)
    return videosize

def getvideostime(videofilename:str)->float:
    '''
    return the video time(float/second)
    '''
    filereadpath=os.path.join(projectPath,'static','videos',videofilename)
    clip = VideoFileClip(filereadpath)
    file_time = (clip.duration)
    return file_time

def judge_token(token)->bool:
    with current_app.app_context():
        try:
            s = Serializer(current_app.config["SECRET_KEY"],expires_in=3600)
            token_result = s.loads(token)
            return token_result
        except:
            return False
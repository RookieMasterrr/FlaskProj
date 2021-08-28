localURL='http://159.75.31.178:5000'
from math import ceil

def return_userjson(user):
    user_json={'userId' : user.userId,
    'userName' : user.userName,
    'userVideosNum' : user.userVideosNum,
    'userTweetsNum' : user.userTweetsNum,
    'userSelfDescribe' : user.userSelfDescribe,
    'userAvatarPath' : user.userAvatarPath,
    'userFollowNumber' : user.userFollowNumber,
    'userFansNumber' : user.userFansNumber,
    'userEmail' : user.userEmail,
    'userRegisterDate' : user.userRegisterDate
    }
    return user_json

def return_videojson(video):
    video_json={'videoId':video.videoId , 'ownerId':video.ownerId, 'ownerName':video.ownerName, 
    'videoName':video.videoName,'coverId':video.videoId, 'videoURL':video.videoURL, 
    'coverURL':video.coverURL,'videoDescribe':video.videoDescribe,'videoViewNum':video.videoViewNum,'videoSize':video.videoSize, 
    'videoTimeLength':video.videoTimeLength,'videoCollectedNum':video.videoCollectedNum, 
    'videoLikeNum':video.videoLikeNum, 'videoRetweetNum':video.videoRetweetNum,
     'videoDislikeNum':video.videoDislikeNum, 'videoUploadDate':video.videoUploadDate
    }
    return video_json

def return_tweetjson(tweet):
    tweet_json={'tweetId' : tweet.tweetId,'ownerId' : tweet.ownerId,'ownerName' : tweet.ownerName,
    'tweetContent' : tweet.tweetContent,'tweetLikeNum' : tweet.tweetLikeNum,
    'tweetRetweetNum' : tweet.tweetRetweetNum, 'tweetDislikeNum' : tweet.tweetDislikeNum,
    'tweetUploadDate' : tweet.tweetUploadDate}
    return tweet_json

def return_msgjson(msg):
    msg_json={'MsgId':msg.MsgId,'MsgContent':msg.MsgContent,'From':msg.From,'To':msg.To,'Time':msg.Time,'ReadYet':msg.ReadYet}
    return msg_json

def paginate(data:list,peerpage:int,page:int)->list:
    '''
    It is a paginate page
    :parameter data: the list waited to be cut
    :parameter peerpage: how many data in a page
    :parameter page: which page you want
    '''
    begin=(page-1)*peerpage
    end=(page*peerpage)-1
    cutData=data[begin:end+1]

    dataLength=len(data)
    maxPage=ceil(dataLength/peerpage)
    minPage=1
    #         0        1          2     3      4       5         6            7
    return cutData,dataLength,peerpage,page,maxPage,minPage,page>minPage,page<maxPage

def return_vComment(comment):
    comment_json={'commentId':comment.commentId,'videoId':comment.videoId ,
                'userId':comment.userId ,'comment':comment.comment, 'date':comment.date}
    return comment_json

def return_tComment(comment):
    comment_json={'commentId':comment.commentId,'tweetId':comment.tweetId ,
                'userId':comment.userId ,'comment':comment.comment, 'date':comment.date}
    return comment_json
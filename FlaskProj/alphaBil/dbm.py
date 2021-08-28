from flask_whooshee import Whooshee
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
whooshee = Whooshee()
db=SQLAlchemy()
mail=Mail()

@whooshee.register_model('videoName','videoDescribe')
class videosTable(db.Model): 
    videoId = db.Column(db.Integer, primary_key=True)
    ownerId = db.Column(db.Integer,nullable=False)
    ownerName = db.Column(db.String,nullable=False)
    videoName = db.Column(db.String,nullable=False)
    coverId = db.Column(db.Integer,nullable=True)
    videoURL = db.Column(db.String,nullable=False)
    coverURL = db.Column(db.String,nullable=False)
    videoDescribe = db.Column(db.String,nullable=True)
    videoViewNum = db.Column(db.Integer,nullable=True)
    videoSize = db.Column(db.Integer,nullable=False)
    videoTimeLength = db.Column(db.Float,nullable=False)
    videoCollectedNum = db.Column(db.Integer,nullable=False)
    videoLikeNum = db.Column(db.Integer,nullable=False)
    videoRetweetNum = db.Column(db.Integer,nullable=False)
    videoDislikeNum = db.Column(db.Integer,nullable=False)
    videoUploadDate  = db.Column(db.DateTime,nullable=False)

@whooshee.register_model('tweetContent')
class tweetsTable(db.Model): 
    tweetId = db.Column(db.Integer, primary_key=True)
    ownerId = db.Column(db.Integer,nullable=False)
    ownerName = db.Column(db.String,nullable=False)
    tweetContent = db.Column(db.String,nullable=False)
    tweetLikeNum = db.Column(db.Integer,nullable=False)
    tweetRetweetNum = db.Column(db.Integer,nullable=False)
    tweetDislikeNum = db.Column(db.Integer,nullable=False)
    tweetUploadDate  = db.Column(db.DateTime,nullable=False)

@whooshee.register_model('userName')
class userTable(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    userPassword = db.Column(db.String, nullable=False)
    userName = db.Column(db.String, nullable=False)
    userVideosNum = db.Column(db.Integer, nullable=False)
    userTweetsNum = db.Column(db.Integer, nullable=False)
    userSelfDescribe = db.Column(db.String, nullable=True)
    userAvatarPath = db.Column(db.String, nullable=True)
    userFollowNumber = db.Column(db.Integer, nullable=False)
    userFansNumber = db.Column(db.Integer, nullable=False)
    userEmail = db.Column(db.String, nullable=False, unique=True)
    userRegisterDate = db.Column(db.DateTime, nullable=False)
    userState =  db.Column(db.Integer, nullable=False)
    userRank = db.Column(db.Integer, nullable=False)

class likeORdislikeTable(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    videoId = db.Column(db.Integer, primary_key=True)
    likeORdislike = db.Column(db.Integer, nullable=True)
    likeORdisplkeDate  = db.Column(db.DateTime, nullable=False)

class t_likeORdislikeTable(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    tweetId = db.Column(db.Integer, primary_key=True)
    likeORdislike = db.Column(db.Integer, nullable=True)
    likeORdisplkeDate  = db.Column(db.DateTime, nullable=False)

class collectTable(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    videoId = db.Column(db.Integer, primary_key=True)
    collectDate  = db.Column(db.DateTime, nullable=False)

class followTable(db.Model):
    fanId = db.Column(db.Integer, primary_key=True)
    fanName = db.Column(db.String, nullable=False)
    vlogerId = db.Column(db.Integer, primary_key=True)
    vlogerName = db.Column(db.String, nullable=False)
    followDate  = db.Column(db.DateTime, nullable=False)

class viewTable(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    videoId = db.Column(db.Integer, primary_key=True)
    viewDate  = db.Column(db.DateTime, nullable=False)

class chatTable(db.Model):
    MsgId = db.Column(db.Integer, primary_key=True)
    MsgContent = db.Column(db.String, nullable=False)
    From = db.Column(db.Integer, nullable=False)
    To = db.Column(db.Integer, nullable=False)
    Time = db.Column(db.DateTime, nullable=False)
    ReadYet = db.Column(db.Boolean, nullable=False)

class v_commentTable(db.Model):
    commentId = db.Column(db.Integer, primary_key=True)
    videoId = db.Column(db.Integer)
    userId = db.Column(db.Integer)
    comment = db.Column(db.String)
    date = db.Column(db.DateTime)

class t_commentTable(db.Model):
    commentId = db.Column(db.Integer, primary_key=True)
    tweetId = db.Column(db.Integer)
    userId = db.Column(db.Integer)
    comment = db.Column(db.String)
    date = db.Column(db.DateTime)

class v_retweetTable(db.Model):
    retweetId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer)
    videoId = db.Column(db.Integer)
    retweetReason = db.Column(db.String)
    date = db.Column(db.DateTime)

class t_retweetTable(db.Model):
    retweetId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer)
    tweetId = db.Column(db.Integer)
    retweetReason = db.Column(db.String)
    date = db.Column(db.DateTime)


from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

# -------------------------
# ユーザー テーブル (User Table)
# -------------------------
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)          # 名前
    age = Column(Integer)                              # 年齢
    email = Column(String(100), unique=True)           # メールアドレス
    password = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)  # 登録日時

    posts = relationship("Post", back_populates="user")
    messages = relationship("Message", back_populates="sender")
    notifications = relationship("Notification", back_populates="user")

# -------------------------
# グループ テーブル (Group Table)
# -------------------------
class Group(Base):
    __tablename__ = "groups"

    group_id = Column(Integer, primary_key=True)
    group_name = Column(String(100), nullable=False)   # グループ名
    description = Column(Text)                         # 説明
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    members = relationship("GroupMember", back_populates="group")
    posts = relationship("Post", back_populates="group")

# -------------------------
# グループメンバー (Group Member Table)
# -------------------------
class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.group_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))

    group = relationship("Group", back_populates="members")
    user = relationship("User")

# -------------------------
# 投稿 テーブル (Post Table)
# -------------------------
class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True)
    content = Column(Text)                             # 内容
    image_url = Column(String(255))                    # 画像URL
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    group_id = Column(Integer, ForeignKey("groups.group_id"))

    user = relationship("User", back_populates="posts")
    group = relationship("Group", back_populates="posts")

# -------------------------
# メッセージ テーブル (Message Table)
# -------------------------
class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True)
    content = Column(Text)                             # 内容
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
    sender_id = Column(Integer, ForeignKey("users.user_id"))  # 送信者

    sender = relationship("User", back_populates="messages")

# -------------------------
# 通知 テーブル (Notification Table)
# -------------------------
class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True)
    message = Column(String(255))                      # 通知内容
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_read = Column(Boolean, default=False)           # 既読
    user_id = Column(Integer, ForeignKey("users.user_id"))

    user = relationship("User", back_populates="notifications")

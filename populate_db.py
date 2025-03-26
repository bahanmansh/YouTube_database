from sqlalchemy import create_engine, Table, Column, Integer, String, Date, MetaData, ForeignKey
from sqlalchemy.orm import sessionmaker
from faker import Faker
import random

# Создание базы данных
engine = create_engine('sqlite:///youtube.db', echo=True)
metadata = MetaData()

user_profile = Table('user_profile', metadata,
                     Column('user_id', Integer, primary_key=True),
                     Column('first_nm', String),
                     Column('last_nm', String))

video = Table('video', metadata,
              Column('video_id', Integer, primary_key=True),
              Column('user_id', Integer, ForeignKey('user_profile.user_id')),
              Column('date_created', Date),
              Column('category', String),
              Column('view_cnt', Integer))

comment = Table('comment', metadata,
                Column('comment_id', Integer, primary_key=True),
                Column('user_id', Integer, ForeignKey('user_profile.user_id')),
                Column('video_id', Integer, ForeignKey('video.video_id')),
                Column('date_created', Date))

video_playlist = Table('video_playlist', metadata,
                       Column('video_id', Integer, ForeignKey('video.video_id')),
                       Column('playlist_id', Integer, ForeignKey('playlist.playlist_id')),
                       Column('date_added', Date),
                       Column('date_deleted', Date))

playlist = Table('playlist', metadata,
                 Column('playlist_id', Integer, primary_key=True),
                 Column('user_id', Integer, ForeignKey('user_profile.user_id')),
                 Column('view_cnt', Integer))

liked_videos = Table('liked_videos', metadata,
                     Column('user_id', Integer, ForeignKey('user_profile.user_id')),
                     Column('video_id', Integer, ForeignKey('video.video_id')))

saved_playlists = Table('saved_playlists', metadata,
                        Column('user_id', Integer, ForeignKey('user_profile.user_id')),
                        Column('playlist_id', Integer, ForeignKey('playlist.playlist_id')))

watch_later = Table('watch_later', metadata,
                    Column('user_id', Integer, ForeignKey('user_profile.user_id')),
                    Column('date_added', Date))

advertisement = Table('advertisement', metadata,
                      Column('ad_id', Integer, primary_key=True),
                      Column('user_id', Integer, ForeignKey('user_profile.user_id')),
                      Column('preferred_ad_type', String))

metadata.create_all(engine)

# Генерация данных
fake = Faker()
Session = sessionmaker(bind=engine)
session = Session()

# Создание пользователей
users = []
for _ in range(100):
    user = {
        'first_nm': fake.first_name(),
        'last_nm': fake.last_name()
    }
    result = session.execute(user_profile.insert().values(user))
    users.append(result.inserted_primary_key[0])

# Создание видео
categories = ['music', 'sports', 'news', 'entertainment', 'education']
for _ in range(300):
    video_data = {
        'user_id': random.choice(users),
        'date_created': fake.date_between(start_date='-10y', end_date='today'),
        'category': random.choice(categories),
        'view_cnt': random.randint(0, 100000)
    }
    session.execute(video.insert().values(video_data))

# Создание комментариев
video_ids = [row[0] for row in session.execute(video.select()).fetchall()]
for _ in range(500):
    comment_data = {
        'user_id': random.choice(users),
        'video_id': random.choice(video_ids),
        'date_created': fake.date_between(start_date='-10y', end_date='today')
    }
    session.execute(comment.insert().values(comment_data))

# Создание плейлистов
for _ in range(50):
    playlist_data = {
        'user_id': random.choice(users),
        'view_cnt': random.randint(0, 10000)
    }
    result = session.execute(playlist.insert().values(playlist_data))
    playlist_id = result.inserted_primary_key[0]

    for _ in range(random.randint(1, 10)):
        video_playlist_data = {
            'video_id': random.choice(video_ids),
            'playlist_id': playlist_id,
            'date_added': fake.date_between(start_date='-10y', end_date='today'),
            'date_deleted': fake.date_between(start_date='-10y', end_date='today') if random.choice([True, False]) else None
        }
        session.execute(video_playlist.insert().values(video_playlist_data))

# Создание лайков
for _ in range(200):
    liked_videos_data = {
        'user_id': random.choice(users),
        'video_id': random.choice(video_ids)
    }
    session.execute(liked_videos.insert().values(liked_videos_data))

# Создание сохраненных плейлистов
playlist_ids = [row[0] for row in session.execute(playlist.select()).fetchall()]
for _ in range(100):
    saved_playlists_data = {
        'user_id': random.choice(users),
        'playlist_id': random.choice(playlist_ids)
    }
    session.execute(saved_playlists.insert().values(saved_playlists_data))

# Создание "посмотреть позже"
for _ in range(100):
    watch_later_data = {
        'user_id': random.choice(users),
        'date_added': fake.date_between(start_date='-5y', end_date='today')
    }
    session.execute(watch_later.insert().values(watch_later_data))

# Создание рекламы
for _ in range(50):
    advertisement_data = {
        'user_id': random.choice(users),
        'preferred_ad_type': random.choice(categories)
    }
    session.execute(advertisement.insert().values(advertisement_data))

session.commit()
session.close()

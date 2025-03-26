import pytest
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Date, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

@pytest.fixture(scope='module')
def db_engine():
    engine = create_engine('sqlite:///:memory:', echo=True)
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
    return engine

@pytest.fixture(scope='function')
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

def test_users_uploaded_videos_between_2013_2016(db_session):
    result = db_session.execute(text("""
        select user_id, first_nm, last_nm
        from (
            select distinct user_profile.user_id, first_nm, last_nm
            from (
                select *
                from video
                where date_created between date('2013-01-01') and date('2016-01-01')
            ) as vd
            join user_profile on vd.user_id = user_profile.user_id
        ) user_upload
    """)).fetchall()
    assert len(result) == 0

def test_users_commented_videos_between_2013_2016(db_session):
    result = db_session.execute(text("""
        select user_id, first_nm, last_nm
        from (
            select distinct user_profile.user_id, first_nm, last_nm
            from (
                select *
                from comment
                where date_created between date('2013-01-01') and date('2016-01-01')
            ) as cm
            join user_profile on cm.user_id = user_profile.user_id
        )
    """)).fetchall()
    assert len(result) == 0

def test_users_modified_playlist_between_2013_2016(db_session):
    result = db_session.execute(text("""
        select user_id, first_nm, last_nm
        from (
            select distinct user_profile.user_id, first_nm, last_nm
            from (
                (
                    select distinct playlist_id
                    from video_playlist
                    where date_added between date('2013-01-01') and date('2016-01-01')
                    or date_deleted between date('2013-01-01') and date('2016-01-01')
                ) pid
                join playlist on pid.playlist_id = playlist.playlist_id
            ) upid
            join user_profile on upid.user_id = user_profile.user_id
        )
    """)).fetchall()
    assert len(result) == 0

def test_users_liked_videos_between_2016_2018(db_session):
    result = db_session.execute(text("""
        select user_id, first_nm, last_nm
        from (
            select distinct user_profile.user_id, first_nm, last_nm
            from (
                select *
                from liked_videos
                join video on liked_videos.video_id = video.video_id
                where video.date_created between date('2016-01-01') and date('2018-12-31')
            ) as lv
            join user_profile on lv.user_id = user_profile.user_id
        ) user_likes
    """)).fetchall()
    assert len(result) == 0

def test_users_saved_playlists_with_high_views(db_session):
    result = db_session.execute(text("""
        select user_id, first_nm, last_nm
        from (
            select distinct user_profile.user_id, first_nm, last_nm
            from (
                select *
                from saved_playlists
                join playlist on saved_playlists.playlist_id = playlist.playlist_id
                where playlist.view_cnt > 1000
            ) as sp
            join user_profile on sp.user_id = user_profile.user_id
        ) user_playlists
    """)).fetchall()
    assert len(result) == 0

def test_users_watched_music_videos_more_than_100_times(db_session):
    result = db_session.execute(text("""
        select user_id, first_nm, last_nm
        from (
            select distinct user_profile.user_id, first_nm, last_nm
            from (
                select user_id, count(video_id) as video_count
                from video
                where category = 'music'
                group by user_id
                having count(video_id) > 100
            ) as music_videos
            join user_profile on music_videos.user_id = user_profile.user_id
        ) music_lovers
    """)).fetchall()
    assert len(result) == 0

def test_users_commented_on_sports_videos(db_session):
    result = db_session.execute(text("""
        select user_id, first_nm, last_nm
        from (
            select distinct user_profile.user_id, first_nm, last_nm
            from (
                select *
                from comment
                join video on comment.video_id = video.video_id
                where video.category = 'sports'
            ) as sports_comments
            join user_profile on sports_comments.user_id = user_profile.user_id
        ) sports_commenters
    """)).fetchall()
    assert len(result) == 0

def test_users_updated_watch_later_list(db_session):
    result = db_session.execute(text("""
        select user_id, first_nm, last_nm
        from (
            select distinct user_profile.user_id, first_nm, last_nm
            from (
                select distinct user_id
                from watch_later
                where date_added between date('2019-01-01') and date('2020-01-01')
            ) as wl
            join user_profile on wl.user_id = user_profile.user_id
        ) watch_later_updates
    """)).fetchall()
    assert len(result) == 0

def test_users_targeted_by_music_ads_and_active_last_month(db_session):
    result = db_session.execute(text("""
        select user_id, first_nm, last_nm
        from (
            select distinct user_profile.user_id, first_nm, last_nm
            from (
                select *
                from advertisement
                where preferred_ad_type = 'music'
            ) as ads
            join user_profile on ads.user_id = user_profile.user_id
        ) targeted_ads
    """)).fetchall()
    assert len(result) == 0

def test_users_with_playlists_containing_popular_videos(db_session):
    result = db_session.execute(text("""
        select user_id, first_nm, last_nm
        from (
            select distinct user_profile.user_id, first_nm, last_nm
            from (
                select distinct playlist_id
                from video_playlist
                join video on video_playlist.video_id = video.video_id
                where video.view_cnt > 10000
            ) as popular_videos
            join playlist on popular_videos.playlist_id = playlist.playlist_id
            join user_profile on playlist.user_id = user_profile.user_id
        ) popular_playlist_owners
    """)).fetchall()
    assert len(result) == 0

if __name__ == '__main__':
    pytest.main()

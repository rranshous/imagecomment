#!/bin/env python

import models as m; m.setup()
from datetime import datetime, timedelta
import os
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.s3.bucket import Bucket

conn = None

def get_bucket(conn):
    bucket = Bucket(connection=conn,
             name='ranshousweddingphotos')
    return bucket

def connect_s3():
    global conn
    if not conn:
        with open('./s3_creds.txt') as fh:
            lines = fh.readlines()
            key = lines[0].strip()
            secret = lines[1].strip()
        conn = S3Connection(key,secret)
    return conn

def run():

    # go through the media which was updated
    # more than 20 min ago and upload to s3

    top = datetime.now() - timedelta(minutes=20)
    medias = m.Media.query.filter(m.Media.created_at<top).all()

    print 'medias: %s' % len(medias)

    for media in medias:

        print 'media: %s' % media.media_path

        # find it on the drive
        if not os.path.exists(media.media_path):
            print 'doesnt exist'
            # woops
            continue

        s3_url = upload_to_s3(media.media_path)
        media.cdn_media_path = s3_url

    # get rid of local file
    os.unlink(media.media_path)
    # get rid of the media path
    media.media_path = None

    # and save
    m.session.commit()

def upload_to_s3(local_path):
    conn = connect_s3()
    bucket = get_bucket(conn)

    print 'uploading'

    key = Key(bucket)
    key.key = get_s3_name(local_path)
    key.set_contents_from_filename(local_path)
    key.set_acl('public-read')

    print 'key: %s' % key.key

    s3_url = 'https://s3.amazonaws.com/ranshousweddingphotos/%s' % key.key

    return s3_url

def get_s3_name(path):
    n = os.path.basename(path)
    n.replace('_','')
    name = 'media/%s' % n
    return name

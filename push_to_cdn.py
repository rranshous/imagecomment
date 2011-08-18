#!/usr/bin/python

import sys

if 'production' in sys.argv:
    import wsgi_entry
else:
    import cherryapp
    cherryapp.setup()

import models as m;
from datetime import datetime, timedelta
import os
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.s3.bucket import Bucket

conn = None

TIME_DELTA = 1

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

    top = datetime.now() - timedelta(minutes=TIME_DELTA)
    medias = m.Media.query.filter(m.Media.created_at<top).filter(m.Media.cdn_media_path==None).all()

    # enable s3 uploading
    m.S3Data.enabled = True

    for media in medias:

        print 'media: %s' % media.id


        # if we haven't uploaded this guy to s3 yet
        for data in media.datas_info:
            print 'data: %s' % data.label
            if not data.s3_key:
                print 'uploading'
                _data = data.get_data()
                m.S3Data.set_data(data,_data)

            # now we can get rid of our local hdd file
            print 'deleting local'
            m.DriveData.delete(data,deep=False)

            # and save
            m.session.commit()

if __name__ == '__main__':
    run()

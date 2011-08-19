from elixir import *
import datetime
import cherrypy
from hashlib import sha1, md5
from tempfile import NamedTemporaryFile
import models as m
import os
from subprocess import call
import lib.exceptions as e
from cStringIO import StringIO
from PIL import Image
from base64 import b64encode,b64decode

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.s3.bucket import Bucket

## helper functions ##
def add_tag_by_name(self,name):
    tag = Tag.get_by(name=name)
    if not tag:
        tag = Tag(name=name)
        session.add(tag)
    if tag not in self.tags:
        self.tags.append(tag)

def reset_session():
    try:
        session.rollback()
        session.expunge_all()
        session.remove()
    except:
        pass
    return

def setup():
    metadata.bind = cherrypy.config.get('db_url')
    cherrypy.log('config bind: %s' % metadata.bind)
    with open('mysql_creds.txt','r') as fh:
        lines = fh.readlines()
        username = lines[0].strip()
        password = lines[1].strip()
    metadata.bind.echo = False
    setup_all()

## end helper functions ##



# for now
BaseEntity = Entity

class Data(Entity):
    """
    obj for describing the attributes of data stored
    via the data helper
    """

    using_options(tablename='datas_info')

    size = Field(Float) # in bytes
    data_hash = Field(Text)
    label = Field(Text)
    obj = ManyToOne('DataEnabler')

    repopulate = True  # if a super has the data and we dont
                       # should we save it ?

    def set_data(self,data,deep=True):
        self.size = len(data)
        cherrypy.log('set_data size: %s' % self.size)
        self.data_hash = self.generate_hash(data)
        cherrypy.log('set_data hash: %s' % self.data_hash)
        return True

    def get_data(self,chunked=False):
        return None

    def delete(self,deep=True):
        """
        deletes the data
        """
        return True

    def compare_data(self,data):
        """
        returns true if you passed the same data as this
        is refering to already
        """
        return self.generate_hash(data) == self.data_hash

    @classmethod
    def generate_hash(cls,data):
        """
        returns the unique id of the passed data
        """

        # we are going to hash the data to name it, that way repeat
        # data isn't duplicated. Need to be careful when deleting
        # data
        h = md5()
        h.update(data)
        unique = h.hexdigest()
        return unique





class S3Data(Data):

    enabled = False

    using_options(inheritance='multi')

    s3_key = Field(UnicodeText)

    repopulate = True

    def set_data(self,data,deep=True):

        # hit the rent up
        if deep:
            super(S3Data,self).set_data(data)
        else:
            Data.set_data(self,data,deep)

        cherrypy.log('s3 data set_data')

        if not self.enabled:
            cherrypy.log('s3 not enabled, skipping')
            return False

        # upload the data to s3
        key = self.get_key()

        cherrypy.log('uploading')

        # TODO: pass our computed hashes so it doesnt re-hash
        # TODO: don't set if they key aleady exists
        key.set_contents_from_string(data)

        # save it's key
        self.s3_key = key.key

        return True

    def get_data(self,chunked=False):
        cherrypy.log('S3data get_data')
        key = self.get_key()

        # see if the key / data exists
        if not key.exists():
            # doesn't exist, see if our super has it
            data = super(S3Data,self).get_data(chunked)

            # if we're chunked what we get back is going to be a generator
            if chunked:
                def stream_data():
                    # if we are going to repopulate we need a container
                    if S3Data.repopulate:
                        buffered_data = ''

                    # grab / yield up the data pieces
                    try:
                        while True:
                            # grab the next value
                            p = data.next()

                            # since we are repopulating we need to hold the data
                            if S3Data.repopulate:
                                buffered_data += p

                            # return back our piece of data
                            yield p

                    except StopIteration:
                        # we've run out of data
                        # if we're supposed to repop do so
                        if buffered_data and S3Data.repopulate:
                            S3Data.set_data(self,buffered_data,False)

                        # and we're done, so raise our StopIteration
                        raise
                return stream_data

            # we're not chunking, data is data
            else:
                # if we're supposed to repop do so
                if data and S3Data.repopulate:
                    S3Data.set_data(self,data,False)

                return data

        # we have the data! lets get it
        else:
            if chunked:
                def stream_data():
                    cherrypy.log('S3Data returning in chunks')
                    # we want to read the data in chunks
                    for p in key:
                        yield p
                return stream_data
            else:
                # grab the data from s3
                data = key.get_contents_as_string()


    def delete(self,deep=True):
        if deep:
            super(S3Data,self).delete(deep)
        key = self.get_key()
        key.delete()
        self.s3_key = None

    def get_bucket(self,conn):
        if not hasattr(self,'s3_bucket') or not self.s3_bucket:
            self.s3_bucket = Bucket(connection=conn,
                                    name=cherrypy.config.get('s3_bucket_name'))
        return self.s3_bucket

    def connect_s3(self):
        if not hasattr(self,'s3_conn') or not self.s3_conn:
            self.s3_conn = S3Connection(cherrypy.config.get('s3_key'),
                                        cherrypy.config.get('s3_secret'))
        return self.s3_conn

    def get_key(self):
        conn = self.connect_s3()
        bucket = self.get_bucket(conn)
        key = Key(bucket)
        if self.s3_key:
            key.key = self.s3_key
        return key


class DriveData(S3Data):
    """
    Info on data stored by the DataEnabler
    """

    using_options(inheritance='multi')

    local_save_path = Field(UnicodeText)

    repopulate = False

    def set_data(self,data,deep=True):
        """
        set the file data
        """
        # do we want to set deeper?
        if deep:
            super(DriveData,self).set_data(data)
        else:
            Data.set_data(self,data,deep)

        cherrypy.log('drive data set_data')

        # now we need to save it to the disk
        # use it's hash to save it down, that way repeat data
        # will not be repeated in storage
        path = os.path.join(cherrypy.config.get('media_root'),
                            self.data_hash)

        with open(path,'wb') as fh:
            cherrypy.log('set_data writing: %s' % path)
            fh.write(data)
            fh.close()
            self.local_save_path = path

        return True

    def get_data(self,chunked=True):
        """
        return the file data
        """

        cherrypy.log('drivedata get_data')

        # check and see if we have the data
        if not self.local_save_path or not os.path.exists(self.local_save_path):

            # nope didn't have the data
            cherrypy.log('drivedata path not found')

            # dig deeper
            data = super(DriveData,self).get_data(chunked=chunked)

            # is data a generator?
            if chunked:
                def stream_data():
                    if DriveData.repopulate:
                        buffered_data = ''
                    try:
                        while True:
                            p = data.next()
                            if DriveData.repopulate:
                                buffered_data += p
                            yield p
                    except StopIteration:
                        # someone knew better than me!
                        if data and DriveData.repopulate:
                            DriveData.set_data(self,buffered_data,False)
                        raise
                return stream_data

            # data is not a generator
            else:
                if data and DriveData.repopulate:
                    DriveData.set_data(self,buffered_data,False)

        else:
            cherrypy.log('get_data: %s' % self.local_save_path)
            if chunked:
                def stream_data():
                    cherrypy.log('drivedata returning chunks')
                    with open(self.local_save_path,'r') as fh:
                        for p in fh.read(self.BUFFER_SIZE):
                            yield p
                return stream_data
            else:
                with open(self.local_save_path,'r') as fh:
                    data = fh.read()

        return data


    def delete(self,deep=True):
        if deep:
            super(DriveData,self).delete(deep)
        cherrypy.log('DriveData delete')

        if self.local_save_path and os.path.exists(self.local_save_path):
            os.unlink(self.local_save_path)
            self.local_save_path = None


class MemcacheData(DriveData):

    repopulate = True

    def set_data(self,data,deep=True):
        from lib.memcache_client import memcache_client

        # respect ur eldurs
        if deep:
            super(MemcacheData,self).set_data(data)
        else:
            Data.set_data(self,data,deep)

        cherrypy.log('memcache data set_data: %s' % self.data_hash)

        # we are b64ing the data for consistency
        memcache_client.set(str(self.data_hash),
                            b64encode(data))

        return True

    def get_data(self,chunked=False):
        from lib.memcache_client import memcache_client

        cherrypy.log('memcache data get_data: %s' % self.data_hash)

        # check and see if we have it
        data = memcache_client.get(str(self.data_hash))

        if not data:
            cherrypy.log('memcache not found')
            data = super(MemcacheData,self).get_data()

            # data may be a generator
            if chunked:
                def stream_data():
                    if MemcacheData.repopulate:
                        buffered_data = ''
                    try:
                        while True:
                            p = data.next()
                            if MemcacheData.repopulate:
                                buffered_data += p
                            yield p
                    except StopIteration:
                        if buffered_data and MemcacheData.repopulate:
                            cherrypy.log('memcachedata repopulating')
                            MemcacheData.set_data(self,buffered_data,False)
                        raise
                return stream_data

            # data is not a generator
            else:
                if data and MemcacheData.repopulate:
                    cherrypy.log('memcachedata repopulating')
                    MemcacheData.set_data(self,data,False)
                return data

        # we have the data
        else:
            # since we can't really chunk we fake it
            if chunked:
                def stream_data():
                    yield b64decode(data)
                return stream_data
            else:
                return b64decode(data)

    def delete(self,deep=True):
        if deep:
            super(MemcacheData,self).delete(deep)
        from lib.memcache_client import memcache_client
        cherrypy.log('memcache delete')
        memcache_client.delete(self.data_hash)


class DataEnabler(BaseEntity):
    """
    to be subclassed. facilitates setting / getting obj data.
    Data can be set or got by label, not name. For example
    a media obj may have source image as well as thumbnail.
    you could set the default data as the source image data
    and than the thumbnail datas as 'thumbnail_[size]' label.
    """

    datas_info = OneToMany('Data')

    DATA_TYPE = None

    def set_data(self,file_data,label='default'):
        """
        sets the obj's data w/ the given label. If it is already
        set the old data will be lost and the new data will be set
        """
        # try and find existing info
        data = self.find_data(label)

        cherrypy.log('DataEnabler set_data: %s' % label)

        # check and see if the info is for the same data
        if not data or not data.compare_data(file_data):
            cherrypy.log('adding data entry')

            # they are not the same data, we need to create
            # a new info for our data
            data = self.DATA_TYPE(label=label)
            data.set_data(file_data)
            self.datas_info.append(data)
            session.add(data)

        else:
            cherrypy.log('skipping set, same data')

        return data

    def get_data(self,label='default',chunked=False):
        """
        gets the obj's data. If no data is found returns None.
        """

        cherrypy.log('DataEnabler get_data: %s' % label)

        # find the data
        data = self.find_data(label)

        # if we didn't find it return none
        if not data:
            cherrypy.log('DataEnabler did not find data entry')
            return None

        # return the data
        if chunked:
            cherrypy.log('DataEnabler returning in chunks')
            # they want us to generate up the pieces
            return data.get_data(chunked=True)

        else:
            # they just want their data all at once
            _data = data.get_data()
            if len(_data) != data.size:
                cherrypy.log('wrong size found: %s %s'
                             % (len(_data),data.size))
            return _data

    def find_data(self,label):
        """
        returns the Data for this obj by the given label
        """
        return self.DATA_TYPE.query.\
                             filter(self.DATA_TYPE.obj==self).\
                             filter(self.DATA_TYPE.label==label).\
                             first()



class User(BaseEntity):
    using_options(tablename='users')

    # users "name"
    handle = Field(Unicode(75))
    handle.public = True
    # url of their avatar
    avatar_url = Field(UnicodeText)
    avatar_url.public = True
    # hash of password
    password_hash = Field(UnicodeText)
    # email address
    email_address = Field(Unicode(120))

    # admin bool flag
    is_admin = Field(BOOLEAN(False))

    media = OneToMany('Media')
    comments = OneToMany('Comment')
    albums = OneToMany('Album')

    def set_password(self,p):
        """ sets users password hash based on passed string """
        self.password_hash = self.create_password_hash(p)

    password = property(lambda a: a.password_hash,
                        set_password)

    @classmethod
    def create_password_hash(cls,p):
        """ returns back hashed version of password """
        return sha1(p).hexdigest()

    def get_tags(self):
        tags = Tag.query.join('media').filter(Media.user==self).all()
        return tags


class Tag(BaseEntity):
    using_options(tablename='tags')

    name = Field(Unicode(100))
    created_at = Field(DateTime, default=datetime.datetime.now)

    media = ManyToMany('Media')
    relates_to = ManyToMany('Tag')
    comments = ManyToMany('Comment')
    albums = ManyToMany('Album')

    def __repr__(self):
        return '<Tag "%s">' % self.name

class Album(BaseEntity):
    using_options(tablename='albums')

    name = Field(Unicode(100))
    created_at = Field(DateTime, default=datetime.datetime.now)

    comments = OneToMany('Comment')
    media = ManyToMany('Media')
    tags = ManyToMany('Tag')
    owner = ManyToOne('User')
    relates_to = ManyToMany('Album')

    add_tag_by_name = add_tag_by_name

    def __repr__(self):
        return '<Album "%s">' % self.name

class Comment(BaseEntity):
    using_options(tablename='comments')

    title = Field(Unicode(100))
    rating = Field(Integer)
    content = Field(UnicodeText)
    created_at = Field(DateTime, default=datetime.datetime.now)

    media = ManyToOne('Media')
    user = ManyToOne('User')
    tags = ManyToMany('Tag')
    album = ManyToOne('Album')

    add_tag_by_name = add_tag_by_name

    def __repr__(self):
        return '<Comment "%s" "%s">' % (self.title,self.rating)

class Media(DataEnabler):
    using_options(tablename='media')

    DATA_TYPE = MemcacheData

    title = Field(Unicode(100))
    size = Field(Float)
    type = Field(Unicode(80))
    extension = Field(Unicode(10))
    created_at = Field(DateTime, default=datetime.datetime.now)

    comments = OneToMany('Comment')
    tags = ManyToMany('Tag')
    user = ManyToOne('User')
    albums = ManyToMany('Album')

    add_tag_by_name = add_tag_by_name


    def create_thumbnail(self,w,h='',overwrite=False):
        cherrypy.log('creating thumbnail')
        if self.is_image():

            # figure out it's dimensions
            w,h = map(str,(w,h))
            if not h:
                h = w
            if 'x' in w:
                size = w
            else:
                size = '%sx%s' % (w,h)

            size_tuple = int(w), int(h) if h else None

            cherrypy.log('creating thumbnail: %s:%s' % size_tuple)

            # label pattern for retrieving the data
            data_label = 'thumbnail_%s' % size

            # try and get the data
            data = self.get_data(data_label)

            if data:
                # easy peasy
                return data

            cherrypy.log('thumnail does not exist')

            # woops didn't find the data for the thumbnail, we'll gen one
            source_data = self.get_data()
            if not source_data:
                raise e.ValidationException('Data for media not found')

            # create our thumbnail
            data_buffer = StringIO(source_data)
            image = Image.open(data_buffer)
            image.thumbnail(size_tuple, Image.ANTIALIAS)
            data_buffer.close()
            out_buffer = StringIO()
            image.save(out_buffer, format='JPEG')
            thumbnail_data = out_buffer.getvalue()
            out_buffer.close()

            # save it's data for later
            self.set_data(thumbnail_data,data_label)

            return thumbnail_data

    @classmethod
    def get_random_path(cls):
        # we are going to pick a random name off the root path
        root_path = cherrypy.config.get('media_root')
        temp_file = NamedTemporaryFile(delete=False,dir=root_path)
        return temp_file.name

    def set_tags(self,tags):
        """ cheating """
        self.tags = []
        for tag in tags:
            self.add_tag_by_name(tag)


    def add_tag_by_name(self,name):
        tag = Tag.get_by(name=name)
        if not tag:
            tag = Tag(name=name)
            session.add(tag)
        if tag not in self.tags:
            self.tags.append(tag)

    def get_safe_title(self):
        title = self.title or self.id
        title.replace(' ','_').replace('\n','_').strip()
        return '%s.%s' % (title,self.extension)

    def is_image(self):
        image_extensions = ('jpg','png','gif','jpeg')
        for e in image_extensions:
            if self.extension.lower() == e:
                return True
        return False

    def is_video(self):
        video_extensions = ('avi','mpeg','mpg','mp4','mov')
        for e in video_extensions:
            if self.extension.lower() == e:
                return True
        return False

    @classmethod
    def validate_form_data(cls,title=None,file_data=None,comment=None,
                           rating=None,tags=None,
                           album_id=None,album_name=None,ignore_file=False):
        """ raises validation exception if something is not valid
            returns file data objects """

        # comment can ride
        comment = unicode(comment)

        # tags can ride also

        # album id must be a valid album
        if album_id and not m.Album.get(album_id):
            cherrypy.log('album_id: %s' % album_id)
            raise e.ValidationException('error','album not found!')

        # if there isn't an album id than there needs to be an album name
        if not album_id and not album_name:
            raise e.ValidationException('error','media must have album')

        # must have a title!
        if not title:
            raise e.ValidationException('error','title required!')

        # can't create a media entry w/o data!
        if not ignore_file:
            if (isinstance(file_data,list) and not file_data) or \
               (not isinstance(file_data,list) and not file_data.filename):
                print 'file_data:',file_data
                raise e.ValidationException('error','must upload file!')

        # we might be getting multiple files
        if not isinstance(file_data,list):
            file_data = [file_data]

        # legit ratings only!
        if rating and not rating.isdigit() or 0> int(rating) >5:
            raise e.ValidationException('error','invalid rating!')


        return file_data

    def __repr__(self):
        return '<Media "%s" %s">' % (self.title,self.type)




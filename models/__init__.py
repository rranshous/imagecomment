from elixir import *
import datetime

def setup():
    metadata.bind = "sqlite:///dbs/media.db"
    metadata.bind.echo = True
    setup_all()

class User(Entity):
    using_options(tablename='users')

    handle = Field(Unicode(75))
    avatar_url = Field(UnicodeText)
    password_hash = Field(UnicodeText)

class Tag(Entity):
    using_options(tablename='tags')

    name = Field(Unicode(100))
    description = Field(UnicodeText)
    created_at = Field(DateTime, default=datetime.datetime.now)

    media = ManyToMany('Media')
    relates_to = ManyToMany('Tag')

    def __repr__(self):
        return '<Tag "%s">' % self.name

class Comment(Entity):
    using_options(tablename='comments')

    title = Field(Unicode(100))
    rating = Field(Integer)
    content = Field(UnicodeText)
    created_at = Field(DateTime, default=datetime.datetime.now)

    media = ManyToOne('Media')

    def __repr__(self):
        return '<Comment "%s" "%s">' % (self.title,self.rating)

class Media(Entity):
    using_options(tablename='media')

    title = Field(Unicode(100))
    size = Field(Float)
    type = Field(Unicode(10))
    created_at = Field(DateTime, default=datetime.datetime.now)

    comments = OneToMany('Comment')
    tags = ManyToMany('Tag')

    def __repr__(self):
        return '<Media "%s" %s">' % (self.title,self.media_type)


## we want to build a simple gui which facilitates batch uploads
## and easy multi upload

from easygui import *

def log_in():
    """
    prmopts for username and password and than logs
    into the site
    """

    # get credentials
    handle = enterbox("What's your name?")
    password = passwordbox("Password?")

    return handle,password


def multi_upload(root):
    """
    presents each of the JPGs under the root argument
    for upload args and than uploads them in sequential order
    """

    print 'multi upload: %s' % root

    # have them enter the album name
    album_name = enterbox('Enter the album name')

    print 'album_name: %s' % album_name

    # go through all the images from root
    for path in find_files(root,extension="jpg"):

        name = os.path.basename(path)

        # get the name
        name = enterbox("What's it's name?",
                        name,
                        default=name,
                        image=path)

        # throw up the multibox for info
        comment = enterbox("What's your comment?",
                           name,
                           image=path)

        # upload that bitch
        upload_image(path=path,
                     comment=comment,
                     album=album)


def upload_image(path=path,comment=comment,album=album):
    """
    logs you in if you are not, uploads an image
    """

    # make sure we're logged in
    log_in()

    # read in our media
    with open(path,'r') as fh:
        file_data = fh.read()

    # post to the media upload
    post('%s/media/create',
         title=title,
         file_data=file_data,
         album_name=album,
         action='POST',
         comment=comment)


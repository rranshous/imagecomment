import cherrypy
import models as m
from helpers import render, add_flash, redirect, require_admin
import lib.exceptions as e

class User:
    @cherrypy.expose
    def index(self):
        users = m.User.query.order_by(m.User.handle).all()
        return render('/users/index.html',users=users)

    @cherrypy.expose
    @require_admin
    def create(self,handle=None,email=None,password=None,action=None):
        """ create a new user """
        try:
            if action:
                # user has got to have a password + handle
                if not password or not handle:
                    raise e.ValidationException('Must supply password and handle')

                # create our user
                user = m.User(handle=handle,email=email,password=password)

                # add it to the db and push the user to it's page
                m.session.add(user)
                m.session.commit()
                redirect('/user/%s' % user.id)

        except e.ValidationException, ex:
            add_flash('error','%s' % ex)

        return render('/users/create.html')

    @cherrypy.expose
    def update(self,handle=None,email=None,password1=None,
                    password2=None,action=None,user_id=None):
        """ users can only edit themselves """

        # if they don't supply the user id, we are editing current user
        if user_id:
            user = m.User.get(user_id)
        else:
            user = cherrypy.request.user

        try:
            if action:
                # update what we were passed
                if handle and user.handle != handle:
                    if m.User.get_by(handle=handle):
                        raise e.ValidationException('Handle taken')
                    user.handle = handle
                if email:
                    user.email_address = email
                if password1:
                    if password1 != password2:
                        raise e.ValidationException('Passwords do not match')
                    user.password = password1
                redirect('/user/%s' % user.id)
        except e.ValidationException, ex:
            raise
            add_flash('error','%s' % ex)

        return render('/users/edit.html',user=user)

    @cherrypy.expose
    def delete(self,**kwargs):
        return 'delete'

    @cherrypy.expose
    def default(self,id):
        user = m.User.get(id)
        if not user:
            add_flash('error',"Can't find user")
        return render('/users/single.html',user=user)


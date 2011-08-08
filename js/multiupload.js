// create a class which can async upload files

Ext.override(Ext.Element, {
    cascade: function(fn,scope,args) {
        if(fn.apply(scope || this.args || [this]) !== false) {
            var cs = this.dom.childNodes;
            var len = cs.len;
            for(var i = 0; i < len; i++) {
                Ext.get(cs[i]).cascade(fn, scope, args);
            }
        }
    },
    clone: function() {
        var result = this.el.dom.cloneNode(true);
        result.id = Ext.id();
        result = Ext.get(result);
        result.cascade(function(e){e.id = Ext.id();});
    }
});

MultiUploader = function(config) {

    // the target form should contain the fields for
    // one file and it's meta data including a submit button
    // the fields / submit will stay, an additional button
    // for adding another set of fields will be added to the
    // form, the submit button will be re-mapped to upload
    // the single field set's data. this should degrade gracefully
    // if there is no javascript in the browser.
    // w/e the request to submit the form returns is
    // used to replace the inputs which were submitted.

    // there should be a button for adding another field set
    // named add_fieldset. this will be unhiden (if hidden)
    // when the form is initialized by this class

    this.ADD_SET_NAME = 'add_fieldset';
    this.ADD_SET_CONTAINER_ID = 'add_fieldset_container';
    this.FIELD_CONTAINER_CLASS = 'form_container';
    this.FAILURE_MESSAGE = 'Upload Failed!';
    this.SUBMIT_MESSAGE = 'Uploading..';

    this.target_form = Ext.get(config.target_form);

    this.init();

};

MultiUploader.prototype = {

init: function() {
    // initialize the form, unhiding the add fieldset button,
    // remapping the submit button to async submit
    // wrapping the fields in a div so that we can create field
    // sets
    //
    
    // grab the div containing the fields in the form
    this.form_container = Ext.get(Ext.query('.'+this.FIELD_CONTAINER_CLASS)[0]);
    this.form_container.dom.id = null;

    // create an hidden copy of the container for replication later
    this.container_template = this.form_container.dom.cloneNode(true);
    console.log({container_template:this.container_template});

    // update the add set button so that when clicked it
    // inserts another field set
    var add_container = Ext.get('add_fieldset_container');
    var add_container_button = Ext.get(add_container.down('button'));
    this.wrap_add_set(add_container_button);

    // we need to setup the add set and submit buttons
    // change the submit button to be an async submit
    var submit_button = Ext.get(this.form_container.query('input[type=submit]')[0]);
    if(Ext.isEmpty(submit_button)) {
        submit_button = this.form_container.down('button[type=submit]');
    }
    console.log({submit_button:submit_button});
    this.wrap_submit(submit_button,this.form_container);

},

wrap_add_set: function(button) {
    // wrap the button so that when it is clicked
    // another set of fields is added to the form
    button.removeAllListeners();
    button.on('click',this.add_set,this);
},

add_set: function() {
    var new_node = this.form_container.appendChild(this.container_template);
    this.container_template = new_node.dom.cloneNode(true);
    return new_node;
},

wrap_submit: function(button,container) {
    // we are going to get a submit button element
    // which would normally submit the form it's in.
    // we need to modify it so that when it is clicked
    // it instead calls our method which will submit it async
    button.removeAllListeners();
    button.on('click',
              this.async_submit.createDelegate(this,[container]),
              this,
              {stopEvent:true,preventDefault:true,stopPropagation:true,buffer:10});
},


async_submit: function(container) {
    // since we are submitting a file we need to use a form
    // this means we are going to create a hidden form, move
    // the contents of the container into the hidden form while putting
    // a processing message in the container. submit the new form,
    // adding the response to our request to the container

    // get the forms method / action / encoding
    var form = container.parent('form');
    var action = form.getAttribute('action');
    var method = form.getAttribute('method');
    var encoding = form.getAttribute('enctype');

    // create our new form
    var temp_form = Ext.DomHelper.append(Ext.getBody(), {
        tag:'form',
        action:action,method:method,enctype:encoding,
        style:'display:none'
    },true);

    // move our container contents to the new form
    container.select('*').each(function(el) {
        el.appendTo(temp_form);
    },this);

    // update our container w/ the submit message
    container.update(this.SUBMIT_MESSAGE);

    return;

    // submit our ajax request
    Ext.Ajax.request({
        scope: this,
        callback: this.handle_response.createDelegate(this,
                                                      [container,new_form],
                                                      true),
        timeout: 60000, // 1 minute
        form: temp_form,
        isUpload: true, // response must be text/html
        disableCaching: true
    });

},

handle_response: function(options,success,response,container,temp_form) {
    // if we got a successful response put the response text into
    // the container. if we got a failure than flash failure in the
    // container and than put the contents of the temp form back into the
    // container. either way remove the temp_form

    if(success) {
        // set our success msg + remove the temp form
        container.update(response.responseText);
        temp_form.remove();
    } else {
        // set the failure message
        container.update(this.FAILURE_MESSAGE);

        // in 3 seconds put the container content back
        // and remove the form
        (function() {
           temp_form.select('*').each(function(el) {
                el.appendTo(container);
                temp_form.remove();
           },this);
        }).defer(3000,this);
    }
}

};

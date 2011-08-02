// create a class which can async upload files

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
    this.FIELD_CONTAINER_CLASS = 'multiupload_fieldset_container';
    this.FAILURE_MESSAGE = 'Upload Failed!';
    this.SUBMIT_MESSAGE = 'Uploading..';


    this.target_form = Ext.get(config.target_form);
    console.log({target_form:this.target_form});

    this.init();

};

MultiUploader.prototype = {

init: function() {
    // initialize the form, unhiding the add fieldset button,
    // remapping the submit button to async submit
    // wrapping the fields in a div so that we can create field
    // sets

    // create our fieldset container
    var fieldset_container = Ext.DomHelper.append(Ext.getBody(),{
                                tag:'div',
                                style:'padding:0;margin:0;border:0;',
                                cls:this.FIELD_CONTAINER_CLASS
                             },true);

    var add_fieldset_container = Ext.get(this.ADD_SET_CONTAINER_ID);

    console.log({fieldset_container:fieldset_container,
                 add_fieldset_container:add_fieldset_container});

    // move everything (but add_fieldset button)
    // from the form into the new container
    var children = [];
    var last;
    divs = this.target_form.query('> div');
    Ext.each(divs, (function(el) {
        el = Ext.get(el);
        console.log({el:el});
        try {
            var name = el.getAttribute('name');
            console.log('name: '+name);
        } catch (err) { name = ''; }
        if(el.id == add_fieldset_container.id) {
            console.log('add fieldset not copied');
            return;
        }
        if(Ext.isEmpty(last)) {
            el.appendTo(fieldset_container);
            last = el;
        }
        else {
            el.insertAfter(last);
            last = el;
        }
    }));

    fieldset_container.appendTo(this.target_form);

    // create an hidden copy of the container for replication later
    this.container_template = this.copy_container(fieldset_container,
                                                  Ext.getBody());
    this.container_template.setVisibilityMode(Ext.Element.DISPLAY);
    this.container_template.hide();
    console.log({template:this.container_template,container:fieldset_container});

    // initialize the container's action buttons
    this.init_container(fieldset_container);
},

init_container: function(container) {

    console.log({container:container});

    // we need to setup the add set and submit buttons
    // change the submit button to be an async submit
    console.log({container:container});
    var submit_button = container.down('input[type=submit]');
    if(!submit_button) {
        submit_button = container.down('button[type=submit]');
    }
    this.wrap_submit(container.down('input[type=submit]'),container);

    // update the add set button so that when clicked it
    // inserts another field set
    this.wrap_add_set(container.down('button[name=add_fieldset]'));
},

wrap_add_set: function(button) {
    // wrap the button so that when it is clicked
    // another set of fields is added to the form
    button.removeAllListeners();
    button.on('click',this.add_set,this);
},

add_set: function() {
    // create a new set copy. we are going to copy the container
    // template into the form
    var copy = this.copy_container(this.container_template);

    // it also copies the fact that the template is hidden
    copy.show();

    return copy
},

wrap_submit: function(button,container) {
    // we are going to get a submit button element
    // which would normally submit the form it's in.
    // we need to modify it so that when it is clicked
    // it instead calls our method which will submit it async
    button.removeAllListeners();
    button.on('click',
              this.async_submit.createCallback(container),
              this,
              {preventDefault:true,stopPropagation:true,buffer:10});
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
},

copy_container: function(container,append_to) {
    // create a copy of the container passed
    // and append it to the second arg
    container.select('> div').each(function(el) { el.set({id:""}); },this);
    var copy = Ext.get(container.dom.cloneNode(true));
    Ext.DomHelper.append(append_to,copy);
    copy = append_to.down(':last-child');
    console.log({container:container,copy:copy})
    return copy;
}

};

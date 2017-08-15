/**
 * Copyright 2017, Le Tuan Anh (tuananh.ke@gmail.com)
 * This file is part of VisualKopasu.
 * VisualKopasu is free software: you can redistribute it and/or modify 
 * it under the terms of the GNU General Public License as published by 
 * the Free Software Foundation, either version 3 of the License, or 
 * (at your option) any later version.
 * VisualKopasu is distributed in the hope that it will be useful, but 
 * WITHOUT ANY WARRANTY; without even the implied warranty of 
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
 * See the GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License 
 * along with VisualKopasu. If not, see http://www.gnu.org/licenses/.
 **/

Yawol = function(container_id, yawol_root, synsetbox_template, local_url) {
    this._template = _.template(synsetbox_template);
    this._yawol_root = (yawol_root == undefined) ? "http://127.0.0.1:5000/yawol/" : yawol_root;
    this._container = $("#" + container_id);
}

Yawol.prototype = {
    /*
     * Load synset template box
     */
    load_template: function (template) {
        this._template = _.template(template);
        return this;
    },
    
    /* 
     * Display a synset to a synsetbox
     */
    build_synsetbox: function(synset, container) {
        container = (container == undefined) ? this._container : container;
        var sbox = $(this._template({synset: synset}));
        sbox.find('.close').click(function(){ sbox.remove(); });
        sbox.appendTo(container);
    },
    
    clear: function(container) {
        container = (container == undefined) ? this._container : container;
        container.empty();
    },
        
    /** Check server version **/
    version: function(callback, callback_error) {
        if (callback_error == undefined) {
            callback_error = log_error;
        }
        if (callback == undefined) {
            callback = {};
        }
        var url = this._yawol_root + 'version';
        $.ajax({url: url, dataType: 'jsonp'})
            .done(callback)
            .fail(callback_error);
    },
    
    /** Create a new synsetbox and display synset **/
    display_synset: function(synset, container, clear_prev) {
        container = (container == undefined) ? this._container : container;
        // Clear previous box
        if (clear_prev) {
            container.empty();
        }
        // Add a synsetbox
        this.build_synsetbox(synset, container);
    },

    
    display_synsets: function(synsets, container) {
        container = (container == undefined) ? this._container : container;
	this.clear(container);
	$.each(synsets, $.proxy(function(idx, synset){
            this.display_synset(synset, container);
        }, this));
    },
    
    /** Search synset (remote or local) **/
    search_synset: function(query, container, success, error) {
        var url = this._yawol_root + 'search/' + query;
        container = (container == undefined) ? this._container : container;
	if (success == undefined) { success = this.display_synsets; }
        if (error == undefined) { error = log_error; }
        $.ajax({
	    url: url,
	    dataType: 'jsonp',
	    success: $.proxy(function(json){
                this.display_synsets(json, container);
            }, this),
	    fail: function(jqxhr) {
                error(jqxhr, query);
            },
	    error: function(jqxhr) {
                error(jqxhr, query);
            }
	});
    }    
}

/**
 * Log error msg 
 **/
function log_error(jqxhr, query) {
    if (console != undefined && console.writeline != undefined) {
        console.writeline("Query: " + query);
        console.writeline( "Request Failed: " + jqxhr.statusText + " | Error code = " + jqxhr.status);
    }
}   

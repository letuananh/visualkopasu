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
    build_synsetbox: function(synset) {
        var sbox = $(this._template({synset: synset}));
        sbox.find('.close').click(function(){ sbox.remove(); });
        sbox.appendTo(this._container);
    },
    
    clear: function() {
        this._container.empty();
    },
        
    /** Check server version **/
    version: function(callback) {
        var url = this._yawol_root + 'version';
        // console.header("Accessing: " + url);
        $.ajax({url: url, dataType: 'jsonp'})
            .done(callback)
            .fail(log_error);
    },
    
    /** Create a new synsetbox and display synset **/
    display_synset: function(synset, clear_prev) {
        // Clear previous box
        if (clear_prev) {
            this._container.empty();
        }
        // Add a synsetbox
       this.build_synsetbox(synset);
    },

    
    display_synsets: function(synsets) {
	var self = this;
	self.clear();
	// console.writeline("Synsets received: " + synsets.length);
	$.each(synsets, function(idx, synset){
            self.display_synset(synset);
        });
    },
    
    /** Search synset (remote or local) **/
    search_synset: function(query, success) {
        var url = this._yawol_root + 'search/' + query;
	var self = this;
	if (success == undefined) { success = this.display_synsets;  }
        $.ajax({
	    url: url,
	    dataType: 'jsonp',
	    success: function(json){
		success.call(self, json);
	    },
	    fail: log_error,
	    error: log_error
	});
    }    
}

/**
 * Log error msg 
 **/
function log_error(jqxhr) {
    if (console != undefined && console.writeline != undefined) {
        console.writeline( "Request Failed: " + jqxhr.statusText + " | code = " + jqxhr.status);
    }
}   

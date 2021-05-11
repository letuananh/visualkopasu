Restisf = function(server) {
    this._server = (server == undefined) ? "http://127.0.0.1:8000/" : server;
}

Restisf.prototype = {
    generate: function(mrs, grammar, success, fail) {
        grammar = (grammar == undefined) ? 'ERG' : grammar;
        $.ajax({
            url: this._server + 'generate',
            type: "post",
            data: {
                'mrs': mrs,
	        'grammar': grammar
            },
            success: success,
            fail: function(jqxhr){
                if (console != undefined && console.writeline != undefined) {
                    console.writeline("Request Failed: " + jqxhr.statusText + " | code = " + jqxhr.status);
                }
                if (typeof fail === 'function'){
                    fail();
                }
            },
            error: function(jqxhr){
                if (console != undefined && console.writeline != undefined) {
                    console.writeline("An error occurred. Message = " + jqxhr.statusText + " | code = " + jqxhr.status);
                }
                if (typeof fail === 'function'){
                    fail();
                }
            }
        });
    },
    /**
     * Parse a sentence
     **/
    parse: function(sent, parse_count, tagger, grammar, success, fail) {
        parse_count = (parse_count == undefined) ? 5 : parse_count;
        tagger = (tagger == undefined) ? 'lelesk' : tagger;
        grammar = (grammar == undefined) ? 'ERG' : grammar;
        $.ajax({
            url: this._server + 'parse',
            dataType: 'jsonp',
            data: {
                'sent': sent,
	        'parse_count': parse_count,
	        'tagger': tagger,
	        'grammar': grammar
            },
            success: success,
            fail: function(jqxhr){
                if (console != undefined && console.writeline != undefined) {
                    console.writeline("Request Failed: " + jqxhr.statusText + " | code = " + jqxhr.status);
                }
                if (typeof fail === 'function'){
                    fail();
                }
            },
            error: function(jqxhr){
                if (console != undefined && console.writeline != undefined) {
                    console.writeline("An error occurred. Message = " + jqxhr.statusText + " | code = " + jqxhr.status);
                }
                if (typeof fail === 'function'){
                    fail();
                }
            }
        });
        // end ajax calling
    }
}

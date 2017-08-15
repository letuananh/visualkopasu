/**
 * Copyright 2017, Le Tuan Anh (tuananh.ke@gmail.com)
 * This file is part of ChibiJS project.
 * ChibiJS is free software: you can redistribute it and/or modify 
 * it under the terms of the GNU General Public License as published by 
 * the Free Software Foundation, either version 3 of the License, or 
 * (at your option) any later version.
 * ChibiJS is distributed in the hope that it will be useful, but 
 * WITHOUT ANY WARRANTY; without even the implied warranty of 
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
 * See the GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License 
 * along with ChibiJS. If not, see http://www.gnu.org/licenses/.
 **/

var Visko;

if (Visko == undefined) {
    Visko = new function() {};
    Visko.find_tag = undefined;
}

Visko.Tagged = new function() {};

Visko.Tagged.Sentence = function(surface, tokens, concepts){
    this._surface = surface;
    this._tokens = tokens;
    this._concepts = concepts;
    this._conceptObjs = [];
    this._tokenObjs = [];
    this._div = undefined;
}

Visko.Tagged.show = function(sent_json, container){
    tsent = new Visko.Tagged.Sentence(sent_json.text, sent_json.tokens, sent_json.concepts);
    if (container == undefined){
        container = "#sentences";
    }
    tsent.to_div($(container));
    return tsent;
}

Visko.Tagged.highlight_concept = function(mweid){
    if (mweid != undefined) {
        var mygroup = $(".TaggedSentence .MWE").filter(function(){
            return $(this).data('mweid') == mweid;
        });
        mygroup.toggleClass("MWEActive");
    }
}

Visko.Tagged.Sentence.prototype = {
    concepts: function(){
        return this._conceptObjs;
    },
    to_div: function(mother) {
        var self = this;
        self._div = $("<div class='TaggedSentence'>");
        // Create tokens
        self._tokenObjs = _.map(self._tokens, function(t){ return new Visko.Tagged.Token(t);});
        self._conceptObjs = [];
        // Create concepts
        _.forEach(self._concepts, function(concept){
            conceptObj = new Visko.Tagged.Concept(concept);
            self._conceptObjs.push(conceptObj);
            _.forEach(concept.words, function(widx){
                self._tokenObjs[widx].add_concept(conceptObj);
            }); // foreach word
        }); // foreach concept
        
        // add tokens to sentence
        _.forEach(self._tokenObjs, function(tokenObj){
            self._div.append(tokenObj.to_span());
            self._div.append(" ");
        });
        // auto attach if mother is provided
        if (mother != undefined){
            $(mother).append(self._div);
        }
        return self._div;
    },
    show_concepts: function(mother) {
        if (mother == undefined) {
            if (this._div != undefined) {
                var mother = $("<div class='concept_list'>");
                this._div.append(mother);
            }
            else {
                return undefined;
            }
        }
        // add concepts
        _.forEach(this._conceptObjs, function(c){
            var span = c.to_span();
            if (c.flag() == "E"){
                span.addClass("label label-danger");
            }
            else if (c.flag() == "W"){
                span.addClass("label label-warning");
            }
            else if (c.flag() == "I"){
                span.addClass("label label-info");
            }
            else if (c.flag() == "S"){
                span.addClass("label label-success");
            }
            else if (c.flag() == "P"){
                span.addClass("label label-primary");
            }
            else {
                span.addClass("label label-default");
            }
            mother.append(span);
        });
        return mother;
    }
};

Visko.Tagged.Token = function(token){
    this._token = token;
    this.tokenid = ちび.newid();
    this._span = $("<span>");
    this._span.data("tokenid", this._tokenid);
    this._tooltips = $("<div>");
    this._popover = $("<div>");
    this._concepts = [];
    if (this._token.lemma) {
        this.add_tooltip("Lemma: " + this._token.lemma);
    }
    if (this._token.pos) {
        this.add_tooltip("POS: " + this._token.pos);
    }
    if (this._token.comment) {
        this.add_tooltip("Note: " + this._token.comment);
    }
    this.mweid = undefined;
}

Visko.Tagged.Token.prototype = {
    add_tooltip: function(tooltip) {
        if (this._tooltips.is(":not(:empty)")){
            this._tooltips.append("<br/>");
        }
        this._tooltips.append(tooltip);
    },
    add_popover: function(popover) {
        if (this._popover.is(":not(:empty)")){
            this._popover.append("<br/>");
        }
        this._popover.append(popover);
    },
    add_concept: function(conceptObj){
        this._concepts.push(conceptObj);
        if(conceptObj.isMWE()){
            // MWE
            this.mweid = conceptObj.conceptid;
        }
        else {
            conceptObj.tokenid = this.tokenid;
        }
        // Add tooltip
        this.add_tooltip(conceptObj.tooltip());
        // Add popover
        this.add_popover(conceptObj.popover());
    },
    to_span: function(mother) {
        // set label
        this._span.text(this._token.label);
        this._span.data("tokenid", this.tokenid);
        // analyse concepts
        if (this._concepts.length > 0) {
            if (this.mweid == undefined) {
                this._span.addClass("TaggedToken");
            }
            else {
                this._span.addClass("MWE");
                this._span.data("mweid", this.mweid);
            }
            // on word hover
            this._span.mouseenter(function(){
                Visko.Tagged.highlight_concept($(this).data('mweid'));
                $(this).toggleClass("current");
            })
                .mouseleave(function(){
                    Visko.Tagged.highlight_concept($(this).data('mweid'));
                    $(this).toggleClass("current");
                });
            // done hover
        }
        // enable tooltips & popover
        if (this._tooltips.is(":not(:empty)")){
            this._span.tooltip({title: this._tooltips, placement: 'bottom', html: true});
        }
        if (this._popover.is(":not(:empty)")){
            this._span.popover({content: this._popover, placement: 'top', html: true});
        }
                
        // Attach to mother if available
        if (mother != undefined) {
            $(mother).append(this._span);
        }
        return this._span;
    }
}

Visko.Tagged.Concept = function(concept){
    this._concept = concept;
    this.conceptid = ちび.newid();
    this.tokenid = undefined;
}

Visko.Tagged.Concept.prototype = {
    isMWE: function() {
        return this._concept.words.length > 1;
    },
    flag: function(){
        if ('flag' in this._concept){
            return this._concept['flag'];
        }
        return undefined;
    },
    data: function() {
        return this._concept;
    },
    tooltip: function(){
        var tt = this._concept.clemma + ": " + this._concept.tag;
        if (this._concept.comment != undefined) {
            tt += " (" + this._concept.comment + ")";
        }
        return tt;
    },
    popover: function() {
        var concept = this._concept;
        if (concept.popover != undefined){
            return concept.popover;
        }
        // Default popover content
        var popdiv = $("<span>");
        popdiv.append(concept.clemma + ": ");
        var lnk = $("<a href='#'>");
        lnk.text(concept.tag);
        lnk.click(function(){
            if (Visko.find_tag != undefined){
                Visko.find_tag(concept.tag);
            }
            else{
                // do nothing? log it?
                // console.writeline("Couldn't lookup tag " + concept.tag);
            }
        });
        popdiv.append(lnk);
        // comment?
        if (concept.comment) {
            popdiv.append("<br/>");
            popdiv.append(concept.comment);
        }
        return popdiv;
    },
    show_related: function(){
        var self = this;
        if (self.isMWE()){
            Visko.Tagged.highlight_concept(self.conceptid);
        }
        else {
            $(".TaggedSentence .TaggedToken").filter(function(){
                return $(this).data('tokenid') == self.tokenid;                           
            }).toggleClass("MWEActive");
        }
    },
    to_span: function(mother) {
        var self = this;
        var span = $("<span>");
        span.text(self._concept.clemma + ": " + self._concept.tag);
        // highlight
        span.mouseenter(function(){
            self.show_related();
        }).mouseleave(function(){
            self.show_related();
        }).click(function(){
            if (Visko.find_tag != undefined){
                Visko.find_tag(self._concept.tag);
            }            
        });
        if (mother != undefined){
            $(mother).append(span);
        }
        if (self._concept.comment){
            span.tooltip({title: self._concept.comment, placement: 'bottom'});
        }
        return span;
    }
};

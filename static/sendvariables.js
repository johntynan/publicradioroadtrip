// gets properties from page
story_hostname = window.location.hostname
story_url = window.location
story_title = document.title
story_title = escape(story_title);
story_id = NPR.community.storyId

// alert(story_hostname);
// alert(story_url);
// alert(story_title);
// alert(story_id);

// A great place to start creating a bookmarklet:
// Smashing Magazine
// Make Your Own Bookmarklets using JQuery
// http://www.smashingmagazine.com/2010/05/23/make-your-own-bookmarklets-with-jquery/
if (typeof jQuery == 'undefined') {
    var jQ = document.createElement('script');
    jQ.type = 'text/javascript';
    jQ.onload = runthis;
    jQ.src = 'http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js';
    document.body.appendChild(jQ);
    } else {
    if (story_hostname == 'www.npr.org') {
	    runthis();
    }
    else {
        alert("This bookmarklet is intended to be used in conjunction with content on NPR.org");
    }
}

// use this url for testing locally:
// localhost:8000
// change out this url when updating on the production server:
// publicradioroadtrip.appspot.com

function runthis(){
    // alert(story_hostname);
    // alert(story_url);
    // alert(story_id);
    // alert(story_title);
    // alert(story_id);
    
    if ($("#wikiframe").length == 0) {
        var s = "";
        s = story_id;
        if (s == "") {
            var s = prompt("Forget something?");
        }
        if ((s != "") && (s != null)) {
            $("body").append("\
			<div id='wikiframe'>\
				<div id='wikiframe_veil' style=''>\
					<p>Loading...</p>\
				</div>\
                <iframe src='http://publicradioroadtrip.appspot.com/publicradioroadtrip/default/add_story?nprid=" + s + '&title=' + story_title + '&url='+ story_url +"' onload=\"$('#wikiframe iframe').slideDown(500);\">Enable iFrames.</iframe>\
				<style type='text/css'>\
					#wikiframe_veil { display: none; position: fixed; width: 100%; height: 100%; top: 0; left: 0; background-color: rgba(255,255,255,.25); cursor: pointer; z-index: 900; }\
					#wikiframe_veil p { color: black; font: normal normal bold 20px/20px Helvetica, sans-serif; position: absolute; top: 50%; left: 50%; width: 10em; margin: -10px auto 0 -5em; text-align: center; }\
					#wikiframe iframe { display: none; position: fixed; top: 10%; left: 10%; width: 80%; height: 80%; z-index: 999; border: 10px solid rgba(0,0,0,.5); margin: -5px 0 0 -5px; }\
				</style>\
			</div>");
            $("#wikiframe_veil").fadeIn(750);
        }
    }
    else {
        $("#wikiframe_veil").fadeOut(750);
        $("#wikiframe iframe").slideUp(500);
        // setTimeout("$('#wikiframe').remove()", 750);
    }
    $("#wikiframe_veil").click(function(event){
        $("#wikiframe_veil").fadeOut(750);
        $("#wikiframe iframe").slideUp(500);
        // setTimeout("$('#wikiframe').remove()", 750);
    });
}


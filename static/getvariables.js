var query = window.location.search.substring(1);
var pairs = query.split("&");
var story_id = pairs[0].substring(8,17)
var story_title = unescape(pairs[1].substring(6))

// document.write(pairs + "<br />");
document.write("Story ID: " + story_id + "<br />");
document.write("Story Title: " + story_title + "<br />");

document.story_form.story_story_npr_id.value = story_id
document.story_form.story_story_title.value = story_title


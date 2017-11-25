chrome.runtime.sendMessage({todo : "showPageAction"});
chrome.runtime.onMessage.addListener(function(request,sender,sendResponse){

if(request.todo == "GetSummary")
{
    jsonObj = [];
    $( ".review-text" ).each(function( index ) {
    item = {}
    item["id"] = index;
    item["text"] = $( this ).text();
    jsonObj.push(item);
  	});
    console.log(jsonObj);
}
if(request.todo == "GetSummaryPara")
{
    jsonObj = [];
    item = {}
    item["id"] = 1;
    item["text"] = request.text;
    jsonObj.push(item);
  	console.log(jsonObj);
}

});
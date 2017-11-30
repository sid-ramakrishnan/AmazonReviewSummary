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


    $.ajax({
        type : 'POST',
        url : "http://127.0.0.1:5000/summarize",
        //contentType: 'application/json;charset=UTF-8',
        contentType: 'application/json',
        data : JSON.stringify(jsonObj),
        dataType:"json",
        crossDomain: true,
        success : function(response){ 
            console.log("Respose reached");
            console.log(response);
            alert("Taking you to summaries!");
            var x=window.open();
            x.document.open();
            x.document.write('<h1>Summary Reviews Page</h1>');
            x.document.write('<center><img style="width:40%; height=40;" src="https://i.imgur.com/7UJ2x8K.png"/></center>');
            for (var key in response)
            {
                //if(key.text.)\
                // x.document.write('<h3>'+key+'. </h3>');
                x.document.write('<h3>'+response[key].text+'</h3>');
            }
            x.document.close();
            
        },
        error : function(response)
        {
            console.log("Error");
            console.log(response);
            

        }
    });

    

}
if(request.todo == "GetSummaryPara")
{
    jsonObj = [];
    item = {}
    item["id"] = 1;
    item["text"] = request.text;
    jsonObj.push(item);
  	console.log(jsonObj);

    $.ajax({
        type : 'POST',
        url : "http://127.0.0.1:5000/summarize",
        //contentType: 'application/json;charset=UTF-8',
        contentType: 'application/json',
        data : JSON.stringify(jsonObj),
        dataType:"json",
        crossDomain: true,
        success : function(response){ 
            console.log("Respose reached");
            console.log(response);
            alert("Taking you to summaries!");
            var x=window.open();
            x.document.open();

            x.document.write('<h1>Summary Reviews Individual</h1>');
            x.document.write('<center><img style="width:40%; height=40;" src="https://i.imgur.com/7UJ2x8K.png"/></center>');
            for (var key in response)
            {
                // x.document.write('<h3>'+key+'. </h3>');
                x.document.write('<h3>'+response[key].text+'</h3>');
            }
            x.document.close();
            
            
        },
        error : function(response)
        {
            console.log("Error");
            console.log(response);
            

        }
    });
}

});
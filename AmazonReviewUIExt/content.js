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
        //data: JSON.stringify([{title: 'hallo', article: 'test'},{title: 'hinm', article: 'tehist'}]),
        dataType:"json",
        // xhrFields: {
        //     withCredentials: true
        // },
        crossDomain: true,
        success : function(response){ 
            console.log("Respose reached");
            console.log(response); 
        },
        error : function(response)
        {
            console.log("Error");
            console.log(response);
        }
    });

    //  $.ajax({
    //     type : 'GET',
    //     url : "http://127.0.0.1:5000/hello",
    //     // contentType: 'application/json;charset=UTF-8',
    //     // // data : {'data':jsonObj},
    //     // xhrFields: {
    //     //     withCredentials: true
    //     // },
    //     crossDomain: true,
    //     success : function(response){ 
    //         console.log("Respose reached");
    //         console.log(response); 
    //     }
    // });


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
        url : "{{url_for('test')}}",
        contentType: 'application/json;charset=UTF-8',
        data : {'data':jsonObj},
        success : function(response){ 
            console.log("Respose reached");
            console.log(response); 
        }
    });
}

});
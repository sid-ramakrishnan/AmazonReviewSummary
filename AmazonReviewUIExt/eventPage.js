var contextMenuItem = {
	"id":"spendMoney",
	"title":"SpendMoney",
	"contexts":["selection"]
};




chrome.runtime.onMessage.addListener(function(request,sender,sendResponse){

if(request.todo == "showPageAction"){
	chrome.tabs.query({active:true,currentWindow:true},function(tabs){
	chrome.pageAction.show(tabs[0].id);
});

	var contextMenuItem = {
	"id":"AmazonReviewSummary",
	"title":"GetAmazonReviewSummary",
	"contexts":["selection"]
	};

	chrome.contextMenus.create(contextMenuItem);
	chrome.contextMenus.onClicked.addListener(function(clickData){
	if(clickData.menuItemId == "AmazonReviewSummary" && clickData.selectionText){
		
		chrome.tabs.query({active: true, currentWindow:true},function(tabs){
        chrome.tabs.sendMessage(tabs[0].id,{todo:"GetSummaryPara",text:clickData.selectionText});
	});
    }



	});


}

});


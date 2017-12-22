# AmazonReviewSummary

For Cleaning Data and other Pre Processing steps, view the instructions in the Readme of "data cleaning and visualization" folder.

1) Chrome Ext UI : 

To make this work carry out the following steps:

1) Clone the ExtUI folder.
2) Open Chrome and type chrome://extensions
3) Check the Developer mode option
4) Click load unpacked extension and add the folder as it is (unzip first if required). 
5) You should see a blue logo (will be gray initially) on the top right corner. This means the extension has been loaded successfully.
6) It will be gray initially as it is disabled until you open a customer reviews page. 
7) Open the following site : https://www.amazon.com/All-New-Remote-Pendant-Streaming-Player/product-reviews/B01N32NCPM/ref=cm_cr_dp_d_show_all_top?ie=UTF8&reviewerType=all_reviews
8) The extension will now be blue. This means you can use the extension. Click the icon and hit Get Summary button.
9) right click the DOM and click inspect element and you should see a json array with index and text of each review.

You can try any customer review page by going to Amazon.com, clicking a product and clicking on "See all reviews".

Additional feature:

User can also summarize individual review paragraphs if needed. Go to reviews page and highlight a paragraph. Right click and you will see the option
to get the summary. Inspect element once again and you will see one array object. This will indicate that the data has been collected properly.

Backend Model Training :

1) We train in the train.py file which saves the summarization models in a json file.
2) In server.py at startup, we load the saved Json Models and the required word to index dictionaries.
3) The UI makes a REST API call to the Flask API exposed
4) The response is sent back as a Json Object to the UI and these summarized results are shown on a new page.

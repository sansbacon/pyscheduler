/*
  var ts = String(new Date().getTime())
  var config = {'n_rounds': 7, 'paired': 0}

  var formData = {
    'ts': ts,
    'config': config
  }

  var gcr_url = 'https://helloworld-axquv55tla-uc.a.run.app';

  var options = {
    'method' : 'post',
    'payload' : formData
  };

  var response = UrlFetchApp.fetch(gcr_url, options);
*/

function processForm(formObject) {
    return formObject;
}
  
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Pickleball Scheduler')
    .addItem('Open Scheduler', 'individualScheduler')
    .addToUi();
}
  
function individualScheduler() {
  var html = HtmlService.createHtmlOutputFromFile('Page').setTitle('Pickleball Scheduler');
  SpreadsheetApp.getUi().showSidebar(html);
}  


  }
  
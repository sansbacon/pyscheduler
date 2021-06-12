294709557925-v6k56qluh1hpjvnjq8vhjgqrfi23f6bf.apps.googleusercontent.com
Bu4jgk8S88_1BE5TGyRf0AFN

/**
 * @OnlyCurrentDoc
 */

function onOpen() {
  var ui = SpreadsheetApp.getUi();
  // Or DocumentApp or FormApp.
  ui.createMenu('Scheduler')
      .addItem('Run Individual Scheduler', 'individualScheduler')
      .addItem('Run Pair Scheduler', 'pairScheduler')
      .addToUi();
}

function individualScheduler() {
  // Display a modal dialog box with custom HtmlService content.
  var htmlOutput = HtmlService
    .createHtmlOutput('<p>A change of speed, a change of style...</p>')
    .setWidth(250)
    .setHeight(300);
  SpreadsheetApp.getUi().showModalDialog(htmlOutput, 'My add-on');
 
  // var response = UrlFetchApp.fetch('http://www.google.com/');
  // Logger.log(response.getResponseCode());
  // SpreadsheetApp.getUi() // Or DocumentApp or FormApp.
  //   .alert('You clicked individual scheduler!');
}

function pairScheduler() {
    SpreadsheetApp.getUi() // Or DocumentApp or FormApp.
     .alert('Thanks for your interest but this feature is not yet available');
  // var response = UrlFetchApp.fetch('http://www.yahoo.com/');
  // Logger.log(response.getResponseCode());
  // SpreadsheetApp.getUi() // Or DocumentApp or FormApp.
  //   .alert('You clicked pair scheduler!');
}


https://www.googleapis.com/auth/script.external_request
https://www.googleapis.com/auth/script.container.ui
https://www.googleapis.com/auth/forms.currentonly
https://www.googleapis.com/auth/documents.currentonly
https://www.googleapis.com/auth/spreadsheets.currentonly


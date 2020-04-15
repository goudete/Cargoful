const puppeteer = require('puppeteer');
//https://www.youtube.com/watch?v=aRXzW-o-zqs basic headless chrome YT tutorial
//member table tutorial http://toddhayton.com/2018/08/01/scraping-with-puppeteer/

//This function scrapes the necessary data from the toll booth price table.
//We only care about total cost for the route, this info is in a single row.
// async function scrapeTollTotals(page) {
//     const data = await page.evaluate(() => {
//         const results = Array.from(document.querySelectorAll('#tContenido > tbody > tr:nth-child(41)'));
//         return results;
//     });
//     console.log(data)
//     return data;
// }


async function getBunnies(originState,originCity,destinationState,destinationCity,truckCategory) {
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: null
  });

  const page = await browser.newPage();

  const url = 'http://app.sct.gob.mx/sibuac_internet/ControllerUI?action=cmdEscogeRuta';


  await page.goto(url);
  //set origin state 
  await page.waitForSelector('#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > select');
  await page.select('select[name="edoOrigen"]', originState);
  //set destination state
  //await page.waitFor('.select1')
  await page.waitForSelector('#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(2) > td:nth-child(5) > select');
  await page.waitFor(50);
  await page.select('select[name="edoDestino"]', destinationState);
  //set origin city

  await page.waitForSelector('#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(3) > td:nth-child(2) > select');
  await page.waitFor(50);


  //await page.waitForFunction(() => document.querySelector('ciudadOrigen').length > 1);

  await page.select('select[name="ciudadOrigen"]', originCity);

  //set destination city 

  // await page.waitFor('.select1');
  // await page.waitFor(100);

  await page.waitForSelector('#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(3) > td:nth-child(5) > select');


  await page.select('select[name="ciudadDestino"]', destinationCity);

  //set vehicle type
  await page.waitForSelector('#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(7) > td:nth-child(2) > select'); 
  await page.select('select[name="vehiculos"]', truckCategory);
  // await page.select('select[name="vehiculos"]', 'C');
  // await page.waitFor(100);

  //wait for submit button
  await page.waitForSelector('#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(4) > td.abacentro > input');



  await page.click('input[type="submit"]');
  await page.waitForSelector('#tContenido')

  const selector = '#tContenido > tbody > tr';

  const row = await page.$$eval(selector, trs => trs.map(tr => {
	  const tds = [...tr.getElementsByTagName('td')];
	  return tds.map(td => td.textContent);
  }));

 console.log(row[row.length-5]);
 await browser.close();

 //return -1;

  //let results = (await page.$$('#tContenido > tbody > tr:nth-child(41)'));

  // const results = await page.$$eval('.tr_gris', trs => {
  // 	return trs.map(tr => {
  // 		const properties = {};
  // 		const tdElement = tr.lastElementChild;
  // 		properties.price = tdElement.innerText
  // 	})
  // })

  //console.log(results);


  //const results = Array.from(page.querySelectorAll('#tContenido > tbody > tr:nth-child(41)'));


  // const selectElem = await page.$('select[name="ciudadOrigen"]');
  // await selectElem.length > 1

  // //await page.waitForFunction(() => document.querySelector('ciudadOrigen').length > 1);

  // await page.select('select[name="ciudadOrigen"]', '2362');
  // await page.select('select[name="ciudadDestino"]', '1139');



  //await page.waitFor('.select1')

  // const results = await page.$$eval('.select1', buttons => {
  // 	return buttons.map(row => {
  // 		const properties = {};
  // 		//const titleElement = row.querySelector('.select1');
  // 		properties.name = row.name
  // 		//properties.title = titleElement.name;
  // 		//properties.url = titleElement.getAttribute('href');
  // 		return properties;
  // 	});
  // })

 // console.log(results); 

}
// var myArgs = process.argv.slice(2)
// console.log(myArgs)
// var originState = String(myArgs[0]);
// var originCity =String(myArgs[1]);
// var destinationState = String(myArgs[2]);
// var destinationCity = String(myArgs[3]);

// console.log(originState)

// var aye = getBunnies(originState,originCity,destinationState,destinationCity);

function main()
{
var myArgs = process.argv.slice(2)
var originState = String(myArgs[0]);
var originCity =String(myArgs[1]);
var destinationState = String(myArgs[2]);
var destinationCity = String(myArgs[3]);
var truckCategory = String(myArgs[4]);


getBunnies(originState,originCity,destinationState,destinationCity,truckCategory);

}
main();


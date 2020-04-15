const puppeteer = require('puppeteer');
const fs = require('fs');
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
async function getSelectOptions(page, selector) {
    const options = await page.evaluate(optionSelector => {
        return Array.from(document.querySelectorAll(optionSelector))
            .filter(o => o.value)
            .map(o => {
                return {
                    name: o.text,
                    value: o.value
                };
            });        
    }, selector);

    return options;
}
async function getStates(page) {
    return await getSelectOptions(page,
        'select#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(2) > option'
    );
}


async function getBunnies() {
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: null
  });

  var results = {}

  const page = await browser.newPage();

  const url = 'http://app.sct.gob.mx/sibuac_internet/ControllerUI?action=cmdEscogeRuta';


  await page.goto(url);
  //set origin state 
  await page.waitForSelector('#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > select');
  //await page.select('select[name="edoOrigen"]', originState);
  const state_opts = await getSelectOptions(page, '#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > select > option');
  console.log(state_opts)

  for (const [ i, state ] of state_opts.entries()) {
    if (state.value != '0'){
      console.log(state.name);

      await page.select('select[name="edoOrigen"]', state.value);
      await page.waitForSelector('#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(3) > td:nth-child(2) > select');
      await page.waitFor(50);

      const city_opts = await getSelectOptions(page, '#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(3) > td:nth-child(2) > select > option');
      if (state.value == '15' || state.value == '11' || state.value == '22' || state.value == '9'){
        console.log('aye')
        console.log(city_opts)
      }
      results[state.value] = city_opts;

    }

  }

  // await page.select('select[name="edoOrigen"]', state);
  // await page.waitForSelector('#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(3) > td:nth-child(2) > select');
  // const city_opts = await getSelectOptions(page, '#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(3) > td:nth-child(2) > select > option');
  // console.log(city_opts);

  // test.state = city_opts;
  // console.log(test);
console.log(results);
fs.writeFileSync('./state_city_vals.json', JSON.stringify(results), 'utf-8');
 
 await browser.close();


}
async function run(){
    console.log('Here JS');
    const browser = await puppeteer.launch({headless:false})
    const page = await browser.newPage()
    await page.goto('http://app.sct.gob.mx/sibuac_internet/ControllerUI?action=cmdEscogeRuta');
    await page.waitForSelector('#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > select');
    //const selectOptions = await page.$$eval('#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(2) > td:nth-child(2) ', options => { return options.map(option => option.value ) })  
    const divsCounts = await page.$$eval('#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > select', divs => divs.options);
  
    await console.log(divsCounts);
}

async function js(){
    console.log('Here JS');
    const browser = await puppeteer.launch({headless:false})
    const page = await browser.newPage()
    await page.goto('http://app.sct.gob.mx/sibuac_internet/ControllerUI?action=cmdEscogeRuta');
    await page.waitForSelector('#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > select');
    const selectElem = await page.$('select[name="edoOrigen"]');    
    page.eval(element => {
    return element.innerText
    }, selectElem).then(text => {
    console.log(text)
    })
}


async function main()
{
const browser = await puppeteer.launch({ headless: false, slowMo: 250 });
const page = await browser.newPage();

await page.goto('http://app.sct.gob.mx/sibuac_internet/ControllerUI?action=cmdEscogeRuta');
await page.waitForSelector('#headerEPN > table:nth-child(3) > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > select');
await page.waitFor(1000);

let states = await getStates(page);
console.log(states)

}
getBunnies();


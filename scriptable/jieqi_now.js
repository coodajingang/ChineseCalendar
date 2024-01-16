
var DARK_MODE_BGCOLOR     = '#262335'
var LIGHT_MODE_BGCOLOR    = '#4f6a8f'
var PREFER_TRANSPARENT_BG = false
var nobg = !PREFER_TRANSPARENT_BG ? null 
    : await importModuleOptional('no-background')

// ?y=2023&m=6&d=8 
const url_prefix = 'https://calendar.c2psevgthil.workers.dev/dayinfo'  


async function createWidget(widgetFamily='small') {  
  const spacing = 1.0;
  const widget = new ListWidget()
  widget.setPadding(spacing,spacing,spacing,spacing)
  widget.spacing = spacing

  widget.backgroundColor = Color.dynamic(
    new Color(LIGHT_MODE_BGCOLOR), 
    new Color(DARK_MODE_BGCOLOR))

  const foreColor = Color.white()

  const now = new Date();
  const y = now.getFullYear(), m = now.getMonth()+1, d = now.getDate() 
  const hour = now.getHours();

  let req = new Request(`${url_prefix}?y=${y}&m=${m}&d=${d}`);
  req.method = 'GET';
  const data = await req.loadJSON()
  if (!data || data.success != 1) {
    log('Error when get data!' + (!data ? '' : data.msg))
    Script.complete();
    return;
  }

  const bazi = data.data;

  const hIndex = Math.floor((hour+1)/2);
  const hGZ = bazi.hs[hIndex]

  const refreshDate = new Date()
  refreshDate.setHours(23)
  refreshDate.setMinutes(59)
  refreshDate.setSeconds(59)
  refreshDate.setMilliseconds(0)
  refreshDate.setDate(refreshDate.getDate() + 1);
  widget.refreshAfterDate = refreshDate

  const tailStack = widget.addStack()
  tailStack.setPadding(0,0,0,0)
  tailStack.centerAlignContent()
  tailStack.layoutVertically()
  tailStack.addText(genJieQi(bazi, 0))
  tailStack.addSpacer()
  tailStack.addText(genJieQi(bazi, 1))

  return widget
}



//---[ main ]-------------------------------------
if (config.runsInWidget) {
    let widget = await createWidget(config.widgetFamily)
    Script.setWidget(widget)
    Script.complete()
  } else {
    // show options
    const options = ['Preview Widget']
    if (nobg) {
      options.push('Set Background')
    }
    options.push('Cancel')
    let response = await presentAlert(
      'Options', options)
    let sel = options[response]
    switch(sel) {
      case 'Preview Widget':
        await previewWidget()
        break;
      case 'Set Background':
        await nobg.chooseBackgroundSlice(widgetID)
        break;
      default:   
    }
}

function genJieQi(bazi, i) {
    if (!bazi || !bazi.solar || !bazi.solar.length || bazi.solar.length <= i) {
        log('No solar info ' + i)
        return ''
    }
    const d = bazi.solar[i]
    return d.name + ":" + d.day  + '日' + d.time
}
//--公共方法库-------------------
function sfIcon(name, font) {
    const sf = SFSymbol.named(name)
    sf.applyFont(font)
    return sf.image
  }
  function formatNumber(n) {
    return new Intl.NumberFormat().format(n)
  }
async function previewWidget() {
    let widget;
    let resp = await presentAlert('Preview Widget',
      ['Small','Medium','Large','Cancel'])
    switch (resp) {
      case 0:
        widget = await createWidget('small')
        await widget.presentSmall()
        break;
      case 1:
        widget = await createWidget('medium')
        await widget.presentMedium()
        break;
      case 2:
        widget = await createWidget('large')
        await widget.presentLarge()
        break;
      default:
    }
  }
async function presentAlert(prompt,items,asSheet) 
{
  let alert = new Alert()
  alert.message = prompt
  
  for (const item of items) {
    alert.addAction(item)
  }
  let resp = asSheet ? 
    await alert.presentSheet() : 
    await alert.presentAlert()
  return resp
}

async function downloadImage(url) {
  const req = new Request(url) 
  const img = await req.loadImage()
  return img
}

async function importModuleOptional(module_name) {
    const ICLOUD =  module.filename
                      .includes('Documents/iCloud~')
    const fm = FileManager.local()
    if (!/\.js$/.test(module_name)) {
      module_name = module_name + '.js'
    }
    const module_path = fm.joinPath
                          (fm.documentsDirectory(), 
                          module_name)
    if (!fm.fileExists(module_path)) {
      log(`module ${module_name} does not exist`)
      return null
    }
    if (ICLOUD) {
      await fm.downloadFileFromiCloud(module_path)
    }
    const mod = importModule(module_name)
    return mod
}

// ----------------
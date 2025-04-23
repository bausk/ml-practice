// Script to capture content from makereal.tldraw.com using Browser MCP

async function captureTldraw() {
  try {
    console.log('Connecting to existing browser instance...');
    
    // Navigate to the site if needed (will use existing tab if already open)
    const pages = await browser.pages();
    let page = pages.find(p => p.url().includes('makereal.tldraw.com'));
    
    if (!page) {
      console.log('No existing tab with makereal.tldraw.com found, navigating...');
      page = await browser.newPage();
      await page.goto('https://makereal.tldraw.com/');
      await page.waitForSelector('canvas', { timeout: 10000 });
    } else {
      console.log('Found existing makereal.tldraw.com tab');
      await page.bringToFront();
    }
    
    // Get a screenshot of the entire page
    console.log('Taking a screenshot of the entire page...');
    const fullScreenshot = await page.screenshot({ 
      type: 'png',
      fullPage: true
    });
    await browser.writeFile('tldraw-full-page.png', fullScreenshot);
    
    // Get a screenshot of just the canvas element
    console.log('Looking for canvas element...');
    const canvasElement = await page.$('canvas');
    
    if (canvasElement) {
      console.log('Taking a screenshot of the canvas...');
      const canvasScreenshot = await canvasElement.screenshot({
        type: 'png',
        omitBackground: false
      });
      await browser.writeFile('tldraw-canvas.png', canvasScreenshot);
    } else {
      console.log('Canvas element not found');
    }
    
    // Try to extract drawing data if possible
    console.log('Attempting to extract drawing data...');
    const drawingData = await page.evaluate(() => {
      // This is an attempt to access tldraw's internal state
      // It may not work depending on how tldraw structures its app
      if (window.app && window.app.store) {
        try {
          return window.app.store.getSnapshot();
        } catch (e) {
          return { error: 'Could not extract snapshot data', message: e.message };
        }
      }
      return { message: 'Could not access app state' };
    });
    
    // Save whatever data we could get
    await browser.writeFile('tldraw-data.json', JSON.stringify(drawingData, null, 2));
    
    return {
      success: true,
      message: 'Captured tldraw content',
      fullPageImage: 'tldraw-full-page.png',
      canvasImage: 'tldraw-canvas.png',
      dataFile: 'tldraw-data.json'
    };
  } catch (error) {
    console.error('Error capturing tldraw content:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

// Run the capture function
captureTldraw().then(result => {
  console.log('Capture operation completed:', result);
  // Don't close the browser since we might be using an existing session
}); 
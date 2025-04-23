// Browser MCP script to extract drawing data using our API

async function extractDrawing() {
  try {
    // Navigate to the drawing interface
    await browser.goto('http://localhost:3000/index.html');
    
    // Wait for the page to fully load and the Three.js canvas to be rendered
    await browser.waitForSelector('canvas');
    
    // Wait a bit more for any animations or initializations
    await browser.wait(1000);
    
    // Extract the drawing data using the app's own functionality
    const drawingData = await browser.evaluate(() => {
      // Get the current drawing data from the app's variables
      if (typeof drawnLines === 'undefined') {
        return { lines: [] };
      }
      
      // Use the same format as in the saveDrawing function
      return {
        lines: drawnLines.map(line => ({
          points: line.points.map(p => ({ x: p.x, y: p.y, z: p.z })),
          color: line.color,
          lineWidth: line.lineWidth
        }))
      };
    });
    
    // Save the drawing data to a file
    await browser.writeFile('extracted-drawing.json', JSON.stringify(drawingData, null, 2));
    console.log('Drawing data saved to extracted-drawing.json');
    
    // Also capture a screenshot of the canvas
    const canvasElement = await browser.evaluateHandle(() => {
      return document.querySelector('canvas');
    });
    
    const screenshot = await canvasElement.screenshot({
      type: 'png',
      omitBackground: false
    });
    
    await browser.writeFile('drawing-screenshot.png', screenshot);
    console.log('Canvas screenshot saved to drawing-screenshot.png');
    
    // Show stats about the drawing
    console.log(`Drawing statistics: ${drawingData.lines.length} strokes`);
    
    return {
      success: true,
      drawingData: drawingData,
      imagePath: 'drawing-screenshot.png'
    };
  } catch (error) {
    console.error('Error extracting drawing:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

// Run the extraction function
extractDrawing().then(result => {
  console.log('Extraction completed:', result.success ? 'Successfully' : 'Failed');
  browser.close();
}); 
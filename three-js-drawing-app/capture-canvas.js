// Script to capture the Three.js canvas content using Browser MCP

async function captureDrawing() {
  try {
    // Navigate to the drawing interface
    await browser.goto('http://localhost:3000/index.html');
    
    // Wait for the page to fully load and the Three.js canvas to be rendered
    await browser.waitForSelector('canvas');
    
    // Wait a bit more for any animations or initializations
    await browser.wait(1000);
    
    // Get the canvas element
    const canvasElement = await browser.evaluateHandle(() => {
      return document.querySelector('canvas');
    });
    
    // Capture the canvas as an image
    const screenshot = await canvasElement.screenshot({
      type: 'png',
      omitBackground: false
    });
    
    console.log('Drawing captured successfully!');
    
    // Save the image to a file
    await browser.writeFile('captured-drawing.png', screenshot);
    console.log('Drawing saved to captured-drawing.png');
    
    // Display information about the drawing
    const drawingInfo = await browser.evaluate(() => {
      if (typeof drawnLines !== 'undefined') {
        return {
          strokes: drawnLines.length,
          points: drawnLines.reduce((total, line) => total + (line.points ? line.points.length : 0), 0)
        };
      }
      return { strokes: 0, points: 0 };
    });
    
    console.log(`Drawing statistics: ${drawingInfo.strokes} strokes, ${drawingInfo.points} points`);
    
    return {
      success: true,
      imagePath: 'captured-drawing.png',
      stats: drawingInfo
    };
  } catch (error) {
    console.error('Error capturing drawing:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

// Run the capture function
captureDrawing().then(result => {
  console.log('Capture operation completed:', result);
  browser.close(); // Close the browser when done
}); 
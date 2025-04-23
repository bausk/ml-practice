# Three.js Drawing Interface

A simple drawing application built with Three.js that allows you to create and save drawings, then use them in other applications.

## Features

- Free-form drawing with customizable line width and color
- Save drawings as JSON files
- Load and view saved drawings
- API for integrating drawings into other applications

## Usage

### Drawing Interface (index.html)

1. Open `index.html` in a web browser
2. Use your mouse or touch to draw on the canvas
3. Controls:
   - Choose colors from the color palette
   - Adjust line width using the slider
   - Clear canvas button removes all drawings
   - Save button downloads your drawing as a JSON file

### Drawing Viewer (viewer.html)

1. Open `viewer.html` in a web browser
2. Click "Choose File" and select a previously saved drawing JSON file
3. Click "Load Drawing" to display the drawing
4. Click "Show as Image" to see the drawing as a bitmap image

### Using the API in Your Applications

To use the drawings in your own application:

```javascript
// Import the API
// Either include api.js in your HTML or import it in Node.js
const { DrawingAPI } = require('./api.js'); // For Node.js

// Create an instance
const api = new DrawingAPI();

// Load drawing from JSON file or string
api.loadDrawing(jsonData);
// OR
await api.loadDrawingFromFile(fileObject);

// Render to Three.js scene
const lines = api.renderToScene(yourThreeJsScene);

// Convert to bitmap
const canvas = api.toBitmap(800, 600);
const imgElement = document.getElementById('your-img');
imgElement.src = canvas.toDataURL();

// Get raw stroke data
const strokes = api.getStrokes();
```

## How It Works

The application uses Three.js to create a 3D scene with an orthographic camera, effectively creating a 2D drawing surface. Each stroke is represented as a Three.js Line object, with points collected as the user draws.

The drawing data is stored in a structured JSON format that includes:
- Line points (x, y, z coordinates)
- Line color
- Line width

This structured data can be saved, loaded, and rendered in various ways using the provided API. 
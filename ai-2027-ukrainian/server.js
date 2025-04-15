const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

// Check if serve is installed
try {
  require.resolve('serve');
  console.log('Starting the development server...');
  
  // Start serve on port 3000
  const serverProcess = exec('npx serve -s . -l 3000', { cwd: __dirname });
  
  serverProcess.stdout.on('data', (data) => {
    console.log(data);
  });
  
  serverProcess.stderr.on('data', (data) => {
    console.error(`Error: ${data}`);
  });
  
  console.log('Server running at http://localhost:3000');
  console.log('Press Ctrl+C to stop the server');
  
} catch (e) {
  console.error('Error: "serve" package is not installed. Please run "npm install" first.');
  process.exit(1);
} 
const fs = require('fs');
const path = require('path');

// Files that should be present in the project
const requiredFiles = [
  'index.html',
  'styles.css',
  'script.js',
  'package.json',
  'vercel.json',
  'robots.txt',
  '404.html',
  'README.md',
  'public/favicon.svg',
  'public/site.webmanifest',
  'public/sitemap.xml'
];

// Check each file
console.log('Checking required files...');
let allFilesPresent = true;

requiredFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  
  if (fs.existsSync(filePath)) {
    console.log(`✓ ${file} exists`);
  } else {
    console.error(`✗ ${file} does not exist`);
    allFilesPresent = false;
  }
});

// Check HTML validation
const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');

// Basic HTML validation checks
const docTypeCheck = html.includes('<!DOCTYPE html>');
const headCheck = html.includes('<head>') && html.includes('</head>');
const bodyCheck = html.includes('<body>') && html.includes('</body>');
const htmlLangCheck = html.includes('<html lang="uk">');

console.log('\nBasic HTML validation:');
console.log(`✓ DOCTYPE declaration: ${docTypeCheck ? 'Present' : 'Missing'}`);
console.log(`✓ <head> tags: ${headCheck ? 'Present' : 'Missing'}`);
console.log(`✓ <body> tags: ${bodyCheck ? 'Present' : 'Missing'}`);
console.log(`✓ Ukrainian language: ${htmlLangCheck ? 'Specified' : 'Not specified'}`);

// Final result
console.log('\nFinal check:');
if (allFilesPresent && docTypeCheck && headCheck && bodyCheck && htmlLangCheck) {
  console.log('✓ All files present and basic validation passed!');
  console.log('✓ Project is ready for deployment to Vercel!');
} else {
  console.error('✗ Some checks failed. Please review the issues above.');
} 
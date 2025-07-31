#!/usr/bin/env node

/**
 * Widget Build Script
 * Builds the embeddable widget for production
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const WIDGET_DIR = path.join(__dirname, '../src/widget');
const DIST_DIR = path.join(__dirname, '../public/widget');

console.log('🔧 Building Chatbot SaaS Widget...');

// Ensure dist directory exists
if (!fs.existsSync(DIST_DIR)) {
  fs.mkdirSync(DIST_DIR, { recursive: true });
}

// Change to widget directory
process.chdir(WIDGET_DIR);\n
try {
  // Install dependencies if needed
  if (!fs.existsSync('node_modules')) {
    console.log('📦 Installing dependencies...');
    execSync('npm install', { stdio: 'inherit' });
  }

  // Build widget
  console.log('🏗️  Building widget...');
  execSync('npm run build', { stdio: 'inherit' });

  // Copy built files to public directory
  console.log('📂 Copying files to public directory...');
  const widgetDistDir = path.join(WIDGET_DIR, 'dist');
  
  if (fs.existsSync(widgetDistDir)) {
    // Copy all files from dist to public/widget
    const files = fs.readdirSync(widgetDistDir);
    files.forEach(file => {
      const srcPath = path.join(widgetDistDir, file);
      const destPath = path.join(DIST_DIR, file);
      fs.copyFileSync(srcPath, destPath);
      console.log(`✅ Copied: ${file}`);
    });

    // Also copy embed.js
    const embedSrc = path.join(WIDGET_DIR, 'embed.js');
    const embedDest = path.join(DIST_DIR, 'embed.js');
    if (fs.existsSync(embedSrc)) {
      fs.copyFileSync(embedSrc, embedDest);
      console.log('✅ Copied: embed.js');
    }
  }

  console.log('🎉 Widget build completed successfully!');
  console.log(`📍 Files available at: ${DIST_DIR}`);

} catch (error) {
  console.error('❌ Build failed:', error.message);
  process.exit(1);
}
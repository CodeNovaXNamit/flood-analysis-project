const fs = require('fs');
let content = fs.readFileSync('src/app/data/mockGeoJSON.ts', 'utf8');

// Find the start of the `const rawFeatures = [` line
const arrayStart = content.indexOf('const rawFeatures = [');
if (arrayStart > -1) {
  // Find where it ends
  const arrayEnd = content.indexOf('export const mockDelhiWards');
  if (arrayEnd > -1) {
    // We remove the massive local definition
    content = content.substring(0, arrayStart) + '\n' + content.substring(arrayEnd);
    
    // And add the import at the top
    const importStatement = `import { rawFeatures } from './Delhi_Wards_with_risk--final';\n`;
    content = importStatement + content;
    
    fs.writeFileSync('src/app/data/mockGeoJSON.ts', content, 'utf8');
    console.log('mockGeoJSON.ts fixed!');
  }
}

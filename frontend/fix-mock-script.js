const fs = require('fs');

try {
  let content = fs.readFileSync('src/app/data/mockGeoJSON.ts', 'utf8');

  // Replace from `const rawFeatures = [` to `export const mockDelhiWards`
  const startIdx = content.indexOf('const rawFeatures = [');
  const endIdx = content.indexOf('export const mockDelhiWards');

  if (startIdx !== -1 && endIdx !== -1) {
    let newContent = content.substring(0, startIdx);
    newContent += 'import { rawFeatures } from "./Delhi_Wards_with_risk--final";\n\n';
    newContent += content.substring(endIdx);
    
    fs.writeFileSync('src/app/data/mockGeoJSON.ts', newContent, 'utf8');
    console.log('Successfully updated mockGeoJSON.ts');
  } else {
    console.log('Failed to find start/end indices.', startIdx, endIdx);
  }
} catch (e) {
  console.log('Error:', e);
}

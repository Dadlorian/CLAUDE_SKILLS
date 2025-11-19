# Matterport API Reference

## SDK Initialization
```javascript
const showcase = new MP.Showcase(iframe, {
  applicationKey: 'YOUR_APP_KEY',
  modelId: 'MODEL_ID'
});

showcase.on('model.loaded', () => {
  console.log('Model loaded');
});
```

## Navigation
```javascript
// Move to position
showcase.Camera.setPosition({
  position: { x: 0, y: 0, z: 0 },
  rotation: { x: 0, y: 90 }
});

// Look at point
showcase.Camera.lookAtPosition({ x: 5, y: 0, z: 0 });
```

## Mattertags
```javascript
// Get all tags
const tags = await showcase.Mattertag.getData();

// Add tag
showcase.Mattertag.add({
  label: 'Kitchen',
  description: 'Newly renovated',
  position: { x: 2, y: 1, z: 3 }
});
```

## Measurements
```javascript
// Enable measurement mode
showcase.Measurements.enable();

// Get measurements
const measurements = await showcase.Measurements.getData();
```

## See Also
- photogrammetry_reference.md
- vr_platforms.md

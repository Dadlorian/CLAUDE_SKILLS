# Medical Image Viewer Development Guide

## Architecture Overview

### Web-Based Viewer Stack
```
Frontend: HTML5 + JavaScript (cornerstone.js/OHIF)
    ↓
DICOMweb API: WADO-RS, QIDO-RS
    ↓
Backend: Node.js/Python (DICOMweb server)
    ↓
DICOM Storage: PACS/VNA
```

## Using Cornerstone.js

### Basic Setup
```html
<!DOCTYPE html>
<html>
<head>
    <title>DICOM Viewer</title>
    <script src="https://unpkg.com/cornerstone-core@2.6.1/dist/cornerstone.min.js"></script>
    <script src="https://unpkg.com/cornerstone-math@0.1.9/dist/cornerstoneMath.min.js"></script>
    <script src="https://unpkg.com/cornerstone-tools@6.0.8/dist/cornerstoneTools.min.js"></script>
    <script src="https://unpkg.com/cornerstone-wado-image-loader@4.1.2/dist/cornerstoneWADOImageLoader.bundle.min.js"></script>
    <script src="https://unpkg.com/dicom-parser@1.8.13/dist/dicomParser.min.js"></script>
    <style>
        #dicomImage {
            width: 512px;
            height: 512px;
            background-color: black;
        }
    </style>
</head>
<body>
    <div id="dicomImage"></div>
    
    <script>
        // Initialize cornerstone
        const element = document.getElementById('dicomImage');
        cornerstone.enable(element);
        
        // Configure WADO image loader
        cornerstoneWADOImageLoader.external.cornerstone = cornerstone;
        cornerstoneWADOImageLoader.external.dicomParser = dicomParser;
        
        // Load and display image
        const imageId = 'wadouri:http://localhost:8080/dicoms/image.dcm';
        
        cornerstone.loadImage(imageId).then(function(image) {
            cornerstone.displayImage(element, image);
        });
    </script>
</body>
</html>
```

### Window/Level (Windowing)
```javascript
// Add window/level tool
const WwwcTool = cornerstoneTools.WwwcTool;
cornerstoneTools.addTool(WwwcTool);
cornerstoneTools.setToolActive('Wwwc', { mouseButtonMask: 1 });

// Set window/level programmatically
const viewport = cornerstone.getViewport(element);
viewport.voi.windowWidth = 400;
viewport.voi.windowCenter = 40;
cornerstone.setViewport(element, viewport);

// Presets
const presets = {
    lung: { ww: 1500, wc: -600 },
    mediastinum: { ww: 400, wc: 40 },
    bone: { ww: 2000, wc: 400 },
    brain: { ww: 80, wc: 40 }
};

function applyPreset(preset) {
    const viewport = cornerstone.getViewport(element);
    viewport.voi.windowWidth = presets[preset].ww;
    viewport.voi.windowCenter = presets[preset].wc;
    cornerstone.setViewport(element, viewport);
}
```

### Measurement Tools
```javascript
// Initialize tools
cornerstoneTools.init();

// Add measurement tools
cornerstoneTools.addTool(cornerstoneTools.LengthTool);
cornerstoneTools.addTool(cornerstoneTools.AngleTool);
cornerstoneTools.addTool(cornerstoneTools.EllipticalRoiTool);
cornerstoneTools.addTool(cornerstoneTools.RectangleRoiTool);

// Activate length tool
cornerstoneTools.setToolActive('Length', { mouseButtonMask: 1 });

// Get measurement data
const toolState = cornerstoneTools.getToolState(element, 'Length');
if (toolState && toolState.data.length > 0) {
    toolState.data.forEach((measurement, index) => {
        console.log(`Measurement ${index + 1}: ${measurement.length.toFixed(2)} mm`);
    });
}
```

### Multi-Frame/Cine Display
```javascript
const StackScrollMouseWheelTool = cornerstoneTools.StackScrollMouseWheelTool;
const StackScrollTool = cornerstoneTools.StackScrollTool;

// Add stack scrolling
cornerstoneTools.addTool(StackScrollMouseWheelTool);
cornerstoneTools.addTool(StackScrollTool);

// Load image stack
const imageIds = [
    'wadouri:http://localhost:8080/dicoms/image001.dcm',
    'wadouri:http://localhost:8080/dicoms/image002.dcm',
    'wadouri:http://localhost:8080/dicoms/image003.dcm',
    // ... more images
];

const stack = {
    currentImageIdIndex: 0,
    imageIds: imageIds
};

cornerstone.loadImage(imageIds[0]).then(function(image) {
    cornerstone.displayImage(element, image);
    cornerstoneTools.addStackStateManager(element, ['stack']);
    cornerstoneTools.addToolState(element, 'stack', stack);
    
    // Enable mouse wheel scrolling
    cornerstoneTools.setToolActive('StackScrollMouseWheel', {});
});

// Cine (auto-play)
function playCine(frameRate = 10) {
    const playClipOptions = {
        framesPerSecond: frameRate,
        loop: true
    };
    cornerstoneTools.playClip(element, playClipOptions);
}

function stopCine() {
    cornerstoneTools.stopClip(element);
}
```

## OHIF Viewer

### Setup OHIF Viewer
```bash
# Clone repository
git clone https://github.com/OHIF/Viewers.git
cd Viewers

# Install dependencies
yarn install

# Configure DICOMweb endpoint
# Edit platform/viewer/public/config/default.js

# Start development server
yarn run dev
```

### Custom Configuration
```javascript
// config/default.js
window.config = {
    routerBasename: '/',
    servers: {
        dicomWeb: [
            {
                name: 'Hospital PACS',
                wadoUriRoot: 'http://localhost:8080/dcm4chee-arc/aets/DCM4CHEE/wado',
                qidoRoot: 'http://localhost:8080/dcm4chee-arc/aets/DCM4CHEE/rs',
                wadoRoot: 'http://localhost:8080/dcm4chee-arc/aets/DCM4CHEE/rs',
                qidoSupportsIncludeField: true,
                imageRendering: 'wadors',
                thumbnailRendering: 'wadors',
                enableStudyLazyLoad: true,
            },
        ],
    },
};
```

## 3D Visualization

### Using VTK.js for 3D Rendering
```javascript
import vtkFullScreenRenderWindow from '@kitware/vtk.js/Rendering/Misc/FullScreenRenderWindow';
import vtkVolume from '@kitware/vtk.js/Rendering/Core/Volume';
import vtkVolumeMapper from '@kitware/vtk.js/Rendering/Core/VolumeMapper';
import vtkImageData from '@kitware/vtk.js/Common/DataModel/ImageData';

// Create renderer
const fullScreenRenderer = vtkFullScreenRenderWindow.newInstance();
const renderer = fullScreenRenderer.getRenderer();
const renderWindow = fullScreenRenderer.getRenderWindow();

// Load DICOM series and create volume
async function load3DVolume(imageIds) {
    const imageData = vtkImageData.newInstance();
    
    // Load all images
    const images = await Promise.all(
        imageIds.map(id => cornerstone.loadImage(id))
    );
    
    // Stack images into 3D volume
    const width = images[0].width;
    const height = images[0].height;
    const depth = images.length;
    
    const scalarArray = new Int16Array(width * height * depth);
    
    images.forEach((image, z) => {
        const pixelData = image.getPixelData();
        const offset = z * width * height;
        scalarArray.set(pixelData, offset);
    });
    
    imageData.setDimensions(width, height, depth);
    imageData.getPointData().setScalars(
        vtkDataArray.newInstance({
            numberOfComponents: 1,
            values: scalarArray,
        })
    );
    
    // Create volume actor
    const actor = vtkVolume.newInstance();
    const mapper = vtkVolumeMapper.newInstance();
    mapper.setInputData(imageData);
    actor.setMapper(mapper);
    
    // Add to scene
    renderer.addVolume(actor);
    renderer.resetCamera();
    renderWindow.render();
}
```

## Mobile Viewer Development

### React Native DICOM Viewer
```javascript
import React, { useState, useEffect } from 'react';
import { View, Image, TouchableOpacity, Text } from 'react-native';
import RNFS from 'react-native-fs';

const DICOMViewer = ({ dicomUri }) => {
    const [imageData, setImageData] = useState(null);
    const [windowLevel, setWindowLevel] = useState({ ww: 400, wc: 40 });
    
    useEffect(() => {
        loadDICOM(dicomUri);
    }, [dicomUri]);
    
    const loadDICOM = async (uri) => {
        // Load DICOM file
        const fileData = await RNFS.readFile(uri, 'base64');
        
        // Parse DICOM (using WASM dicom-parser)
        const parsedData = parseDICOM(fileData);
        
        // Apply window/level and convert to PNG
        const processedImage = applyWindowLevel(
            parsedData.pixelData,
            windowLevel.ww,
            windowLevel.wc
        );
        
        setImageData(processedImage);
    };
    
    const handlePinchGesture = (event) => {
        // Adjust window/level based on gesture
        const newWW = windowLevel.ww * event.scale;
        const newWC = windowLevel.wc + event.velocity * 10;
        setWindowLevel({ ww: newWW, wc: newWC });
    };
    
    return (
        <View style={{ flex: 1 }}>
            <Image
                source={{ uri: imageData }}
                style={{ flex: 1 }}
                resizeMode="contain"
            />
            <View style={{ flexDirection: 'row', justifyContent: 'space-around', padding: 10 }}>
                <TouchableOpacity onPress={() => applyPreset('lung')}>
                    <Text>Lung</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => applyPreset('bone')}>
                    <Text>Bone</Text>
                </TouchableOpacity>
            </View>
        </View>
    );
};

export default DICOMViewer;
```

## Performance Optimization

### Progressive Loading
```javascript
class ProgressiveImageLoader {
    constructor(imageIds) {
        this.imageIds = imageIds;
        this.lowResLoaded = false;
        this.highResLoaded = false;
    }
    
    async load(element) {
        // Load low-resolution preview first
        const lowResId = this.imageIds[0].replace('.dcm', '_thumb.jpg');
        try {
            const lowResImage = await cornerstone.loadImage(lowResId);
            cornerstone.displayImage(element, lowResImage);
            this.lowResLoaded = true;
        } catch (e) {
            console.log('No low-res preview available');
        }
        
        // Load full resolution in background
        const highResImage = await cornerstone.loadImage(this.imageIds[0]);
        cornerstone.displayImage(element, highResImage);
        this.highResLoaded = true;
    }
}
```

### Image Caching
```javascript
// Configure cache size (in MB)
cornerstone.imageCache.setMaximumSizeBytes(512 * 1024 * 1024); // 512 MB

// Prefetch images
function prefetchSeries(imageIds, startIndex = 0) {
    const prefetchCount = 10; // Prefetch 10 images ahead
    
    for (let i = startIndex; i < Math.min(startIndex + prefetchCount, imageIds.length); i++) {
        cornerstone.loadAndCacheImage(imageIds[i]);
    }
}

// Clear cache when needed
function clearCache() {
    cornerstone.imageCache.purgeCache();
}
```

## Hanging Protocols

### Implement Custom Layouts
```javascript
const hangingProtocols = {
    'ct-chest-comparison': {
        viewports: [
            {position: { row: 0, col: 0 }, series: 'current', window: 'lung'},
            {position: { row: 0, col: 1 }, series: 'current', window: 'mediastinum'},
            {position: { row: 1, col: 0 }, series: 'prior', window: 'lung'},
            {position: { row: 1, col: 1 }, series: 'prior', window: 'mediastinum'},
        ]
    },
    'mr-brain-multisequence': {
        viewports: [
            {position: { row: 0, col: 0 }, series: 't1'},
            {position: { row: 0, col: 1 }, series: 't2'},
            {position: { row: 1, col: 0 }, series: 'flair'},
            {position: { row: 1, col: 1 }, series: 'dwi'},
        ]
    }
};

function applyHangingProtocol(protocolName, studyData) {
    const protocol = hangingProtocols[protocolName];
    
    protocol.viewports.forEach(vp => {
        const element = document.getElementById(`viewport-${vp.position.row}-${vp.position.col}`);
        const series = findSeries(studyData, vp.series);
        const imageId = series.instances[0].imageId;
        
        cornerstone.loadImage(imageId).then(image => {
            cornerstone.displayImage(element, image);
            
            // Apply window preset
            if (vp.window) {
                applyWindowPreset(element, vp.window);
            }
        });
    });
}
```

## Security Considerations

### Secure DICOMweb Access
```javascript
// Add authentication headers
const headers = {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/dicom+json'
};

// Secure image loading
function loadSecureImage(imageId, token) {
    cornerstoneWADOImageLoader.configure({
        beforeSend: function(xhr) {
            xhr.setRequestHeader('Authorization', `Bearer ${token}`);
        }
    });
    
    return cornerstone.loadImage(imageId);
}
```

### PHI Protection
```javascript
// Blur patient demographics in screenshots
function blurPHI(element) {
    const canvas = element.querySelector('canvas');
    const ctx = canvas.getContext('2d');
    
    // Blur top region where PHI typically displayed
    ctx.filter = 'blur(20px)';
    ctx.fillRect(0, 0, canvas.width, 50);
    ctx.filter = 'none';
}
```

## Testing Medical Viewers

### Automated Testing
```javascript
describe('DICOM Viewer', () => {
    it('should load and display image', async () => {
        const element = document.getElementById('dicomImage');
        const imageId = 'wadouri:test-image.dcm';
        
        const image = await cornerstone.loadImage(imageId);
        cornerstone.displayImage(element, image);
        
        expect(element.querySelector('canvas')).toBeTruthy();
        expect(cornerstone.getViewport(element)).toBeTruthy();
    });
    
    it('should apply window/level correctly', () => {
        const viewport = cornerstone.getViewport(element);
        viewport.voi.windowWidth = 400;
        viewport.voi.windowCenter = 40;
        cornerstone.setViewport(element, viewport);
        
        const updatedViewport = cornerstone.getViewport(element);
        expect(updatedViewport.voi.windowWidth).toBe(400);
        expect(updatedViewport.voi.windowCenter).toBe(40);
    });
});
```

## Resources
- Cornerstone.js documentation
- OHIF Viewer GitHub
- VTK.js examples
- DICOMweb specification
- WebGL medical imaging tutorials

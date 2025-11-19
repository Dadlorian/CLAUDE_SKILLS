# Virtual Tour Integration Guide

## Integrating 3D Tours and Virtual Walkthroughs

### Matterport Integration

```javascript
// Embed Matterport tour
const MatterportEmbed = ({ modelId }) => {
  return (
    <iframe
      width="100%"
      height="480"
      src={`https://my.matterport.com/show/?m=${modelId}`}
      frameBorder="0"
      allowFullScreen
      allow="xr-spatial-tracking"
    />
  );
};

// Matterport API integration
const fetchMatterportModel = async (modelId) => {
  const response = await fetch(
    `https://api.matterport.com/api/v1/models/${modelId}`,
    {
      headers: {
        'Authorization': `Bearer ${MATTERPORT_API_KEY}`
      }
    }
  );
  return await response.json();
};
```

### Zillow 3D Home Integration

```javascript
// Store 3D Home tour URL
const listing = {
  virtual_tours: [
    {
      type: 'zillow_3d',
      url: 'https://www.zillow.com/view-3d-home/abc123',
      provider: 'Zillow 3D Home'
    },
    {
      type: 'matterport',
      url: 'https://my.matterport.com/show/?m=xyz789',
      provider: 'Matterport'
    }
  ]
};

// Display virtual tour options
const VirtualTourSection = ({ tours }) => {
  return (
    <div className="virtual-tours">
      <h3>Virtual Tours</h3>
      {tours.map((tour, index) => (
        <button
          key={index}
          onClick={() => window.open(tour.url, '_blank')}
          className="tour-button"
        >
          {tour.provider} Tour
        </button>
      ))}
    </div>
  );
};
```

### YouTube Video Tours

```javascript
const extractYouTubeId = (url) => {
  const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
  const match = url.match(regex);
  return match ? match[1] : null;
};

const VideoTourEmbed = ({ url }) => {
  const videoId = extractYouTubeId(url);

  if (!videoId) return null;

  return (
    <iframe
      width="100%"
      height="480"
      src={`https://www.youtube.com/embed/${videoId}`}
      frameBorder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen
    />
  );
};
```

### Custom 360° Photo Tours

```javascript
// Using Photo Sphere Viewer
import { Viewer } from 'photo-sphere-viewer';

const Photo360Viewer = ({ images }) => {
  const viewerRef = useRef(null);

  useEffect(() => {
    const viewer = new Viewer({
      container: viewerRef.current,
      panorama: images[0],
      navbar: [
        'autorotate',
        'zoom',
        'fullscreen'
      ]
    });

    return () => viewer.destroy();
  }, [images]);

  return <div ref={viewerRef} style={{ width: '100%', height: '500px' }} />;
};
```

## Best Practices

1. **Multiple Options**: Offer both 3D tours and video tours
2. **Mobile Support**: Ensure tours work on mobile devices
3. **Loading States**: Show loading indicators for tours
4. **Analytics**: Track tour engagement metrics
5. **SEO**: Add schema markup for video tours

## See Also
- property_listing_workflow.md

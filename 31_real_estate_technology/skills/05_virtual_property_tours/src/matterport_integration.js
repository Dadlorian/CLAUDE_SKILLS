/**
 * Matterport Integration
 */
const MP = require('@matterport/sdk');

class MatterportTour {
  constructor(iframeId, modelId) {
    const iframe = document.getElementById(iframeId);
    this.showcase = new MP.Showcase(iframe, {
      applicationKey: process.env.MATTERPORT_KEY,
      modelId: modelId
    });
    
    this.showcase.on('model.loaded', () => {
      this.onModelLoaded();
    });
  }
  
  async onModelLoaded() {
    // Get all mattertags
    const tags = await this.showcase.Mattertag.getData();
    console.log(`Loaded ${tags.length} tags`);
    
    // Track analytics
    this.trackView();
  }
  
  async addCustomTag(position, label, description) {
    await this.showcase.Mattertag.add({
      label,
      description,
      anchorPosition: position,
      stemVector: { x: 0, y: 0.5, z: 0 }
    });
  }
  
  trackView() {
    // Analytics tracking
    gtag('event', 'virtual_tour_view', {
      model_id: this.modelId
    });
  }
}

module.exports = MatterportTour;

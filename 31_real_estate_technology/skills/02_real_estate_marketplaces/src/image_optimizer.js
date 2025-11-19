/**
 * Image Optimizer
 * Optimizes property photos for web display and CDN delivery
 */

const sharp = require('sharp');
const AWS = require('aws-sdk');
const path = require('path');
const fs = require('fs').promises;

const s3 = new AWS.S3({
  region: process.env.AWS_REGION || 'us-east-1',
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
});

const CDN_BUCKET = process.env.CDN_BUCKET || 'property-images';
const CDN_BASE_URL = process.env.CDN_BASE_URL || 'https://cdn.example.com';

/**
 * Image size configurations
 */
const IMAGE_SIZES = {
  thumbnail: { width: 200, height: 150, quality: 80 },
  small: { width: 400, height: 300, quality: 85 },
  medium: { width: 800, height: 600, quality: 85 },
  large: { width: 1200, height: 900, quality: 90 },
  xlarge: { width: 1920, height: 1440, quality: 90 }
};

class ImageOptimizer {
  /**
   * Process and optimize a property image
   * @param {Buffer|string} input - Image buffer or file path
   * @param {string} propertyId - Property ID for organizing images
   * @param {number} photoIndex - Photo index/order
   * @returns {Object} URLs for different image sizes
   */
  async processImage(input, propertyId, photoIndex) {
    try {
      // Load image
      let imageBuffer;
      if (typeof input === 'string') {
        imageBuffer = await fs.readFile(input);
      } else {
        imageBuffer = input;
      }

      // Get image metadata
      const metadata = await sharp(imageBuffer).metadata();
      console.log(`Processing image: ${metadata.width}x${metadata.height}, ${metadata.format}`);

      // Generate optimized versions
      const urls = {};

      for (const [sizeName, config] of Object.entries(IMAGE_SIZES)) {
        const optimizedBuffer = await this.optimizeImage(imageBuffer, config);
        const key = `properties/${propertyId}/${photoIndex}_${sizeName}.jpg`;
        const url = await this.uploadToCDN(optimizedBuffer, key);
        urls[sizeName] = url;
      }

      // Generate WebP versions for modern browsers
      const webpBuffer = await sharp(imageBuffer)
        .webp({ quality: 85 })
        .toBuffer();

      const webpKey = `properties/${propertyId}/${photoIndex}.webp`;
      urls.webp = await this.uploadToCDN(webpBuffer, webpKey, 'image/webp');

      return {
        urls,
        metadata: {
          original_width: metadata.width,
          original_height: metadata.height,
          format: metadata.format,
          optimized_at: new Date().toISOString()
        }
      };

    } catch (error) {
      console.error('Image processing failed:', error);
      throw error;
    }
  }

  /**
   * Optimize image to specific dimensions and quality
   * @param {Buffer} buffer - Image buffer
   * @param {Object} config - Size configuration
   * @returns {Buffer} Optimized image buffer
   */
  async optimizeImage(buffer, config) {
    return await sharp(buffer)
      .resize(config.width, config.height, {
        fit: 'inside',
        withoutEnlargement: true
      })
      .jpeg({
        quality: config.quality,
        progressive: true,
        mozjpeg: true
      })
      .toBuffer();
  }

  /**
   * Upload image to CDN (S3)
   * @param {Buffer} buffer - Image buffer
   * @param {string} key - S3 key
   * @param {string} contentType - Content type
   * @returns {string} CDN URL
   */
  async uploadToCDN(buffer, key, contentType = 'image/jpeg') {
    const params = {
      Bucket: CDN_BUCKET,
      Key: key,
      Body: buffer,
      ContentType: contentType,
      ACL: 'public-read',
      CacheControl: 'public, max-age=31536000' // 1 year
    };

    await s3.putObject(params).promise();

    return `${CDN_BASE_URL}/${key}`;
  }

  /**
   * Batch process multiple images for a property
   * @param {Array} images - Array of image buffers/paths
   * @param {string} propertyId - Property ID
   * @returns {Array} Processed image data
   */
  async batchProcess(images, propertyId) {
    const results = [];

    for (let i = 0; i < images.length; i++) {
      try {
        const result = await this.processImage(images[i], propertyId, i + 1);
        results.push({
          order: i + 1,
          ...result
        });
      } catch (error) {
        console.error(`Failed to process image ${i + 1}:`, error);
        results.push({
          order: i + 1,
          error: error.message
        });
      }
    }

    return results;
  }

  /**
   * Add watermark to image
   * @param {Buffer} imageBuffer - Image buffer
   * @param {string} watermarkPath - Path to watermark image
   * @param {Object} options - Watermark options
   * @returns {Buffer} Watermarked image
   */
  async addWatermark(imageBuffer, watermarkPath, options = {}) {
    const {
      position = 'southeast',
      opacity = 0.5,
      margin = 20
    } = options;

    const watermark = await sharp(watermarkPath)
      .resize(200, 50, { fit: 'inside' })
      .toBuffer();

    const watermarkWithOpacity = await sharp(watermark)
      .composite([{
        input: Buffer.from([255, 255, 255, Math.round(opacity * 255)]),
        raw: { width: 1, height: 1, channels: 4 },
        tile: true,
        blend: 'dest-in'
      }])
      .toBuffer();

    const image = sharp(imageBuffer);
    const metadata = await image.metadata();

    // Position watermark
    const positions = {
      southeast: { left: metadata.width - 220, top: metadata.height - 70 },
      southwest: { left: margin, top: metadata.height - 70 },
      northeast: { left: metadata.width - 220, top: margin },
      northwest: { left: margin, top: margin }
    };

    return await image
      .composite([{
        input: watermarkWithOpacity,
        ...positions[position]
      }])
      .toBuffer();
  }

  /**
   * Generate responsive image srcset
   * @param {Object} urls - Image URLs for different sizes
   * @returns {string} srcset attribute value
   */
  generateSrcSet(urls) {
    return [
      `${urls.small} 400w`,
      `${urls.medium} 800w`,
      `${urls.large} 1200w`,
      `${urls.xlarge} 1920w`
    ].join(', ');
  }

  /**
   * Generate picture element with WebP support
   * @param {Object} urls - Image URLs
   * @param {string} alt - Alt text
   * @returns {string} HTML picture element
   */
  generatePictureHTML(urls, alt = '') {
    return `
      <picture>
        <source
          type="image/webp"
          srcset="${urls.webp}"
        />
        <source
          type="image/jpeg"
          srcset="${this.generateSrcSet(urls)}"
          sizes="(max-width: 640px) 100vw,
                 (max-width: 1024px) 50vw,
                 33vw"
        />
        <img
          src="${urls.large}"
          alt="${alt}"
          loading="lazy"
          decoding="async"
        />
      </picture>
    `;
  }

  /**
   * Delete all images for a property
   * @param {string} propertyId - Property ID
   */
  async deletePropertyImages(propertyId) {
    const prefix = `properties/${propertyId}/`;

    // List all objects with prefix
    const listParams = {
      Bucket: CDN_BUCKET,
      Prefix: prefix
    };

    const listedObjects = await s3.listObjectsV2(listParams).promise();

    if (!listedObjects.Contents || listedObjects.Contents.length === 0) {
      return;
    }

    // Delete objects
    const deleteParams = {
      Bucket: CDN_BUCKET,
      Delete: {
        Objects: listedObjects.Contents.map(obj => ({ Key: obj.Key }))
      }
    };

    await s3.deleteObjects(deleteParams).promise();
    console.log(`Deleted ${listedObjects.Contents.length} images for property ${propertyId}`);
  }
}

/**
 * Helper function to download image from URL
 * @param {string} url - Image URL
 * @returns {Buffer} Image buffer
 */
async function downloadImage(url) {
  const axios = require('axios');
  const response = await axios.get(url, { responseType: 'arraybuffer' });
  return Buffer.from(response.data);
}

// Usage example
async function example() {
  const optimizer = new ImageOptimizer();

  // Download image from MLS
  const imageUrl = 'https://mls.example.com/photos/12345_1.jpg';
  const imageBuffer = await downloadImage(imageUrl);

  // Process image
  const result = await optimizer.processImage(imageBuffer, 'prop-12345', 1);

  console.log('Image URLs:');
  console.log('  Thumbnail:', result.urls.thumbnail);
  console.log('  Medium:', result.urls.medium);
  console.log('  Large:', result.urls.large);
  console.log('  WebP:', result.urls.webp);

  // Generate responsive HTML
  const html = optimizer.generatePictureHTML(
    result.urls,
    '3 bedroom home at 123 Main St, Austin, TX'
  );
  console.log('HTML:', html);
}

module.exports = {
  ImageOptimizer,
  downloadImage,
  IMAGE_SIZES
};

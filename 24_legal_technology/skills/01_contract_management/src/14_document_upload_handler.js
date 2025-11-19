/**
 * Document Upload Handler - Handle contract document uploads with validation
 * Express.js middleware for file uploads
 */

const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

class DocumentUploadHandler {
  constructor(uploadDir = './uploads/contracts') {
    this.uploadDir = uploadDir;
    this.allowedMimeTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'image/jpeg',
      'image/png'
    ];
    this.maxFileSize = 50 * 1024 * 1024;

    this.setupStorage();
    this.setupUploader();
  }

  setupStorage() {
    if (!fs.existsSync(this.uploadDir)) {
      fs.mkdirSync(this.uploadDir, { recursive: true });
    }
  }

  setupUploader() {
    const storage = multer.diskStorage({
      destination: (req, file, cb) => {
        cb(null, this.uploadDir);
      },
      filename: (req, file, cb) => {
        const timestamp = Date.now();
        const sanitizedFilename = file.originalname.replace(/[^a-zA-Z0-9.-]/g, '_');
        const filename = `${timestamp}_${sanitizedFilename}`;
        cb(null, filename);
      }
    });

    this.uploader = multer({
      storage,
      limits: {
        fileSize: this.maxFileSize
      }
    });
  }

  getMiddleware() {
    return this.uploader.single('document');
  }

  async processUpload(req, res) {
    try {
      if (!req.file) {
        return res.status(400).json({
          success: false,
          error: 'No file uploaded'
        });
      }

      const file = req.file;
      const metadata = {
        originalFilename: file.originalname,
        filename: file.filename,
        mimeType: file.mimetype,
        size: file.size,
        uploadedAt: new Date(),
        uploadedBy: req.user?.id,
        path: file.path
      };

      return res.json({
        success: true,
        data: {
          file: metadata,
          message: 'File uploaded successfully'
        }
      });
    } catch (error) {
      return res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  async deleteFile(filename) {
    const filePath = path.join(this.uploadDir, filename);

    return new Promise((resolve, reject) => {
      fs.unlink(filePath, (err) => {
        if (err) reject(err);
        else resolve(true);
      });
    });
  }
}

module.exports = DocumentUploadHandler;

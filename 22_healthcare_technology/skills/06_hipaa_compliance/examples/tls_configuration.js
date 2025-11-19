/**
 * TLS/SSL Configuration for HIPAA Compliance
 * Requires TLS 1.2 or higher
 */
const https = require('https');
const fs = require('fs');

const tlsOptions = {
  // Certificates
  key: fs.readFileSync('/path/to/private-key.pem'),
  cert: fs.readFileSync('/path/to/certificate.pem'),
  ca: fs.readFileSync('/path/to/ca-cert.pem'),

  // TLS version - require 1.2 or higher
  minVersion: 'TLSv1.2',
  maxVersion: 'TLSv1.3',

  // Cipher suites (strong only)
  ciphers: [
    'ECDHE-RSA-AES128-GCM-SHA256',
    'ECDHE-RSA-AES256-GCM-SHA384',
    'ECDHE-RSA-AES128-SHA256',
    'ECDHE-RSA-AES256-SHA384'
  ].join(':'),

  // Honor server cipher order
  honorCipherOrder: true,

  // Reject unauthorized
  rejectUnauthorized: true
};

const server = https.createServer(tlsOptions, (req, res) => {
  // Handle requests with HIPAA-compliant TLS
  res.writeHead(200);
  res.end('Secure HIPAA connection');
});

module.exports = { tlsOptions };

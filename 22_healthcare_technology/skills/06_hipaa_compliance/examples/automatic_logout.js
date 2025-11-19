/**
 * HIPAA-Compliant Automatic Logout / Session Timeout
 * 
 * Implements automatic session termination after inactivity
 * Required by Security Rule §164.312(a)(2)(iii) (Addressable)
 */

class SessionTimeoutManager {
  constructor(options = {}) {
    this.timeoutMinutes = options.timeoutMinutes || 15; // HIPAA recommended: ≤15 minutes
    this.warningMinutes = options.warningMinutes || 2; // Warn before logout
    this.checkIntervalSeconds = options.checkIntervalSeconds || 30;
    this.sessions = new Map();
  }

  /**
   * Express middleware to track session activity
   */
  middleware() {
    return (req, res, next) => {
      if (req.session && req.session.id) {
        this.updateActivity(req.session.id);
      }
      next();
    };
  }

  /**
   * Update last activity timestamp for session
   */
  updateActivity(sessionId) {
    this.sessions.set(sessionId, {
      lastActivity: new Date(),
      warned: false
    });
  }

  /**
   * Check for idle sessions and terminate them
   */
  checkSessions(sessionStore) {
    const now = new Date();
    const timeoutMs = this.timeoutMinutes * 60 * 1000;
    const warningMs = (this.timeoutMinutes - this.warningMinutes) * 60 * 1000;

    for (const [sessionId, sessionData] of this.sessions.entries()) {
      const idleTime = now - sessionData.lastActivity;

      if (idleTime >= timeoutMs) {
        // Timeout exceeded - destroy session
        this.destroySession(sessionId, sessionStore);
        console.log(`Session ${sessionId} terminated due to inactivity`);
      } else if (idleTime >= warningMs && !sessionData.warned) {
        // Warn user
        this.warnSession(sessionId);
        sessionData.warned = true;
      }
    }
  }

  /**
   * Destroy inactive session
   */
  destroySession(sessionId, sessionStore) {
    sessionStore.destroy(sessionId, (err) => {
      if (err) {
        console.error(`Error destroying session ${sessionId}:`, err);
      }
    });
    this.sessions.delete(sessionId);
  }

  /**
   * Send warning to user (implement via WebSocket or other mechanism)
   */
  warnSession(sessionId) {
    // Implement warning mechanism
    // Could be WebSocket, Server-Sent Events, etc.
    console.log(`Warning: Session ${sessionId} will expire in ${this.warningMinutes} minutes`);
  }

  /**
   * Start periodic session checking
   */
  startMonitoring(sessionStore) {
    setInterval(() => {
      this.checkSessions(sessionStore);
    }, this.checkIntervalSeconds * 1000);
  }

  /**
   * Client-side timeout handler (JavaScript for browser)
   */
  static getClientSideScript(timeoutMinutes = 15, warningMinutes = 2) {
    return `
      <script>
      (function() {
        const TIMEOUT_MS = ${timeoutMinutes * 60 * 1000};
        const WARNING_MS = ${(timeoutMinutes - warningMinutes) * 60 * 1000};
        
        let timeoutTimer = null;
        let warningTimer = null;
        let logoutModal = null;

        function resetTimers() {
          clearTimeout(timeoutTimer);
          clearTimeout(warningTimer);

          // Hide warning if shown
          if (logoutModal) {
            logoutModal.style.display = 'none';
          }

          // Set warning timer
          warningTimer = setTimeout(showWarning, WARNING_MS);

          // Set logout timer
          timeoutTimer = setTimeout(autoLogout, TIMEOUT_MS);
        }

        function showWarning() {
          // Create or show warning modal
          if (!logoutModal) {
            logoutModal = document.createElement('div');
            logoutModal.id = 'session-timeout-warning';
            logoutModal.innerHTML = \`
              <div style="position: fixed; top: 20px; right: 20px; background: #fff3cd; 
                          border: 1px solid #ffc107; padding: 20px; border-radius: 5px; 
                          box-shadow: 0 2px 10px rgba(0,0,0,0.3); z-index: 10000;">
                <h3>Session Expiring Soon</h3>
                <p>Your session will expire in ${warningMinutes} minutes due to inactivity.</p>
                <p>Click anywhere or move your mouse to stay logged in.</p>
                <button onclick="window.sessionTimeout.extend()">Stay Logged In</button>
              </div>
            \`;
            document.body.appendChild(logoutModal);
          } else {
            logoutModal.style.display = 'block';
          }
        }

        function autoLogout() {
          // Log out user
          alert('Your session has expired due to inactivity. You will be logged out for security.');
          window.location.href = '/logout?reason=timeout';
        }

        function extendSession() {
          // Make API call to extend session
          fetch('/api/extend-session', { method: 'POST', credentials: 'include' })
            .then(() => resetTimers())
            .catch(err => console.error('Failed to extend session:', err));
        }

        // Track user activity
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        
        let activityDetected = false;
        function onActivity() {
          if (!activityDetected) {
            activityDetected = true;
            setTimeout(() => {
              activityDetected = false;
              resetTimers();
            }, 1000); // Debounce to 1 second
          }
        }

        events.forEach(event => {
          document.addEventListener(event, onActivity, true);
        });

        // Initialize
        resetTimers();

        // Expose methods
        window.sessionTimeout = {
          extend: extendSession,
          reset: resetTimers
        };
      })();
      </script>
    `;
  }
}

module.exports = SessionTimeoutManager;

// Usage example
/*
const express = require('express');
const session = require('express-session');
const app = express();

// Configure session
app.use(session({
  secret: 'your-secret-key',
  resave: false,
  saveUninitialized: false,
  cookie: {
    maxAge: 15 * 60 * 1000, // 15 minutes
    httpOnly: true,
    secure: true, // HTTPS only
    sameSite: 'strict'
  }
}));

// Initialize session timeout manager
const timeoutManager = new SessionTimeoutManager({
  timeoutMinutes: 15,
  warningMinutes: 2
});

// Use middleware
app.use(timeoutManager.middleware());

// Start monitoring
timeoutManager.startMonitoring(app.sessionStore);

// Extend session endpoint
app.post('/api/extend-session', (req, res) => {
  if (req.session) {
    req.session.touch(); // Update session timestamp
    res.json({ success: true });
  } else {
    res.status(401).json({ error: 'No active session' });
  }
});

// Include client-side script in HTML
app.get('/', (req, res) => {
  res.send(\`
    <html>
      <head><title>HIPAA App</title></head>
      <body>
        <h1>HIPAA-Compliant Application</h1>
        ${SessionTimeoutManager.getClientSideScript(15, 2)}
      </body>
    </html>
  \`);
});
*/

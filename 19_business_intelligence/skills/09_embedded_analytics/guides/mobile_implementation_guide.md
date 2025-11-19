# Mobile Implementation Guide

## React Native Setup

```bash
npm install react-native-webview
npm install @react-native-async-storage/async-storage
```

## Basic Implementation

```javascript
import React, { useState, useEffect } from 'react';
import { View, ActivityIndicator } from 'react-native';
import { WebView } from 'react-native-webview';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function MobileAnalytics({ dashboardId }) {
  const [url, setUrl] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, [dashboardId]);

  async function loadDashboard() {
    const cached = await getCached(dashboardId);
    if (cached && !isExpired(cached)) {
      setUrl(cached.url);
      setLoading(false);
      return;
    }

    const token = await fetchToken();
    const embedUrl = `https://bi.example.com/embed/${dashboardId}?token=${token}&mobile=true`;

    await cache(dashboardId, embedUrl);
    setUrl(embedUrl);
    setLoading(false);
  }

  async function fetchToken() {
    const authToken = await AsyncStorage.getItem('authToken');

    const response = await fetch('https://api.example.com/embed-token', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      }
    });

    const { token } = await response.json();
    return token;
  }

  async function getCached(id) {
    const cached = await AsyncStorage.getItem(`dashboard_${id}`);
    return cached ? JSON.parse(cached) : null;
  }

  async function cache(id, url) {
    await AsyncStorage.setItem(`dashboard_${id}`, JSON.stringify({
      url,
      cachedAt: Date.now(),
      expiresAt: Date.now() + (30 * 60 * 1000)
    }));
  }

  function isExpired(cached) {
    return Date.now() > cached.expiresAt;
  }

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center' }}>
        <ActivityIndicator size="large" color="#0078D4" />
      </View>
    );
  }

  return (
    <WebView
      source={{ uri: url }}
      style={{ flex: 1 }}
      javaScriptEnabled={true}
      domStorageEnabled={true}
      onLoad={() => console.log('Loaded')}
      onError={(error) => console.error('Error:', error)}
    />
  );
}
```

## iOS Native (Swift)

```swift
import WebKit

class AnalyticsViewController: UIViewController {
    var webView: WKWebView!

    override func loadView() {
        let config = WKWebViewConfiguration()
        config.preferences.javaScriptEnabled = true

        webView = WKWebView(frame: .zero, configuration: config)
        view = webView
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        loadDashboard()
    }

    func loadDashboard() {
        getEmbedToken { [weak self] token in
            guard let token = token else { return }

            let url = URL(string: "https://bi.example.com/embed/1?token=\(token)&mobile=true")!
            self?.webView.load(URLRequest(url: url))
        }
    }

    func getEmbedToken(completion: @escaping (String?) -> Void) {
        // Fetch token from API
    }
}
```

## Android Native (Kotlin)

```kotlin
class AnalyticsActivity : AppCompatActivity() {
    private lateinit var webView: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_analytics)

        webView = findViewById(R.id.webView)
        webView.settings.javaScriptEnabled = true

        loadDashboard()
    }

    private fun loadDashboard() {
        getEmbedToken { token ->
            val url = "https://bi.example.com/embed/1?token=$token&mobile=true"
            webView.loadUrl(url)
        }
    }

    private fun getEmbedToken(callback: (String) -> Unit) {
        // Fetch token from API
    }
}
```

## Offline Support

```javascript
import NetInfo from '@react-native-community/netinfo';

class OfflineAnalytics {
  async loadWithOfflineSupport(dashboardId) {
    const isConnected = await NetInfo.fetch()
      .then(state => state.isConnected);

    if (!isConnected) {
      return this.loadFromCache(dashboardId);
    }

    try {
      const data = await this.fetchFromNetwork(dashboardId);
      await this.cacheData(dashboardId, data);
      return data;
    } catch (error) {
      return this.loadFromCache(dashboardId);
    }
  }
}
```

## Mobile Checklist
- [ ] Touch-optimized controls
- [ ] Responsive design
- [ ] Offline caching
- [ ] Certificate pinning
- [ ] Secure token storage
- [ ] Low data mode
- [ ] Battery optimization
- [ ] Test on real devices

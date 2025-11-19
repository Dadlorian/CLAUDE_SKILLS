# Mobile Embedding for Analytics

## Overview

Best practices and implementation patterns for embedding analytics in mobile applications (iOS and Android).

## Mobile-Specific Considerations

### Challenges
- Limited screen size
- Touch interactions vs mouse/keyboard
- Intermittent connectivity
- Battery consumption
- Data usage constraints
- Performance on lower-end devices

### Solutions
- Responsive design
- Touch-optimized controls
- Offline capability with caching
- Lazy loading and progressive enhancement
- Optimized data transfer
- Native SDK integration

---

## iOS Implementation

### 1. Using WKWebView for iframe Embedding

```swift
import UIKit
import WebKit

class AnalyticsDashboardViewController: UIViewController, WKNavigationDelegate {

    var webView: WKWebView!

    override func loadView() {
        // Configure WKWebView
        let webConfiguration = WKWebViewConfiguration()

        // Allow inline media playback
        webConfiguration.allowsInlineMediaPlayback = true

        // Configure to work with analytics
        webConfiguration.preferences.javaScriptEnabled = true

        webView = WKWebView(frame: .zero, configuration: webConfiguration)
        webView.navigationDelegate = self
        view = webView
    }

    override func viewDidLoad() {
        super.viewDidLoad()

        loadDashboard()
    }

    func loadDashboard() {
        // Get embed token from backend
        getEmbedToken { [weak self] token, embedUrl in
            guard let self = self, let token = token, let embedUrl = embedUrl else {
                return
            }

            // Construct URL with token
            var urlComponents = URLComponents(string: embedUrl)
            urlComponents?.queryItems = [
                URLQueryItem(name: "token", value: token),
                URLQueryItem(name: "mobile", value: "true"),
                URLQueryItem(name: "device", value: "ios")
            ]

            if let url = urlComponents?.url {
                let request = URLRequest(url: url)
                self.webView.load(request)
            }
        }
    }

    func getEmbedToken(completion: @escaping (String?, String?) -> Void) {
        // Call your backend API
        guard let url = URL(string: "https://api.yourapp.com/embed-token") else {
            completion(nil, nil)
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"

        // Add auth headers
        if let authToken = UserDefaults.standard.string(forKey: "authToken") {
            request.setValue("Bearer \(authToken)", forHTTPHeaderField: "Authorization")
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            guard let data = data, error == nil else {
                completion(nil, nil)
                return
            }

            do {
                let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
                let token = json?["token"] as? String
                let embedUrl = json?["embedUrl"] as? String
                completion(token, embedUrl)
            } catch {
                completion(nil, nil)
            }
        }.resume()
    }

    // Handle navigation events
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        print("Dashboard loaded")

        // Hide loading indicator
        hideLoadingIndicator()
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        print("Dashboard failed to load: \(error)")

        // Show error message
        showError(message: "Failed to load dashboard")
    }
}
```

### 2. Power BI Mobile SDK (iOS)

```swift
import PowerBI

class PowerBIDashboardViewController: UIViewController {

    var reportView: UIView!

    override func viewDidLoad() {
        super.viewDidLoad()

        embedPowerBIReport()
    }

    func embedPowerBIReport() {
        // Get embed token and config
        getEmbedConfig { [weak self] config in
            guard let self = self, let config = config else {
                return
            }

            // Create embed configuration
            let embedConfig = EmbedConfiguration(
                embedUrl: config.embedUrl,
                embedToken: config.token,
                reportId: config.reportId
            )

            // Set view size for mobile
            embedConfig.settings = Settings(
                filterPaneEnabled: false,
                navContentPaneEnabled: false,
                layoutType: .mobilePortrait
            )

            // Create report view
            reportView = PowerBIReportView(frame: view.bounds, configuration: embedConfig)

            // Handle events
            (reportView as? PowerBIReportView)?.onLoaded = {
                print("Report loaded")
            }

            (reportView as? PowerBIReportView)?.onError = { error in
                print("Error: \(error)")
            }

            // Add to view hierarchy
            view.addSubview(reportView)

            // Auto layout
            reportView.translatesAutoresizingMaskIntoConstraints = false
            NSLayoutConstraint.activate([
                reportView.topAnchor.constraint(equalTo: view.topAnchor),
                reportView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
                reportView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
                reportView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
            ])
        }
    }

    func getEmbedConfig(completion: @escaping ([String: String]?) -> Void) {
        // Fetch from your backend
        // ...
    }
}
```

### 3. Offline Support with Caching

```swift
import RealmSwift

class DashboardCache {

    // Realm model for cached dashboard data
    class CachedDashboard: Object {
        @Persisted(primaryKey: true) var id: String
        @Persisted var data: Data
        @Persisted var cachedAt: Date
        @Persisted var expiresAt: Date
    }

    func getCachedDashboard(id: String) -> Data? {
        let realm = try! Realm()

        guard let cached = realm.object(ofType: CachedDashboard.self, forPrimaryKey: id) else {
            return nil
        }

        // Check if expired
        if cached.expiresAt < Date() {
            try! realm.write {
                realm.delete(cached)
            }
            return nil
        }

        return cached.data
    }

    func cacheDashboard(id: String, data: Data, ttl: TimeInterval = 3600) {
        let realm = try! Realm()

        let cached = CachedDashboard()
        cached.id = id
        cached.data = data
        cached.cachedAt = Date()
        cached.expiresAt = Date().addingTimeInterval(ttl)

        try! realm.write {
            realm.add(cached, update: .modified)
        }
    }

    func loadDashboardWithOfflineSupport(id: String, completion: @escaping (Data?) -> Void) {
        // Try cache first
        if let cached = getCachedDashboard(id: id) {
            print("Loading from cache")
            completion(cached)
            return
        }

        // Fetch from network
        fetchDashboardData(id: id) { [weak self] data in
            guard let data = data else {
                completion(nil)
                return
            }

            // Cache for offline use
            self?.cacheDashboard(id: id, data: data)

            completion(data)
        }
    }

    func fetchDashboardData(id: String, completion: @escaping (Data?) -> Void) {
        // Network request
        // ...
    }
}
```

---

## Android Implementation

### 1. Using WebView for iframe Embedding

```kotlin
import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

class AnalyticsDashboardActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        webView = findViewById(R.id.webView)

        // Configure WebView
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            loadWithOverviewMode = true
            useWideViewPort = true
            builtInZoomControls = true
            displayZoomControls = false
        }

        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                println("Dashboard loaded")
                hideLoadingIndicator()
            }

            override fun onReceivedError(
                view: WebView?,
                errorCode: Int,
                description: String?,
                failingUrl: String?
            ) {
                super.onReceivedError(view, errorCode, description, failingUrl)
                showError("Failed to load dashboard: $description")
            }
        }

        loadDashboard()
    }

    private fun loadDashboard() {
        // Get embed token
        getEmbedToken { token, embedUrl ->
            if (token != null && embedUrl != null) {
                val url = "$embedUrl?token=$token&mobile=true&device=android"
                webView.loadUrl(url)
            }
        }
    }

    private fun getEmbedToken(callback: (String?, String?) -> Unit) {
        // Call your backend API
        // ...
    }

    private fun hideLoadingIndicator() {
        // Hide loading spinner
    }

    private fun showError(message: String) {
        // Show error message
    }
}
```

### 2. Power BI Mobile SDK (Android)

```kotlin
import com.microsoft.powerbi.sampleapp.EmbedConfig
import com.microsoft.powerbi.sampleapp.PowerBIReportView

class PowerBIDashboardActivity : AppCompatActivity() {

    private lateinit var reportView: PowerBIReportView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_powerbi)

        reportView = findViewById(R.id.reportView)

        embedPowerBIReport()
    }

    private fun embedPowerBIReport() {
        getEmbedConfig { config ->
            config?.let {
                val embedConfig = EmbedConfig(
                    embedUrl = it.embedUrl,
                    embedToken = it.token,
                    reportId = it.reportId
                )

                // Mobile-optimized settings
                embedConfig.settings = Settings(
                    filterPaneEnabled = false,
                    navContentPaneEnabled = false,
                    layoutType = LayoutType.MOBILE_PORTRAIT
                )

                // Set callbacks
                reportView.onLoaded = {
                    println("Report loaded")
                }

                reportView.onError = { error ->
                    println("Error: $error")
                }

                // Load report
                reportView.load(embedConfig)
            }
        }
    }

    private fun getEmbedConfig(callback: (EmbedConfig?) -> Unit) {
        // Fetch from backend
        // ...
    }
}
```

### 3. Offline Support with Room

```kotlin
import androidx.room.*

@Entity(tableName = "cached_dashboards")
data class CachedDashboard(
    @PrimaryKey val id: String,
    val data: ByteArray,
    val cachedAt: Long,
    val expiresAt: Long
)

@Dao
interface DashboardCacheDao {
    @Query("SELECT * FROM cached_dashboards WHERE id = :id AND expiresAt > :now")
    fun getCachedDashboard(id: String, now: Long): CachedDashboard?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    fun cacheDashboard(dashboard: CachedDashboard)

    @Query("DELETE FROM cached_dashboards WHERE expiresAt < :now")
    fun cleanExpired(now: Long)
}

@Database(entities = [CachedDashboard::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun dashboardCacheDao(): DashboardCacheDao
}

class DashboardCache(private val dao: DashboardCacheDao) {

    fun getCachedDashboard(id: String): ByteArray? {
        val now = System.currentTimeMillis()
        return dao.getCachedDashboard(id, now)?.data
    }

    fun cacheDashboard(id: String, data: ByteArray, ttl: Long = 3600000) {
        val now = System.currentTimeMillis()
        val dashboard = CachedDashboard(
            id = id,
            data = data,
            cachedAt = now,
            expiresAt = now + ttl
        )
        dao.cacheDashboard(dashboard)
    }

    fun loadDashboardWithOfflineSupport(
        id: String,
        callback: (ByteArray?) -> Unit
    ) {
        // Try cache first
        getCachedDashboard(id)?.let {
            println("Loading from cache")
            callback(it)
            return
        }

        // Fetch from network
        fetchDashboardData(id) { data ->
            data?.let {
                cacheDashboard(id, it)
            }
            callback(data)
        }
    }

    private fun fetchDashboardData(id: String, callback: (ByteArray?) -> Unit) {
        // Network request
        // ...
    }
}
```

---

## React Native Implementation

### Cross-Platform Embedding

```javascript
import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, Alert } from 'react-native';
import { WebView } from 'react-native-webview';
import AsyncStorage from '@react-native-async-storage/async-storage';

const AnalyticsDashboard = ({ dashboardId }) => {
  const [embedUrl, setEmbedUrl] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, [dashboardId]);

  const loadDashboard = async () => {
    // Check cache first
    const cached = await getCachedDashboard(dashboardId);
    if (cached) {
      setEmbedUrl(cached);
      setLoading(false);
      return;
    }

    // Fetch embed token
    try {
      const response = await fetch('https://api.yourapp.com/embed-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await getAuthToken()}`
        },
        body: JSON.stringify({ dashboardId })
      });

      const { token, embedUrl: url } = await response.json();

      const fullUrl = `${url}?token=${token}&mobile=true`;

      // Cache for offline
      await cacheDashboard(dashboardId, fullUrl);

      setEmbedUrl(fullUrl);
    } catch (error) {
      Alert.alert('Error', 'Failed to load dashboard');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getCachedDashboard = async (id) => {
    try {
      const cached = await AsyncStorage.getItem(`dashboard_${id}`);
      if (cached) {
        const { url, expiresAt } = JSON.parse(cached);
        if (Date.now() < expiresAt) {
          return url;
        }
      }
    } catch (error) {
      console.error('Cache error:', error);
    }
    return null;
  };

  const cacheDashboard = async (id, url) => {
    try {
      await AsyncStorage.setItem(
        `dashboard_${id}`,
        JSON.stringify({
          url,
          expiresAt: Date.now() + (30 * 60 * 1000) // 30 minutes
        })
      );
    } catch (error) {
      console.error('Cache error:', error);
    }
  };

  const getAuthToken = async () => {
    return await AsyncStorage.getItem('authToken');
  };

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#0000ff" />
      </View>
    );
  }

  return (
    <WebView
      source={{ uri: embedUrl }}
      style={{ flex: 1 }}
      onLoad={() => console.log('Dashboard loaded')}
      onError={(error) => {
        console.error('WebView error:', error);
        Alert.alert('Error', 'Failed to display dashboard');
      }}
      javaScriptEnabled={true}
      domStorageEnabled={true}
      startInLoadingState={true}
      renderLoading={() => <ActivityIndicator />}
    />
  );
};

export default AnalyticsDashboard;
```

---

## Mobile Optimization Techniques

### 1. Responsive Design

```javascript
// Detect mobile device and adjust embed config
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

const embedConfig = {
  embedUrl: dashboardUrl,
  token: embedToken,
  settings: {
    // Mobile-specific settings
    filterPaneEnabled: false,  // Hide filters on mobile
    navContentPaneEnabled: !isMobile, // Hide nav on mobile
    layoutType: isMobile ? 'mobilePortrait' : 'master',

    // Touch-optimized
    background: models.BackgroundType.Transparent,

    // Performance
    visualRenderedEvents: false // Reduce events
  }
};

// Adjust based on orientation
window.addEventListener('orientationchange', () => {
  const isPortrait = window.orientation === 0;

  embedAPI.updateSettings({
    layoutType: isPortrait ? 'mobilePortrait' : 'mobileLandscape'
  });
});
```

### 2. Data Compression

```javascript
// Backend: Compress dashboard data for mobile
app.get('/api/mobile/dashboard/:id', async (req, res) => {
  const data = await getDashboardData(req.params.id);

  // Reduce data size for mobile
  const mobileData = {
    ...data,
    // Limit data points
    chartData: data.chartData.slice(-100), // Only last 100 points

    // Lower precision
    values: data.values.map(v => Math.round(v * 100) / 100),

    // Remove unnecessary metadata
    metadata: undefined
  };

  // Compress
  const compressed = zlib.gzipSync(JSON.stringify(mobileData));

  res.set('Content-Encoding', 'gzip');
  res.send(compressed);
});
```

### 3. Progressive Loading

```javascript
// Load minimal data first, then details
const MobileAnalytics = () => {
  const [summary, setSummary] = useState(null);
  const [details, setDetails] = useState(null);

  useEffect(() => {
    // Load summary immediately
    loadSummary().then(setSummary);

    // Load details after summary
    setTimeout(() => {
      loadDetails().then(setDetails);
    }, 1000);
  }, []);

  const loadSummary = async () => {
    const response = await fetch('/api/mobile/dashboard/summary');
    return response.json();
  };

  const loadDetails = async () => {
    const response = await fetch('/api/mobile/dashboard/details');
    return response.json();
  };

  return (
    <View>
      {summary && <SummaryView data={summary} />}
      {details ? <DetailsView data={details} /> : <LoadingIndicator />}
    </View>
  );
};
```

---

## Mobile Best Practices Checklist

### Performance
- [ ] Implement lazy loading
- [ ] Use progressive enhancement
- [ ] Minimize data transfer
- [ ] Compress responses
- [ ] Optimize images
- [ ] Cache aggressively

### User Experience
- [ ] Touch-optimized controls
- [ ] Responsive design
- [ ] Portrait and landscape support
- [ ] Simplified navigation
- [ ] Minimal text input
- [ ] Large tap targets (min 44x44 pts)

### Offline Support
- [ ] Cache dashboard metadata
- [ ] Cache recent data
- [ ] Offline indicator
- [ ] Sync when online
- [ ] Handle stale data

### Security
- [ ] Secure token storage (Keychain/KeyStore)
- [ ] Certificate pinning
- [ ] App transport security
- [ ] Biometric authentication option

### Testing
- [ ] Test on various screen sizes
- [ ] Test on low-end devices
- [ ] Test with slow network
- [ ] Test offline functionality
- [ ] Test different orientations
- [ ] Battery consumption testing

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Production-Ready Java API Client
 * Implements OAuth2 authentication, retry logic, and comprehensive error handling
 *
 * @author API Team
 * @version 1.0
 */
public class JavaAPIClient {

    private static final Logger LOGGER = Logger.getLogger(JavaAPIClient.class.getName());

    /**
     * API Client Configuration
     */
    public static class APIConfig {
        public final String baseUrl;
        public final String clientId;
        public final String clientSecret;
        public final Duration timeout;
        public final int maxRetries;
        public final double backoffFactor;

        public APIConfig(String baseUrl, String clientId, String clientSecret,
                        Duration timeout, int maxRetries, double backoffFactor) {
            this.baseUrl = baseUrl;
            this.clientId = clientId;
            this.clientSecret = clientSecret;
            this.timeout = timeout;
            this.maxRetries = maxRetries;
            this.backoffFactor = backoffFactor;
        }
    }

    /**
     * OAuth2 Token Response
     */
    public static class TokenResponse {
        public String access_token;
        public String refresh_token;
        public int expires_in;
        public String token_type;
    }

    /**
     * OAuth2 Authentication Client
     */
    public static class OAuth2Client {
        private final String clientId;
        private final String clientSecret;
        private String accessToken;
        private String refreshToken;
        private Instant tokenExpiry;

        public OAuth2Client(String clientId, String clientSecret) {
            this.clientId = clientId;
            this.clientSecret = clientSecret;
        }

        /**
         * Authenticate and retrieve access token
         *
         * @param authEndpoint OAuth2 token endpoint
         * @param scopes Requested scopes
         * @return Token response
         * @throws IOException If authentication fails
         */
        public TokenResponse getToken(String authEndpoint, String... scopes) throws IOException {
            HttpClient client = HttpClient.newBuilder()
                    .connectTimeout(Duration.ofSeconds(30))
                    .build();

            StringBuilder scopeBuilder = new StringBuilder();
            for (int i = 0; i < scopes.length; i++) {
                if (i > 0) scopeBuilder.append(" ");
                scopeBuilder.append(scopes[i]);
            }

            String body = String.format(
                    "grant_type=client_credentials&client_id=%s&client_secret=%s&scope=%s",
                    URLEncoder.encode(clientId, StandardCharsets.UTF_8),
                    URLEncoder.encode(clientSecret, StandardCharsets.UTF_8),
                    URLEncoder.encode(scopeBuilder.toString(), StandardCharsets.UTF_8)
            );

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(authEndpoint))
                    .header("Content-Type", "application/x-www-form-urlencoded")
                    .POST(HttpRequest.BodyPublishers.ofString(body))
                    .timeout(Duration.ofSeconds(30))
                    .build();

            try {
                HttpResponse<String> response = client.send(request,
                        HttpResponse.BodyHandlers.ofString());

                if (response.statusCode() != 200) {
                    throw new IOException("Authentication failed: " + response.statusCode());
                }

                Gson gson = new Gson();
                TokenResponse tokenResponse = gson.fromJson(response.body(), TokenResponse.class);

                this.accessToken = tokenResponse.access_token;
                this.refreshToken = tokenResponse.refresh_token;
                this.tokenExpiry = Instant.now().plusSeconds(tokenResponse.expires_in);

                LOGGER.log(Level.INFO, "Successfully authenticated. Token expires at " + tokenExpiry);
                return tokenResponse;

            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new IOException("Authentication interrupted", e);
            }
        }

        /**
         * Refresh access token
         *
         * @param authEndpoint OAuth2 token endpoint
         * @return New token response
         * @throws IOException If refresh fails
         */
        public TokenResponse refresh(String authEndpoint) throws IOException {
            if (refreshToken == null) {
                throw new IllegalStateException("No refresh token available");
            }

            HttpClient client = HttpClient.newBuilder()
                    .connectTimeout(Duration.ofSeconds(30))
                    .build();

            String body = String.format(
                    "grant_type=refresh_token&refresh_token=%s&client_id=%s&client_secret=%s",
                    URLEncoder.encode(refreshToken, StandardCharsets.UTF_8),
                    URLEncoder.encode(clientId, StandardCharsets.UTF_8),
                    URLEncoder.encode(clientSecret, StandardCharsets.UTF_8)
            );

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(authEndpoint))
                    .header("Content-Type", "application/x-www-form-urlencoded")
                    .POST(HttpRequest.BodyPublishers.ofString(body))
                    .timeout(Duration.ofSeconds(30))
                    .build();

            try {
                HttpResponse<String> response = client.send(request,
                        HttpResponse.BodyHandlers.ofString());

                if (response.statusCode() != 200) {
                    throw new IOException("Token refresh failed: " + response.statusCode());
                }

                Gson gson = new Gson();
                return gson.fromJson(response.body(), TokenResponse.class);

            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new IOException("Refresh interrupted", e);
            }
        }

        /**
         * Check if token is expired
         *
         * @return True if token is expired
         */
        public boolean isTokenExpired() {
            return tokenExpiry == null || Instant.now().isAfter(tokenExpiry);
        }

        /**
         * Get current access token
         *
         * @return Access token
         */
        public String getAccessToken() {
            return accessToken;
        }
    }

    /**
     * Production-Ready API Client
     */
    public static class APIClient {
        private final APIConfig config;
        private final OAuth2Client oauth2;
        private final HttpClient httpClient;
        private final Gson gson;

        public APIClient(APIConfig config, OAuth2Client oauth2) {
            this.config = config;
            this.oauth2 = oauth2;
            this.httpClient = HttpClient.newBuilder()
                    .connectTimeout(config.timeout)
                    .build();
            this.gson = new Gson();
        }

        /**
         * Get request headers with authentication
         *
         * @return Headers map
         */
        private HttpRequest.Builder getHeaders() {
            HttpRequest.Builder builder = HttpRequest.newBuilder()
                    .header("Content-Type", "application/json")
                    .header("Accept", "application/json")
                    .header("User-Agent", "JavaAPIClient/1.0");

            if (oauth2 != null && oauth2.getAccessToken() != null) {
                builder.header("Authorization", "Bearer " + oauth2.getAccessToken());
            }

            return builder;
        }

        /**
         * Make HTTP request with retry logic
         *
         * @param method HTTP method
         * @param endpoint API endpoint
         * @param body Request body (optional)
         * @param params Query parameters (optional)
         * @return Response body as string
         * @throws IOException If request fails
         */
        private String makeRequest(String method, String endpoint, String body,
                                  Map<String, String> params) throws IOException {
            String url = buildUrl(endpoint, params);
            int attempt = 0;

            while (attempt <= config.maxRetries) {
                try {
                    HttpRequest.Builder requestBuilder = getHeaders()
                            .uri(URI.create(url))
                            .timeout(config.timeout);

                    if ("GET".equals(method)) {
                        requestBuilder.GET();
                    } else if ("POST".equals(method)) {
                        requestBuilder.POST(HttpRequest.BodyPublishers.ofString(body != null ? body : ""));
                    } else if ("PATCH".equals(method)) {
                        requestBuilder.method("PATCH", HttpRequest.BodyPublishers.ofString(body != null ? body : ""));
                    } else if ("DELETE".equals(method)) {
                        requestBuilder.DELETE();
                    }

                    HttpRequest request = requestBuilder.build();
                    HttpResponse<String> response = httpClient.send(request,
                            HttpResponse.BodyHandlers.ofString());

                    LOGGER.log(Level.FINE, method + " " + endpoint + " -> " + response.statusCode());

                    handleResponse(response);
                    return response.body();

                } catch (IOException | InterruptedException e) {
                    attempt++;
                    if (attempt <= config.maxRetries) {
                        long sleepTime = (long) Math.pow(config.backoffFactor, attempt - 1) * 1000;
                        try {
                            Thread.sleep(sleepTime);
                        } catch (InterruptedException ie) {
                            Thread.currentThread().interrupt();
                            throw new IOException("Interrupted", ie);
                        }
                    } else {
                        LOGGER.log(Level.SEVERE, "Request failed: " + method + " " + endpoint, e);
                        throw new IOException("Request failed after " + config.maxRetries + " retries", e);
                    }
                }
            }

            throw new IOException("Request failed after maximum retries");
        }

        /**
         * Handle HTTP response status codes
         *
         * @param response HTTP response
         * @throws IOException If response indicates error
         */
        private void handleResponse(HttpResponse<String> response) throws IOException {
            switch (response.statusCode()) {
                case 200:
                case 201:
                case 202:
                    return;
                case 401:
                    throw new IOException("Unauthorized - invalid or expired token");
                case 403:
                    throw new IOException("Insufficient permissions");
                case 404:
                    throw new IOException("Resource not found");
                case 429:
                    throw new IOException("Rate limit exceeded");
                default:
                    if (response.statusCode() >= 500) {
                        throw new IOException("Server error: " + response.statusCode());
                    }
                    throw new IOException("HTTP error: " + response.statusCode());
            }
        }

        /**
         * Build complete URL with parameters
         *
         * @param endpoint API endpoint
         * @param params Query parameters
         * @return Complete URL
         */
        private String buildUrl(String endpoint, Map<String, String> params) {
            StringBuilder url = new StringBuilder(config.baseUrl).append(endpoint);

            if (params != null && !params.isEmpty()) {
                url.append("?");
                params.forEach((key, value) -> {
                    try {
                        url.append(key).append("=")
                                .append(URLEncoder.encode(value, StandardCharsets.UTF_8))
                                .append("&");
                    } catch (Exception e) {
                        LOGGER.log(Level.WARNING, "Error encoding parameter", e);
                    }
                });
                url.deleteCharAt(url.length() - 1);
            }

            return url.toString();
        }

        /**
         * Make GET request
         *
         * @param endpoint API endpoint
         * @param params Query parameters
         * @return Parsed JSON response
         * @throws IOException If request fails
         */
        public JsonObject get(String endpoint, Map<String, String> params) throws IOException {
            String response = makeRequest("GET", endpoint, null, params);
            return gson.fromJson(response, JsonObject.class);
        }

        /**
         * Make POST request
         *
         * @param endpoint API endpoint
         * @param body Request body
         * @return Parsed JSON response
         * @throws IOException If request fails
         */
        public JsonObject post(String endpoint, JsonObject body) throws IOException {
            String response = makeRequest("POST", endpoint, body.toString(), null);
            return gson.fromJson(response, JsonObject.class);
        }

        /**
         * Make PATCH request
         *
         * @param endpoint API endpoint
         * @param body Request body
         * @return Parsed JSON response
         * @throws IOException If request fails
         */
        public JsonObject patch(String endpoint, JsonObject body) throws IOException {
            String response = makeRequest("PATCH", endpoint, body.toString(), null);
            return gson.fromJson(response, JsonObject.class);
        }

        /**
         * Make DELETE request
         *
         * @param endpoint API endpoint
         * @return Parsed JSON response
         * @throws IOException If request fails
         */
        public JsonObject delete(String endpoint) throws IOException {
            String response = makeRequest("DELETE", endpoint, null, null);
            return response.isEmpty() ? new JsonObject() : gson.fromJson(response, JsonObject.class);
        }
    }

    /**
     * Specialized client for user operations
     */
    public static class UserClient {
        private final APIClient apiClient;

        public UserClient(APIClient apiClient) {
            this.apiClient = apiClient;
        }

        /**
         * List users with pagination
         *
         * @param page Page number
         * @param limit Results per page
         * @return Paginated user list
         * @throws IOException If request fails
         */
        public JsonObject listUsers(int page, int limit) throws IOException {
            Map<String, String> params = new HashMap<>();
            params.put("page", String.valueOf(page));
            params.put("limit", String.valueOf(limit));
            return apiClient.get("/users", params);
        }

        /**
         * Create new user
         *
         * @param userData User attributes
         * @return Created user
         * @throws IOException If request fails
         */
        public JsonObject createUser(JsonObject userData) throws IOException {
            return apiClient.post("/users", userData);
        }

        /**
         * Get user by ID
         *
         * @param userId User ID
         * @return User data
         * @throws IOException If request fails
         */
        public JsonObject getUser(String userId) throws IOException {
            return apiClient.get("/users/" + userId, null);
        }

        /**
         * Update user
         *
         * @param userId User ID
         * @param updates Fields to update
         * @return Updated user
         * @throws IOException If request fails
         */
        public JsonObject updateUser(String userId, JsonObject updates) throws IOException {
            return apiClient.patch("/users/" + userId, updates);
        }

        /**
         * Delete user
         *
         * @param userId User ID
         * @return Deletion confirmation
         * @throws IOException If request fails
         */
        public JsonObject deleteUser(String userId) throws IOException {
            return apiClient.delete("/users/" + userId);
        }
    }

    /**
     * Example usage
     */
    public static void main(String[] args) {
        try {
            // Initialize OAuth2 client
            OAuth2Client oauth2 = new OAuth2Client(
                    "your-client-id",
                    "your-client-secret"
            );

            // Authenticate
            oauth2.getToken(
                    "https://auth.example.com/oauth/token",
                    "users.read", "users.write"
            );

            // Create API client
            APIConfig config = new APIConfig(
                    "https://api.example.com/v1",
                    "your-client-id",
                    "your-client-secret",
                    Duration.ofSeconds(30),
                    3,
                    0.5
            );

            APIClient apiClient = new APIClient(config, oauth2);

            // List users
            Map<String, String> params = new HashMap<>();
            params.put("limit", "10");
            JsonObject users = apiClient.get("/users", params);
            LOGGER.log(Level.INFO, "Retrieved users: " + users.toString());

            // Create user
            JsonObject userData = new JsonObject();
            userData.addProperty("firstName", "John");
            userData.addProperty("lastName", "Doe");
            userData.addProperty("email", "john@example.com");

            JsonObject newUser = apiClient.post("/users", userData);
            LOGGER.log(Level.INFO, "Created user: " + newUser.toString());

            // Use specialized client
            UserClient userClient = new UserClient(apiClient);
            JsonObject user = userClient.getUser("123");
            LOGGER.log(Level.INFO, "Retrieved user: " + user.toString());

        } catch (IOException e) {
            LOGGER.log(Level.SEVERE, "Error: " + e.getMessage(), e);
            System.exit(1);
        }
    }
}

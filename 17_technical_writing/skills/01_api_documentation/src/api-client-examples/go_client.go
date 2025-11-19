package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"path"
	"time"
)

// APIConfig holds API client configuration
type APIConfig struct {
	BaseURL       string
	ClientID      string
	ClientSecret  string
	Timeout       time.Duration
	MaxRetries    int
	BackoffFactor float64
}

// OAuth2Client handles OAuth2 authentication
type OAuth2Client struct {
	clientID     string
	clientSecret string
	accessToken  string
	refreshToken string
	tokenExpiry  time.Time
	logger       *log.Logger
}

// TokenResponse represents OAuth2 token response
type TokenResponse struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	ExpiresIn    int    `json:"expires_in"`
	TokenType    string `json:"token_type"`
}

// NewOAuth2Client creates new OAuth2 client
func NewOAuth2Client(clientID, clientSecret string, logger *log.Logger) *OAuth2Client {
	return &OAuth2Client{
		clientID:     clientID,
		clientSecret: clientSecret,
		logger:       logger,
	}
}

// GetToken authenticates and retrieves access token
func (o *OAuth2Client) GetToken(authEndpoint string, scopes []string) (*TokenResponse, error) {
	client := &http.Client{
		Timeout: 30 * time.Second,
	}

	// Prepare OAuth2 request
	data := url.Values{}
	data.Set("grant_type", "client_credentials")
	data.Set("client_id", o.clientID)
	data.Set("client_secret", o.clientSecret)
	for _, scope := range scopes {
		data.Add("scope", scope)
	}

	resp, err := client.PostForm(authEndpoint, data)
	if err != nil {
		o.logger.Printf("Authentication request failed: %v", err)
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		o.logger.Printf("Authentication failed: %d - %s", resp.StatusCode, string(body))
		return nil, fmt.Errorf("authentication failed: status %d", resp.StatusCode)
	}

	var tokenResp TokenResponse
	if err := json.NewDecoder(resp.Body).Decode(&tokenResp); err != nil {
		o.logger.Printf("Failed to parse token response: %v", err)
		return nil, err
	}

	// Store token and calculate expiry
	o.accessToken = tokenResp.AccessToken
	o.refreshToken = tokenResp.RefreshToken
	o.tokenExpiry = time.Now().Add(time.Duration(tokenResp.ExpiresIn) * time.Second)

	o.logger.Printf("Successfully authenticated. Token expires at %v", o.tokenExpiry)
	return &tokenResp, nil
}

// RefreshToken refreshes the access token
func (o *OAuth2Client) RefreshToken(authEndpoint string) (*TokenResponse, error) {
	if o.refreshToken == "" {
		return nil, fmt.Errorf("no refresh token available")
	}

	client := &http.Client{
		Timeout: 30 * time.Second,
	}

	data := url.Values{}
	data.Set("grant_type", "refresh_token")
	data.Set("refresh_token", o.refreshToken)
	data.Set("client_id", o.clientID)
	data.Set("client_secret", o.clientSecret)

	resp, err := client.PostForm(authEndpoint, data)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("token refresh failed: status %d", resp.StatusCode)
	}

	var tokenResp TokenResponse
	if err := json.NewDecoder(resp.Body).Decode(&tokenResp); err != nil {
		return nil, err
	}

	o.accessToken = tokenResp.AccessToken
	o.refreshToken = tokenResp.RefreshToken
	o.tokenExpiry = time.Now().Add(time.Duration(tokenResp.ExpiresIn) * time.Second)

	return &tokenResp, nil
}

// IsTokenExpired checks if current token is expired
func (o *OAuth2Client) IsTokenExpired() bool {
	return time.Now().After(o.tokenExpiry)
}

// GetAccessToken returns the current access token
func (o *OAuth2Client) GetAccessToken() string {
	return o.accessToken
}

// APIClient provides methods for API interaction
type APIClient struct {
	baseURL     string
	oauth2      *OAuth2Client
	httpClient  *http.Client
	maxRetries  int
	backoffFunc func(int) time.Duration
	logger      *log.Logger
}

// NewAPIClient creates new API client
func NewAPIClient(config APIConfig, oauth2 *OAuth2Client, logger *log.Logger) *APIClient {
	if logger == nil {
		logger = log.New(io.Discard, "", 0)
	}

	return &APIClient{
		baseURL:    config.BaseURL,
		oauth2:     oauth2,
		maxRetries: config.MaxRetries,
		httpClient: &http.Client{
			Timeout: config.Timeout,
		},
		backoffFunc: func(attempt int) time.Duration {
			return time.Duration(time.Duration(int(config.BackoffFactor))^attempt) * time.Second
		},
		logger: logger,
	}
}

// getHeaders prepares request headers with authentication
func (a *APIClient) getHeaders() map[string]string {
	headers := map[string]string{
		"Content-Type": "application/json",
		"Accept":       "application/json",
		"User-Agent":   "GoAPIClient/1.0",
	}

	if a.oauth2 != nil && a.oauth2.accessToken != "" {
		headers["Authorization"] = fmt.Sprintf("Bearer %s", a.oauth2.accessToken)
	}

	return headers
}

// buildURL constructs full request URL
func (a *APIClient) buildURL(endpoint string, params map[string]string) string {
	u, _ := url.Parse(a.baseURL)
	u.Path = path.Join(u.Path, endpoint)

	if len(params) > 0 {
		q := u.Query()
		for k, v := range params {
			q.Add(k, v)
		}
		u.RawQuery = q.Encode()
	}

	return u.String()
}

// makeRequest makes HTTP request with retry logic
func (a *APIClient) makeRequest(method, endpoint string, body interface{}, params map[string]string) (*http.Response, error) {
	var bodyReader io.Reader

	if body != nil {
		jsonBody, _ := json.Marshal(body)
		bodyReader = bytes.NewReader(jsonBody)
	}

	url := a.buildURL(endpoint, params)

	for attempt := 0; attempt <= a.maxRetries; attempt++ {
		req, _ := http.NewRequest(method, url, bodyReader)

		// Set headers
		for k, v := range a.getHeaders() {
			req.Header.Set(k, v)
		}

		resp, err := a.httpClient.Do(req)
		if err != nil {
			if attempt < a.maxRetries {
				time.Sleep(a.backoffFunc(attempt))
				continue
			}
			a.logger.Printf("Request failed: %s %s - %v", method, endpoint, err)
			return nil, err
		}

		// Check response status
		if resp.StatusCode >= 500 || resp.StatusCode == 429 {
			if attempt < a.maxRetries {
				resp.Body.Close()
				time.Sleep(a.backoffFunc(attempt))
				continue
			}
		}

		a.logger.Printf("%s %s -> %d", method, endpoint, resp.StatusCode)
		return resp, nil
	}

	return nil, fmt.Errorf("request failed after %d retries", a.maxRetries)
}

// handleResponse parses and validates HTTP response
func (a *APIClient) handleResponse(resp *http.Response) (map[string]interface{}, error) {
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)

	switch resp.StatusCode {
	case http.StatusOK, http.StatusCreated, http.StatusAccepted:
		var result map[string]interface{}
		if len(body) > 0 {
			json.Unmarshal(body, &result)
		}
		return result, nil
	case http.StatusUnauthorized:
		return nil, fmt.Errorf("unauthorized - invalid or expired token")
	case http.StatusForbidden:
		return nil, fmt.Errorf("insufficient permissions")
	case http.StatusNotFound:
		return nil, fmt.Errorf("resource not found")
	case http.StatusTooManyRequests:
		return nil, fmt.Errorf("rate limit exceeded")
	default:
		if resp.StatusCode >= 500 {
			return nil, fmt.Errorf("server error: %d", resp.StatusCode)
		}
		return nil, fmt.Errorf("HTTP error: %d", resp.StatusCode)
	}
}

// Get makes GET request
func (a *APIClient) Get(endpoint string, params map[string]string) (map[string]interface{}, error) {
	resp, err := a.makeRequest("GET", endpoint, nil, params)
	if err != nil {
		return nil, err
	}
	return a.handleResponse(resp)
}

// Post makes POST request
func (a *APIClient) Post(endpoint string, body interface{}) (map[string]interface{}, error) {
	resp, err := a.makeRequest("POST", endpoint, body, nil)
	if err != nil {
		return nil, err
	}
	return a.handleResponse(resp)
}

// Patch makes PATCH request
func (a *APIClient) Patch(endpoint string, body interface{}) (map[string]interface{}, error) {
	resp, err := a.makeRequest("PATCH", endpoint, body, nil)
	if err != nil {
		return nil, err
	}
	return a.handleResponse(resp)
}

// Delete makes DELETE request
func (a *APIClient) Delete(endpoint string) (map[string]interface{}, error) {
	resp, err := a.makeRequest("DELETE", endpoint, nil, nil)
	if err != nil {
		return nil, err
	}
	return a.handleResponse(resp)
}

// UserClient provides user-specific operations
type UserClient struct {
	apiClient *APIClient
}

// NewUserClient creates new user client
func NewUserClient(apiClient *APIClient) *UserClient {
	return &UserClient{apiClient: apiClient}
}

// ListUsers lists users with pagination
func (u *UserClient) ListUsers(page, limit int) (map[string]interface{}, error) {
	params := map[string]string{
		"page":  fmt.Sprintf("%d", page),
		"limit": fmt.Sprintf("%d", limit),
	}
	return u.apiClient.Get("/users", params)
}

// CreateUser creates new user
func (u *UserClient) CreateUser(userData map[string]interface{}) (map[string]interface{}, error) {
	return u.apiClient.Post("/users", userData)
}

// GetUser retrieves user by ID
func (u *UserClient) GetUser(userID string) (map[string]interface{}, error) {
	return u.apiClient.Get(fmt.Sprintf("/users/%s", userID), nil)
}

// UpdateUser updates user
func (u *UserClient) UpdateUser(userID string, updates map[string]interface{}) (map[string]interface{}, error) {
	return u.apiClient.Patch(fmt.Sprintf("/users/%s", userID), updates)
}

// DeleteUser deletes user
func (u *UserClient) DeleteUser(userID string) (map[string]interface{}, error) {
	return u.apiClient.Delete(fmt.Sprintf("/users/%s", userID))
}

// Example usage
func main() {
	logger := log.New(os.Stdout, "API: ", log.LstdFlags)

	// Initialize OAuth2 client
	oauth2 := NewOAuth2Client(
		"your-client-id",
		"your-client-secret",
		logger,
	)

	// Authenticate
	_, err := oauth2.GetToken(
		"https://auth.example.com/oauth/token",
		[]string{"users.read", "users.write"},
	)
	if err != nil {
		logger.Fatalf("Authentication failed: %v", err)
	}

	// Create API client
	config := APIConfig{
		BaseURL:       "https://api.example.com/v1",
		ClientID:      "your-client-id",
		ClientSecret:  "your-client-secret",
		Timeout:       30 * time.Second,
		MaxRetries:    3,
		BackoffFactor: 0.5,
	}

	apiClient := NewAPIClient(config, oauth2, logger)

	// List users
	users, err := apiClient.Get("/users", map[string]string{"limit": "10"})
	if err != nil {
		logger.Printf("Error listing users: %v", err)
		return
	}
	logger.Printf("Retrieved users: %+v", users)

	// Create user
	newUser, err := apiClient.Post("/users", map[string]interface{}{
		"firstName": "John",
		"lastName":  "Doe",
		"email":     "john@example.com",
	})
	if err != nil {
		logger.Printf("Error creating user: %v", err)
		return
	}
	logger.Printf("Created user: %+v", newUser)

	// Use specialized client
	userClient := NewUserClient(apiClient)
	user, err := userClient.GetUser("123")
	if err != nil {
		logger.Printf("Error getting user: %v", err)
		return
	}
	logger.Printf("Retrieved user: %+v", user)
}

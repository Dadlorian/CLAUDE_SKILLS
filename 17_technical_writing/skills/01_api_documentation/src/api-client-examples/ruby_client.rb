#!/usr/bin/env ruby
# frozen_string_literal: true

##
# Production-Ready Ruby API Client
# Implements OAuth2 authentication, retry logic, and comprehensive error handling
#
# Module: APIClient
# Requires: httpclient, json, time

require 'httpclient'
require 'json'
require 'time'
require 'logger'

##
# OAuth2 Authentication Client
class OAuth2Client
  attr_reader :access_token, :refresh_token, :token_expires_at

  ##
  # Initialize OAuth2 client
  def initialize(client_id, client_secret, logger = Logger.new($stdout))
    @client_id = client_id
    @client_secret = client_secret
    @logger = logger
    @access_token = nil
    @refresh_token = nil
    @token_expires_at = nil
  end

  ##
  # Authenticate and get access token
  #
  # @param auth_endpoint [String] OAuth2 token endpoint
  # @param scopes [Array<String>] Requested scopes
  # @return [Hash] Token response
  # @raise [StandardError] If authentication fails
  def get_token(auth_endpoint, scopes = [])
    client = HTTPClient.new
    payload = {
      grant_type: 'client_credentials',
      client_id: @client_id,
      client_secret: @client_secret,
      scope: scopes.join(' ')
    }

    response = client.post(auth_endpoint, body: payload)

    unless response.status == 200
      raise "Authentication failed: #{response.status}"
    end

    token_data = JSON.parse(response.body)
    @access_token = token_data['access_token']
    @refresh_token = token_data['refresh_token']

    # Calculate token expiration
    expires_in = token_data['expires_in'] || 3600
    @token_expires_at = Time.now + expires_in

    @logger.info("Successfully authenticated. Token expires at #{@token_expires_at}")
    token_data
  end

  ##
  # Refresh access token
  #
  # @param auth_endpoint [String] OAuth2 token endpoint
  # @return [Hash] New token response
  # @raise [StandardError] If refresh fails
  def refresh(auth_endpoint)
    raise 'No refresh token available' unless @refresh_token

    client = HTTPClient.new
    payload = {
      grant_type: 'refresh_token',
      refresh_token: @refresh_token,
      client_id: @client_id,
      client_secret: @client_secret
    }

    response = client.post(auth_endpoint, body: payload)

    unless response.status == 200
      raise "Token refresh failed: #{response.status}"
    end

    get_token(auth_endpoint, [])
  end

  ##
  # Check if current token is expired
  #
  # @return [Boolean] True if token is expired
  def token_expired?
    return true if @token_expires_at.nil?

    Time.now >= @token_expires_at
  end
end

##
# Production-Ready API Client
class APIClient
  attr_reader :base_url, :oauth2

  ##
  # Initialize API client
  #
  # @param base_url [String] Base API URL
  # @param oauth2 [OAuth2Client] OAuth2 client for authentication
  # @param options [Hash] Configuration options
  # @option options [Integer] :timeout Request timeout in seconds
  # @option options [Integer] :max_retries Maximum retry attempts
  # @option options [Logger] :logger Logger instance
  def initialize(base_url, oauth2 = nil, options = {})
    @base_url = base_url
    @oauth2 = oauth2
    @timeout = options[:timeout] || 30
    @max_retries = options[:max_retries] || 3
    @logger = options[:logger] || Logger.new($stdout)
    @client = create_http_client
  end

  ##
  # Create HTTP client with configuration
  #
  # @return [HTTPClient] Configured HTTP client
  private def create_http_client
    client = HTTPClient.new
    client.connect_timeout = @timeout
    client.send_timeout = @timeout
    client.receive_timeout = @timeout
    client
  end

  ##
  # Get request headers with authentication
  #
  # @return [Hash] Request headers
  private def headers
    hdrs = {
      'Content-Type' => 'application/json',
      'Accept' => 'application/json',
      'User-Agent' => 'RubyAPIClient/1.0'
    }

    if @oauth2&.access_token
      hdrs['Authorization'] = "Bearer #{@oauth2.access_token}"
    end

    hdrs
  end

  ##
  # Make HTTP request with error handling and retries
  #
  # @param method [Symbol] HTTP method (:get, :post, :patch, :delete)
  # @param endpoint [String] API endpoint path
  # @param options [Hash] Request options
  # @return [HTTP::Message] Response object
  # @raise [StandardError] If request fails
  private def make_request(method, endpoint, options = {})
    url = File.join(@base_url, endpoint)
    retry_count = 0

    loop do
      begin
        response = case method.to_sym
                   when :get
                     @client.get(url, query: options[:params], header: headers)
                   when :post
                     @client.post(url, body: options[:json]&.to_json || options[:data],
                                 header: headers)
                   when :patch
                     @client.patch(url, body: options[:json]&.to_json, header: headers)
                   when :delete
                     @client.delete(url, header: headers)
                   else
                     raise "Unsupported HTTP method: #{method}"
                   end

        handle_response(response, method, endpoint)
        return response

      rescue StandardError => e
        retry_count += 1

        if retry_count < @max_retries && retryable_error?(e)
          sleep(2 ** (retry_count - 1))
          next
        end

        @logger.error("Request failed: #{method.upcase} #{endpoint} - #{e.message}")
        raise
      end
    end
  end

  ##
  # Handle HTTP response and check for errors
  #
  # @param response [HTTP::Message] Response object
  # @param method [Symbol] HTTP method used
  # @param endpoint [String] API endpoint
  # @raise [StandardError] If response indicates an error
  private def handle_response(response, method, endpoint)
    @logger.debug("#{method.upcase} #{endpoint} -> #{response.status}")

    case response.status
    when 200..299
      # Success
    when 401
      @logger.warn('Authentication failed (401)')
      raise 'Unauthorized - invalid or expired token'
    when 403
      raise 'Insufficient permissions (403)'
    when 404
      raise "Resource not found (404): #{endpoint}"
    when 429
      raise 'Rate limit exceeded (429)'
    when 500..599
      raise "Server error: #{response.status}"
    else
      raise "HTTP error: #{response.status}"
    end
  end

  ##
  # Determine if error is retryable
  #
  # @param error [StandardError] Error to check
  # @return [Boolean] True if error is retryable
  private def retryable_error?(error)
    error.message.match?(/timeout|connection|Rate limit/)
  end

  ##
  # Make GET request
  #
  # @param endpoint [String] API endpoint
  # @param params [Hash] Query parameters
  # @return [Hash] Parsed JSON response
  def get(endpoint, params: {})
    response = make_request(:get, endpoint, params: params)
    JSON.parse(response.body)
  end

  ##
  # Make POST request
  #
  # @param endpoint [String] API endpoint
  # @param data [Hash] Request body
  # @return [Hash] Parsed JSON response
  def post(endpoint, data: {})
    response = make_request(:post, endpoint, json: data)
    JSON.parse(response.body)
  end

  ##
  # Make PATCH request
  #
  # @param endpoint [String] API endpoint
  # @param data [Hash] Request body
  # @return [Hash] Parsed JSON response
  def patch(endpoint, data: {})
    response = make_request(:patch, endpoint, json: data)
    JSON.parse(response.body)
  end

  ##
  # Make DELETE request
  #
  # @param endpoint [String] API endpoint
  # @return [Hash] Parsed JSON response
  def delete(endpoint)
    response = make_request(:delete, endpoint)
    response.body.empty? ? {} : JSON.parse(response.body)
  end
end

##
# Specialized client for user operations
class UserClient
  def initialize(api_client)
    @api_client = api_client
  end

  ##
  # List users with pagination
  #
  # @param page [Integer] Page number
  # @param limit [Integer] Results per page
  # @return [Hash] Paginated user list
  def list_users(page: 1, limit: 10)
    @api_client.get('/users', params: { page: page, limit: limit })
  end

  ##
  # Create new user
  #
  # @param user_data [Hash] User attributes
  # @return [Hash] Created user
  def create_user(user_data)
    @api_client.post('/users', data: user_data)
  end

  ##
  # Get user by ID
  #
  # @param user_id [String] User ID
  # @return [Hash] User data
  def get_user(user_id)
    @api_client.get("/users/#{user_id}")
  end

  ##
  # Update user
  #
  # @param user_id [String] User ID
  # @param updates [Hash] Fields to update
  # @return [Hash] Updated user
  def update_user(user_id, updates)
    @api_client.patch("/users/#{user_id}", data: updates)
  end

  ##
  # Delete user
  #
  # @param user_id [String] User ID
  # @return [Hash] Deletion confirmation
  def delete_user(user_id)
    @api_client.delete("/users/#{user_id}")
  end
end

# Example usage
if __FILE__ == $PROGRAM_NAME
  logger = Logger.new($stdout)
  logger.level = Logger::INFO

  # Initialize OAuth2 client
  oauth2 = OAuth2Client.new(
    'your-client-id',
    'your-client-secret',
    logger
  )

  # Authenticate
  begin
    oauth2.get_token(
      'https://auth.example.com/oauth/token',
      ['users.read', 'users.write']
    )
  rescue StandardError => e
    logger.error("Authentication failed: #{e.message}")
    exit 1
  end

  # Create API client
  api_client = APIClient.new(
    'https://api.example.com/v1',
    oauth2,
    logger: logger,
    timeout: 30
  )

  begin
    # List users
    users = api_client.get('/users', params: { limit: 10 })
    logger.info("Retrieved #{users['items']&.length || 0} users")

    # Create user
    new_user = api_client.post(
      '/users',
      data: {
        firstName: 'John',
        lastName: 'Doe',
        email: 'john@example.com'
      }
    )
    logger.info("Created user: #{new_user['id']}")

    # Use specialized client
    user_client = UserClient.new(api_client)
    user = user_client.get_user(new_user['id'])
    logger.info("Retrieved user: #{user['email']}")

  rescue StandardError => e
    logger.error("Error: #{e.message}")
  end
end

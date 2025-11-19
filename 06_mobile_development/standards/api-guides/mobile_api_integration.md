# Mobile API Integration Patterns
## RESTful APIs, GraphQL, gRPC, and WebSockets for Mobile

**Version**: 1.0 | **Last Updated**: 2025-11-19

---

## Overview

Mobile API integration requires careful consideration of:
- **Network reliability**: Handle intermittent connectivity
- **Battery efficiency**: Minimize network requests
- **Data usage**: Reduce bandwidth consumption
- **Security**: Protect sensitive data in transit
- **Performance**: Fast response times, caching strategies

---

## RESTful API Integration

### iOS (URLSession)

```swift
// Modern async/await approach (iOS 15+)
struct APIClient {
    private let baseURL = "https://api.example.com"

    func fetchUser(id: String) async throws -> User {
        guard let url = URL(string: "\(baseURL)/users/\(id)") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.invalidResponse
        }

        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .iso8601

        return try decoder.decode(User.self, from: data)
    }

    func updateUser(_ user: User) async throws {
        guard let url = URL(string: "\(baseURL)/users/\(user.id)") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
        request.httpBody = try encoder.encode(user)

        let (_, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.invalidResponse
        }
    }
}

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case decodingError(Error)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case .invalidResponse: return "Invalid response from server"
        case .decodingError(let error): return "Decoding failed: \(error)"
        }
    }
}
```

### Android (Retrofit + OkHttp)

```kotlin
// API Service Interface
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): Response<User>

    @PUT("users/{id}")
    suspend fun updateUser(
        @Path("id") userId: String,
        @Body user: User
    ): Response<Unit>

    @POST("users")
    suspend fun createUser(@Body user: User): Response<User>

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") userId: String): Response<Unit>

    @GET("users")
    suspend fun getUsers(
        @Query("page") page: Int,
        @Query("limit") limit: Int = 20
    ): Response<List<User>>
}

// Retrofit Setup
object NetworkModule {
    private const val BASE_URL = "https://api.example.com/"

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = if (BuildConfig.DEBUG) {
            HttpLoggingInterceptor.Level.BODY
        } else {
            HttpLoggingInterceptor.Level.NONE
        }
    }

    private val authInterceptor = Interceptor { chain ->
        val original = chain.request()
        val request = original.newBuilder()
            .header("Authorization", "Bearer $accessToken")
            .header("Content-Type", "application/json")
            .build()
        chain.proceed(request)
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .addInterceptor(authInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(MoshiConverterFactory.create())
        .build()

    val apiService: ApiService = retrofit.create(ApiService::class.java)
}

// Repository Pattern
class UserRepository(private val apiService: ApiService) {
    suspend fun getUser(userId: String): Result<User> {
        return try {
            val response = apiService.getUser(userId)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(ApiException(response.code(), response.message()))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

data class ApiException(val code: Int, override val message: String) : Exception(message)
```

### React Native (Axios)

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';

// API Client Setup
class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: 'https://api.example.com',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = getAccessToken(); // Get from secure storage
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired, try refresh
          const newToken = await refreshAccessToken();
          if (newToken && error.config) {
            error.config.headers.Authorization = `Bearer ${newToken}`;
            return this.client.request(error.config);
          }
        }
        return Promise.reject(error);
      }
    );
  }

  async getUser(userId: string): Promise<User> {
    const response = await this.client.get<User>(`/users/${userId}`);
    return response.data;
  }

  async updateUser(user: User): Promise<void> {
    await this.client.put(`/users/${user.id}`, user);
  }

  async createUser(user: Partial<User>): Promise<User> {
    const response = await this.client.post<User>('/users', user);
    return response.data;
  }

  async deleteUser(userId: string): Promise<void> {
    await this.client.delete(`/users/${userId}`);
  }

  async getUsers(page: number = 1, limit: number = 20): Promise<User[]> {
    const response = await this.client.get<User[]>('/users', {
      params: { page, limit },
    });
    return response.data;
  }
}

export const apiClient = new APIClient();
```

### Flutter (Dio)

```dart
import 'package:dio/dio.dart';

class ApiClient {
  final Dio _dio;
  static const String baseUrl = 'https://api.example.com';

  ApiClient()
      : _dio = Dio(
          BaseOptions(
            baseUrl: baseUrl,
            connectTimeout: const Duration(seconds: 30),
            receiveTimeout: const Duration(seconds: 30),
            headers: {'Content-Type': 'application/json'},
          ),
        ) {
    _dio.interceptors.add(_AuthInterceptor());
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
    ));
  }

  Future<User> getUser(String userId) async {
    try {
      final response = await _dio.get('/users/$userId');
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> updateUser(User user) async {
    try {
      await _dio.put('/users/${user.id}', data: user.toJson());
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<User> createUser(User user) async {
    try {
      final response = await _dio.post('/users', data: user.toJson());
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> deleteUser(String userId) async {
    try {
      await _dio.delete('/users/$userId');
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<User>> getUsers({int page = 1, int limit = 20}) async {
    try {
      final response = await _dio.get(
        '/users',
        queryParameters: {'page': page, 'limit': limit},
      );
      return (response.data as List)
          .map((json) => User.fromJson(json))
          .toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Exception _handleError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return TimeoutException('Request timed out');
      case DioExceptionType.badResponse:
        return ApiException(
          error.response?.statusCode ?? 0,
          error.response?.statusMessage ?? 'Unknown error',
        );
      default:
        return NetworkException('Network error occurred');
    }
  }
}

class _AuthInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final token = getAccessToken(); // Get from secure storage
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // Token expired, try refresh
      final newToken = await refreshAccessToken();
      if (newToken != null) {
        err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
        final response = await _dio.fetch(err.requestOptions);
        return handler.resolve(response);
      }
    }
    handler.next(err);
  }
}
```

---

## GraphQL Integration

### iOS (Apollo GraphQL)

```swift
import Apollo

class ApolloClient {
    static let shared = ApolloClient()

    private lazy var apollo: Apollo.Client = {
        let store = ApolloStore()
        let client = URLSessionClient()
        let provider = NetworkInterceptorProvider(store: store, client: client)
        let url = URL(string: "https://api.example.com/graphql")!

        let transport = RequestChainNetworkTransport(
            interceptorProvider: provider,
            endpointURL: url
        )

        return Apollo.Client(networkTransport: transport, store: store)
    }()

    func fetchUser(id: String) async throws -> UserQuery.Data.User {
        let query = UserQuery(id: id)
        let result = try await apollo.fetch(query: query)

        guard let user = result.data?.user else {
            throw GraphQLError.noData
        }

        return user
    }

    func updateUser(input: UpdateUserInput) async throws {
        let mutation = UpdateUserMutation(input: input)
        _ = try await apollo.perform(mutation: mutation)
    }
}

// GraphQL query definition (*.graphql file)
/*
query User($id: ID!) {
  user(id: $id) {
    id
    name
    email
    avatarUrl
  }
}

mutation UpdateUser($input: UpdateUserInput!) {
  updateUser(input: $input) {
    id
    name
    email
  }
}
*/
```

### Android (Apollo GraphQL)

```kotlin
import com.apollographql.apollo3.ApolloClient
import com.apollographql.apollo3.network.okHttpClient
import okhttp3.Interceptor

object GraphQLClient {
    private const val SERVER_URL = "https://api.example.com/graphql"

    private val authInterceptor = Interceptor { chain ->
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer $accessToken")
            .build()
        chain.proceed(request)
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)
        .build()

    val apolloClient = ApolloClient.Builder()
        .serverUrl(SERVER_URL)
        .okHttpClient(okHttpClient)
        .build()
}

// Repository usage
class UserRepository {
    suspend fun getUser(userId: String): User {
        val response = GraphQLClient.apolloClient
            .query(UserQuery(userId))
            .execute()

        return response.data?.user?.let {
            User(
                id = it.id,
                name = it.name,
                email = it.email
            )
        } ?: throw Exception("User not found")
    }

    suspend fun updateUser(input: UpdateUserInput): User {
        val response = GraphQLClient.apolloClient
            .mutation(UpdateUserMutation(input))
            .execute()

        return response.data?.updateUser?.let {
            User(
                id = it.id,
                name = it.name,
                email = it.email
            )
        } ?: throw Exception("Update failed")
    }
}
```

### React Native (Apollo Client)

```typescript
import { ApolloClient, InMemoryCache, createHttpLink, gql } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';

// Apollo Client setup
const httpLink = createHttpLink({
  uri: 'https://api.example.com/graphql',
});

const authLink = setContext(async (_, { headers }) => {
  const token = await getAccessToken();
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
    },
  };
});

const apolloClient = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});

// GraphQL queries and mutations
const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) {
      id
      name
      email
      avatarUrl
    }
  }
`;

const UPDATE_USER = gql`
  mutation UpdateUser($input: UpdateUserInput!) {
    updateUser(input: $input) {
      id
      name
      email
    }
  }
`;

// Usage in component with hooks
import { useQuery, useMutation } from '@apollo/client';

function UserProfile({ userId }: { userId: string }) {
  const { data, loading, error } = useQuery(GET_USER, {
    variables: { id: userId },
  });

  const [updateUser, { loading: updating }] = useMutation(UPDATE_USER);

  const handleUpdate = async (name: string) => {
    await updateUser({
      variables: {
        input: { id: userId, name },
      },
    });
  };

  if (loading) return <LoadingView />;
  if (error) return <ErrorView message={error.message} />;

  return <UserView user={data.user} onUpdate={handleUpdate} />;
}
```

### Flutter (GraphQL Flutter)

```dart
import 'package:graphql_flutter/graphql_flutter.dart';

class GraphQLConfig {
  static HttpLink httpLink = HttpLink('https://api.example.com/graphql');

  static AuthLink authLink = AuthLink(
    getToken: () async {
      final token = await getAccessToken();
      return token != null ? 'Bearer $token' : null;
    },
  );

  static Link link = authLink.concat(httpLink);

  static ValueNotifier<GraphQLClient> client = ValueNotifier(
    GraphQLClient(
      link: link,
      cache: GraphQLCache(store: InMemoryStore()),
    ),
  );
}

// GraphQL queries
const String getUserQuery = r'''
  query GetUser($id: ID!) {
    user(id: $id) {
      id
      name
      email
      avatarUrl
    }
  }
''';

const String updateUserMutation = r'''
  mutation UpdateUser($input: UpdateUserInput!) {
    updateUser(input: $input) {
      id
      name
      email
    }
  }
''';

// Usage in widget
class UserProfileScreen extends StatelessWidget {
  final String userId;

  const UserProfileScreen({required this.userId});

  @override
  Widget build(BuildContext context) {
    return Query(
      options: QueryOptions(
        document: gql(getUserQuery),
        variables: {'id': userId},
      ),
      builder: (result, {fetchMore, refetch}) {
        if (result.isLoading) {
          return const CircularProgressIndicator();
        }

        if (result.hasException) {
          return Text('Error: ${result.exception}');
        }

        final user = result.data?['user'];

        return Mutation(
          options: MutationOptions(
            document: gql(updateUserMutation),
          ),
          builder: (runMutation, result) {
            return UserView(
              user: user,
              onUpdate: (name) {
                runMutation({'input': {'id': userId, 'name': name}});
              },
            );
          },
        );
      },
    );
  }
}
```

---

## Caching Strategies

### HTTP Caching

```swift
// iOS - URLCache configuration
let cache = URLCache(
    memoryCapacity: 50_000_000, // 50 MB
    diskCapacity: 100_000_000,   // 100 MB
    diskPath: "api_cache"
)
URLCache.shared = cache

// Cache policy
var request = URLRequest(url: url)
request.cachePolicy = .returnCacheDataElseLoad
```

```kotlin
// Android - OkHttp caching
val cacheSize = 50 * 1024 * 1024L // 50 MB
val cache = Cache(context.cacheDir, cacheSize)

val okHttpClient = OkHttpClient.Builder()
    .cache(cache)
    .build()
```

### Application-Level Caching

```typescript
// React Native - React Query caching
import { useQuery } from '@tanstack/react-query';

function useUser(userId: string) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => apiClient.getUser(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
}
```

```dart
// Flutter - Hive caching
class UserRepository {
  final Box<User> _cache = Hive.box<User>('users');

  Future<User> getUser(String userId) async {
    // Check cache first
    if (_cache.containsKey(userId)) {
      return _cache.get(userId)!;
    }

    // Fetch from API
    final user = await _apiClient.getUser(userId);

    // Update cache
    await _cache.put(userId, user);

    return user;
  }
}
```

---

## Error Handling & Retry Logic

```typescript
// Exponential backoff retry
async function fetchWithRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3
): Promise<T> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries) throw error;

      const delay = Math.min(1000 * 2 ** attempt, 10000);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  throw new Error('Max retries exceeded');
}

// Usage
const user = await fetchWithRetry(() => apiClient.getUser('123'));
```

---

**Professional API integration ensures reliable, performant, and secure data access in mobile applications!**

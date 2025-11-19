# Mobile Coding Standards
## Professional Code Quality Across iOS, Android, React Native & Flutter

**Version**: 1.0 | **Last Updated**: 2025-11-19

---

## Philosophy

Write code that is:
- **Readable**: Clear intent, self-documenting
- **Maintainable**: Easy to modify and extend
- **Testable**: Designed for automated testing
- **Performant**: Optimized for mobile constraints
- **Secure**: Following OWASP guidelines
- **Accessible**: Supporting all users

---

## iOS (Swift) Coding Standards

### Naming Conventions

#### Types
```swift
// Classes, Structs, Enums, Protocols - PascalCase
class UserProfileViewController: UIViewController { }
struct UserData { }
enum NetworkError { }
protocol DataSource { }
```

#### Variables & Functions
```swift
// Variables, functions, parameters - camelCase
var userName: String
func fetchUserData(userId: String) async throws -> User { }
let isAuthenticated = true
```

#### Constants
```swift
// Constants - camelCase (not SCREAMING_SNAKE_CASE)
let maxRetryAttempts = 3
let apiBaseURL = "https://api.example.com"

// Static constants
struct Constants {
    static let animationDuration: TimeInterval = 0.3
}
```

### Code Organization

```swift
// MARK: - Type definition
class UserViewModel: ObservableObject {

    // MARK: - Properties

    // Published properties first
    @Published var user: User?
    @Published var isLoading = false

    // Private properties
    private let repository: UserRepository
    private var cancellables = Set<AnyCancellable>()

    // MARK: - Initialization

    init(repository: UserRepository) {
        self.repository = repository
    }

    // MARK: - Public Methods

    func loadUser(id: String) async {
        isLoading = true
        defer { isLoading = false }

        do {
            user = try await repository.fetchUser(id: id)
        } catch {
            handleError(error)
        }
    }

    // MARK: - Private Methods

    private func handleError(_ error: Error) {
        // Error handling logic
    }
}
```

### SwiftUI Best Practices

```swift
// Extract complex views into smaller components
struct UserProfileView: View {
    @StateObject private var viewModel: UserViewModel

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                UserHeaderView(user: viewModel.user)
                UserStatsView(stats: viewModel.stats)
                UserPostsView(posts: viewModel.posts)
            }
        }
        .task { await viewModel.loadUser() }
    }
}

// Use view modifiers for consistent styling
extension View {
    func primaryButtonStyle() -> some View {
        self
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(8)
    }
}

// Prefer @ViewBuilder for conditional views
@ViewBuilder
func contentView() -> some View {
    if isLoading {
        ProgressView()
    } else if let user = user {
        UserDetailView(user: user)
    } else {
        EmptyStateView()
    }
}
```

### Error Handling

```swift
// Use custom error types
enum NetworkError: LocalizedError {
    case invalidURL
    case noData
    case decodingFailed(Error)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case .noData: return "No data received"
        case .decodingFailed(let error):
            return "Decoding failed: \(error.localizedDescription)"
        }
    }
}

// Async/await error handling
func fetchData() async throws -> Data {
    guard let url = URL(string: apiURL) else {
        throw NetworkError.invalidURL
    }

    let (data, _) = try await URLSession.shared.data(from: url)
    return data
}
```

### Memory Management

```swift
// Use [weak self] in closures to prevent retain cycles
class UserViewController: UIViewController {
    private var viewModel: UserViewModel?

    func setupObservers() {
        viewModel?.userPublisher
            .sink { [weak self] user in
                self?.updateUI(with: user)
            }
            .store(in: &cancellables)
    }
}

// Use unowned sparingly, only when reference is guaranteed
class ChildView {
    unowned let parent: ParentView // Only if parent always exists
}
```

---

## Android (Kotlin) Coding Standards

### Naming Conventions

#### Types
```kotlin
// Classes, Interfaces, Objects - PascalCase
class UserProfileActivity : AppCompatActivity()
interface DataRepository
object AppConfig
sealed class UiState
```

#### Variables & Functions
```kotlin
// Variables and functions - camelCase
var userName: String
fun fetchUserData(userId: String): Flow<User>
val isAuthenticated = true
```

#### Constants
```kotlin
// Top-level and object constants - SCREAMING_SNAKE_CASE
const val MAX_RETRY_ATTEMPTS = 3
const val API_BASE_URL = "https://api.example.com"

object Constants {
    const val ANIMATION_DURATION = 300L
}

// Class-level constants - camelCase with const or @JvmField
class Config {
    companion object {
        const val timeout = 30_000
    }
}
```

### Code Organization

```kotlin
class UserViewModel(
    private val repository: UserRepository,
    private val analytics: Analytics
) : ViewModel() {

    // State
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // Public methods
    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            repository.getUser(userId)
                .onSuccess { user ->
                    _uiState.value = UiState.Success(user)
                    analytics.logEvent("user_loaded")
                }
                .onFailure { error ->
                    _uiState.value = UiState.Error(error.message)
                }
        }
    }

    // Private methods
    private fun handleError(error: Throwable) {
        // Error handling
    }
}

// Sealed class for state
sealed class UiState {
    object Loading : UiState()
    data class Success(val user: User) : UiState()
    data class Error(val message: String?) : UiState()
}
```

### Jetpack Compose Best Practices

```kotlin
// Extract complex composables
@Composable
fun UserProfileScreen(
    viewModel: UserViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = { UserProfileTopBar() }
    ) { paddingValues ->
        when (val state = uiState) {
            is UiState.Loading -> LoadingView()
            is UiState.Success -> UserContent(
                user = state.user,
                modifier = Modifier.padding(paddingValues)
            )
            is UiState.Error -> ErrorView(state.message)
        }
    }
}

// Use remember for expensive calculations
@Composable
fun ExpensiveView(items: List<Item>) {
    val processedItems = remember(items) {
        items.map { processItem(it) }
    }

    LazyColumn {
        items(processedItems) { item ->
            ItemView(item)
        }
    }
}

// Hoist state up
@Composable
fun SearchScreen() {
    var searchQuery by remember { mutableStateOf("") }

    Column {
        SearchBar(
            query = searchQuery,
            onQueryChange = { searchQuery = it }
        )
        SearchResults(query = searchQuery)
    }
}
```

### Coroutines Best Practices

```kotlin
// Use structured concurrency
fun fetchData() {
    viewModelScope.launch {
        try {
            val user = async { userRepository.getUser() }
            val posts = async { postRepository.getPosts() }

            updateUI(user.await(), posts.await())
        } catch (e: Exception) {
            handleError(e)
        }
    }
}

// Use proper dispatchers
suspend fun saveToDatabase(user: User) {
    withContext(Dispatchers.IO) {
        database.userDao().insert(user)
    }
}

// Flow collection in UI
@Composable
fun UserScreen(viewModel: UserViewModel) {
    val users by viewModel.users.collectAsState(initial = emptyList())

    LazyColumn {
        items(users) { user ->
            UserItem(user)
        }
    }
}
```

### Null Safety

```kotlin
// Use safe calls and Elvis operator
val userName = user?.name ?: "Unknown"

// Use let for null checks
user?.let { nonNullUser ->
    displayUser(nonNullUser)
}

// Use require/check for validation
fun processUser(user: User?) {
    requireNotNull(user) { "User cannot be null" }
    require(user.id.isNotEmpty()) { "User ID must not be empty" }
}
```

---

## React Native (JavaScript/TypeScript) Standards

### TypeScript Configuration

```typescript
// tsconfig.json - Strict mode enabled
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
```

### Naming Conventions

```typescript
// Components - PascalCase
const UserProfileScreen: React.FC<Props> = () => { };

// Functions, variables - camelCase
const fetchUserData = async (userId: string): Promise<User> => { };
const userName = 'John';

// Constants - SCREAMING_SNAKE_CASE
const MAX_RETRIES = 3;
const API_BASE_URL = 'https://api.example.com';

// Types/Interfaces - PascalCase
interface User {
  id: string;
  name: string;
}

type UserState = 'loading' | 'success' | 'error';
```

### Component Structure

```typescript
// Functional component with hooks
interface UserProfileProps {
  userId: string;
  onUpdate?: (user: User) => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ userId, onUpdate }) => {
  // State hooks first
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  // Refs
  const isMounted = useRef(true);

  // Memoized values
  const fullName = useMemo(() =>
    user ? `${user.firstName} ${user.lastName}` : '',
    [user]
  );

  // Callbacks
  const handleUpdate = useCallback((updatedUser: User) => {
    setUser(updatedUser);
    onUpdate?.(updatedUser);
  }, [onUpdate]);

  // Effects
  useEffect(() => {
    loadUser();
    return () => {
      isMounted.current = false;
    };
  }, [userId]);

  // Helper functions
  const loadUser = async () => {
    setLoading(true);
    try {
      const data = await fetchUser(userId);
      if (isMounted.current) {
        setUser(data);
      }
    } catch (error) {
      console.error('Failed to load user:', error);
    } finally {
      setLoading(false);
    }
  };

  // Render
  if (loading) return <LoadingView />;
  if (!user) return <EmptyView />;

  return (
    <View style={styles.container}>
      <Text style={styles.name}>{fullName}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
  },
});

export default UserProfile;
```

### Redux Toolkit Best Practices

```typescript
// Slice definition
import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';

interface UserState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

const initialState: UserState = {
  user: null,
  loading: false,
  error: null,
};

export const fetchUser = createAsyncThunk(
  'user/fetch',
  async (userId: string, { rejectWithValue }) => {
    try {
      const response = await api.getUser(userId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    clearUser(state) {
      state.user = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(fetchUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearUser } = userSlice.actions;
export default userSlice.reducer;
```

---

## Flutter (Dart) Coding Standards

### Naming Conventions

```dart
// Classes - PascalCase (UpperCamelCase)
class UserProfile extends StatefulWidget { }
class UserRepository { }

// Variables, functions, parameters - camelCase (lowerCamelCase)
String userName = 'John';
void fetchUserData(String userId) { }

// Constants - camelCase (not SCREAMING_SNAKE_CASE in Dart)
const int maxRetries = 3;
const String apiBaseUrl = 'https://api.example.com';

// Private members - prefix with underscore
class User {
  final String id;
  final String _privateField;
}

// Files - snake_case
// user_profile_screen.dart
// api_service.dart
```

### Widget Structure

```dart
// Stateless widget
class UserAvatar extends StatelessWidget {
  const UserAvatar({
    super.key,
    required this.imageUrl,
    this.size = 48.0,
  });

  final String imageUrl;
  final double size;

  @override
  Widget build(BuildContext context) {
    return ClipOval(
      child: Image.network(
        imageUrl,
        width: size,
        height: size,
        fit: BoxFit.cover,
      ),
    );
  }
}

// Stateful widget
class UserProfileScreen extends StatefulWidget {
  const UserProfileScreen({super.key, required this.userId});

  final String userId;

  @override
  State<UserProfileScreen> createState() => _UserProfileScreenState();
}

class _UserProfileScreenState extends State<UserProfileScreen> {
  User? _user;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadUser();
  }

  Future<void> _loadUser() async {
    setState(() => _isLoading = true);
    try {
      final user = await userRepository.getUser(widget.userId);
      if (mounted) {
        setState(() => _user = user);
      }
    } catch (e) {
      _handleError(e);
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _handleError(Object error) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Error: $error')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_user == null) return const Center(child: Text('No user found'));

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          UserAvatar(imageUrl: _user!.avatarUrl),
          const SizedBox(height: 16),
          Text(_user!.name, style: Theme.of(context).textTheme.headlineMedium),
        ],
      ),
    );
  }

  @override
  void dispose() {
    // Clean up resources
    super.dispose();
  }
}
```

### BLoC Pattern

```dart
// Events
abstract class UserEvent {}
class LoadUser extends UserEvent {
  final String userId;
  LoadUser(this.userId);
}

// States
abstract class UserState {}
class UserInitial extends UserState {}
class UserLoading extends UserState {}
class UserLoaded extends UserState {
  final User user;
  UserLoaded(this.user);
}
class UserError extends UserState {
  final String message;
  UserError(this.message);
}

// BLoC
class UserBloc extends Bloc<UserEvent, UserState> {
  final UserRepository repository;

  UserBloc({required this.repository}) : super(UserInitial()) {
    on<LoadUser>(_onLoadUser);
  }

  Future<void> _onLoadUser(LoadUser event, Emitter<UserState> emit) async {
    emit(UserLoading());
    try {
      final user = await repository.getUser(event.userId);
      emit(UserLoaded(user));
    } catch (e) {
      emit(UserError(e.toString()));
    }
  }
}

// Usage in widget
class UserScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<UserBloc, UserState>(
      builder: (context, state) {
        if (state is UserLoading) {
          return const CircularProgressIndicator();
        } else if (state is UserLoaded) {
          return UserView(user: state.user);
        } else if (state is UserError) {
          return ErrorView(message: state.message);
        }
        return const SizedBox();
      },
    );
  }
}
```

---

## Cross-Platform Standards

### File Organization

```
src/ (or lib/ for Flutter)
├── features/          # Feature-based organization
│   ├── auth/
│   │   ├── data/     # Data layer (repositories, API, models)
│   │   ├── domain/   # Domain layer (entities, use cases)
│   │   └── presentation/ # UI layer (screens, widgets, view models)
│   └── user/
├── core/             # Shared utilities
│   ├── constants/
│   ├── theme/
│   ├── utils/
│   └── network/
├── shared/           # Shared components
│   ├── components/
│   └── hooks/
└── navigation/       # Routing
```

### Comments & Documentation

```typescript
/**
 * Fetches user data from the API
 *
 * @param userId - The unique identifier for the user
 * @returns Promise resolving to User object
 * @throws {NetworkError} If the request fails
 *
 * @example
 * ```typescript
 * const user = await fetchUser('123');
 * console.log(user.name);
 * ```
 */
async function fetchUser(userId: string): Promise<User> {
  // Implementation
}

// Use comments for complex logic
// Calculate exponential backoff: delay = baseDelay * 2^attempt
const delay = BASE_DELAY * Math.pow(2, attempt);
```

### Code Review Checklist

- [ ] Follows platform naming conventions
- [ ] No compiler warnings or linter errors
- [ ] Includes unit tests for business logic
- [ ] Error handling for edge cases
- [ ] No hardcoded strings (use localization)
- [ ] No magic numbers (use named constants)
- [ ] Memory leaks checked (no retain cycles, proper cleanup)
- [ ] Accessibility labels added
- [ ] Performance tested (no blocking main thread)
- [ ] Security reviewed (no sensitive data in logs)

---

## Linting & Formatting

### iOS (SwiftLint)
```yaml
# .swiftlint.yml
disabled_rules:
  - trailing_whitespace
opt_in_rules:
  - empty_count
  - explicit_init
line_length: 120
file_length:
  warning: 500
  error: 1000
```

### Android (ktlint)
```kotlin
// build.gradle.kts
plugins {
    id("org.jlleitschuh.gradle.ktlint") version "11.0.0"
}

ktlint {
    android.set(true)
    ignoreFailures.set(false)
}
```

### React Native (ESLint)
```json
{
  "extends": [
    "@react-native-community",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "prettier/prettier": "error",
    "@typescript-eslint/no-unused-vars": "error"
  }
}
```

### Flutter (analysis_options.yaml)
```yaml
include: package:flutter_lints/flutter.yaml

linter:
  rules:
    - prefer_const_constructors
    - prefer_const_literals_to_create_immutables
    - avoid_print
    - prefer_single_quotes
```

---

**Use these standards to maintain professional code quality across all mobile platforms!**

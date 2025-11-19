# Mobile Architecture Patterns
## MVVM, MVI, Clean Architecture & More

**Version**: 1.0 | **Last Updated**: 2025-11-19

---

## Pattern Selection Guide

| Pattern | Best For | Complexity | Testability |
|---------|----------|------------|-------------|
| MVC | Simple apps, prototypes | Low | Low |
| MVP | Legacy Android, UIKit | Medium | Medium |
| MVVM | iOS/Android with reactive | Medium | High |
| MVI | Complex state, unidirectional flow | High | High |
| Clean Architecture | Large apps, multiple teams | High | Very High |
| VIPER | iOS enterprise apps | Very High | High |
| TCA (Composable) | SwiftUI functional approach | High | Very High |

---

## MVVM (Model-View-ViewModel)

**Best for**: SwiftUI, Jetpack Compose, React Native, Flutter

### iOS (SwiftUI + Combine)

```swift
// Model
struct User {
    let id: String
    let name: String
    let email: String
}

// ViewModel
import Combine

class UserViewModel: ObservableObject {
    @Published var user: User?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let repository: UserRepository
    private var cancellables = Set<AnyCancellable>()

    init(repository: UserRepository) {
        self.repository = repository
    }

    func loadUser(id: String) {
        isLoading = true
        errorMessage = nil

        repository.fetchUser(id: id)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                self?.isLoading = false
                if case .failure(let error) = completion {
                    self?.errorMessage = error.localizedDescription
                }
            } receiveValue: { [weak self] user in
                self?.user = user
            }
            .store(in: &cancellables)
    }
}

// View
struct UserProfileView: View {
    @StateObject private var viewModel: UserViewModel

    init(userId: String, repository: UserRepository) {
        _viewModel = StateObject(wrappedValue: UserViewModel(repository: repository))
    }

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
            } else if let error = viewModel.errorMessage {
                Text("Error: \(error)")
            } else if let user = viewModel.user {
                VStack {
                    Text(user.name)
                    Text(user.email)
                }
            }
        }
        .onAppear {
            viewModel.loadUser(id: userId)
        }
    }
}
```

### Android (Jetpack Compose + StateFlow)

```kotlin
// Model
data class User(
    val id: String,
    val name: String,
    val email: String
)

// ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            repository.getUser(userId)
                .onSuccess { user ->
                    _uiState.value = UiState.Success(user)
                }
                .onFailure { error ->
                    _uiState.value = UiState.Error(error.message ?: "Unknown error")
                }
        }
    }

    sealed class UiState {
        object Loading : UiState()
        data class Success(val user: User) : UiState()
        data class Error(val message: String) : UiState()
    }
}

// View (Composable)
@Composable
fun UserProfileScreen(
    userId: String,
    viewModel: UserViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(userId) {
        viewModel.loadUser(userId)
    }

    when (val state = uiState) {
        is UiState.Loading -> CircularProgressIndicator()
        is UiState.Success -> UserContent(user = state.user)
        is UiState.Error -> Text("Error: ${state.message}")
    }
}
```

---

## MVI (Model-View-Intent)

**Best for**: Complex state management, unidirectional data flow

### Android MVI Implementation

```kotlin
// Intent (User Actions)
sealed class UserIntent {
    data class LoadUser(val userId: String) : UserIntent()
    object RefreshUser : UserIntent()
    data class UpdateName(val name: String) : UserIntent()
}

// State
data class UserViewState(
    val isLoading: Boolean = false,
    val user: User? = null,
    val error: String? = null
) {
    val hasError: Boolean get() = error != null
}

// ViewModel with MVI
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _state = MutableStateFlow(UserViewState())
    val state: StateFlow<UserViewState> = _state.asStateFlow()

    fun processIntent(intent: UserIntent) {
        when (intent) {
            is UserIntent.LoadUser -> loadUser(intent.userId)
            is UserIntent.RefreshUser -> refreshUser()
            is UserIntent.UpdateName -> updateName(intent.name)
        }
    }

    private fun loadUser(userId: String) {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, error = null) }

            repository.getUser(userId)
                .onSuccess { user ->
                    _state.update { it.copy(isLoading = false, user = user) }
                }
                .onFailure { error ->
                    _state.update { it.copy(isLoading = false, error = error.message) }
                }
        }
    }

    private fun refreshUser() {
        state.value.user?.let { loadUser(it.id) }
    }

    private fun updateName(name: String) {
        viewModelScope.launch {
            state.value.user?.let { user ->
                val updated = user.copy(name = name)
                repository.updateUser(updated)
                    .onSuccess {
                        _state.update { it.copy(user = updated) }
                    }
            }
        }
    }
}

// View
@Composable
fun UserScreen(userId: String, viewModel: UserViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsState()

    LaunchedEffect(userId) {
        viewModel.processIntent(UserIntent.LoadUser(userId))
    }

    Column {
        when {
            state.isLoading -> CircularProgressIndicator()
            state.hasError -> ErrorView(state.error!!) {
                viewModel.processIntent(UserIntent.RefreshUser)
            }
            state.user != null -> UserView(state.user!!) { newName ->
                viewModel.processIntent(UserIntent.UpdateName(newName))
            }
        }
    }
}
```

---

## Clean Architecture

**Best for**: Large-scale applications, multiple teams

### Layer Structure

```
app/
├── presentation/     # UI Layer (Views, ViewModels)
├── domain/          # Business Logic (Use Cases, Entities)
└── data/            # Data Layer (Repositories, API, Database)
```

### Domain Layer (Platform-agnostic)

```kotlin
// Entity
data class User(
    val id: String,
    val name: String,
    val email: String
)

// Repository Interface (in domain layer)
interface UserRepository {
    suspend fun getUser(id: String): Result<User>
    suspend fun updateUser(user: User): Result<Unit>
}

// Use Case
class GetUserUseCase(
    private val repository: UserRepository
) {
    suspend operator fun invoke(userId: String): Result<User> {
        return repository.getUser(userId)
    }
}

class UpdateUserUseCase(
    private val repository: UserRepository,
    private val validator: UserValidator
) {
    suspend operator fun invoke(user: User): Result<Unit> {
        return when (val validation = validator.validate(user)) {
            is ValidationResult.Success -> repository.updateUser(user)
            is ValidationResult.Error -> Result.failure(
                ValidationException(validation.errors)
            )
        }
    }
}
```

### Data Layer

```kotlin
// Repository Implementation
class UserRepositoryImpl(
    private val remoteDataSource: UserRemoteDataSource,
    private val localDataSource: UserLocalDataSource
) : UserRepository {

    override suspend fun getUser(id: String): Result<User> {
        return try {
            // Try local first
            localDataSource.getUser(id)?.let {
                return Result.success(it)
            }

            // Fetch from remote
            val user = remoteDataSource.getUser(id)

            // Cache locally
            localDataSource.saveUser(user)

            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun updateUser(user: User): Result<Unit> {
        return try {
            remoteDataSource.updateUser(user)
            localDataSource.updateUser(user)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// Remote Data Source
interface UserRemoteDataSource {
    suspend fun getUser(id: String): User
    suspend fun updateUser(user: User)
}

class UserRemoteDataSourceImpl(
    private val apiService: ApiService
) : UserRemoteDataSource {

    override suspend fun getUser(id: String): User {
        val dto = apiService.getUser(id)
        return dto.toDomain()
    }

    override suspend fun updateUser(user: User) {
        apiService.updateUser(user.id, user.toDto())
    }
}
```

### Presentation Layer

```kotlin
class UserViewModel(
    private val getUserUseCase: GetUserUseCase,
    private val updateUserUseCase: UpdateUserUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            getUserUseCase(userId)
                .onSuccess { user ->
                    _uiState.value = UiState.Success(user.toPresentation())
                }
                .onFailure { error ->
                    _uiState.value = UiState.Error(error.toErrorMessage())
                }
        }
    }
}
```

---

## The Composable Architecture (TCA) - iOS

**Best for**: SwiftUI apps with complex state and side effects

```swift
import ComposableArchitecture

// State
struct UserState: Equatable {
    var user: User?
    var isLoading = false
    var errorMessage: String?
}

// Action
enum UserAction {
    case loadUser(String)
    case userResponse(Result<User, Error>)
    case updateName(String)
    case updateResponse(Result<Void, Error>)
}

// Environment (Dependencies)
struct UserEnvironment {
    var userRepository: UserRepository
    var mainQueue: AnySchedulerOf<DispatchQueue>
}

// Reducer
let userReducer = Reducer<UserState, UserAction, UserEnvironment> { state, action, environment in
    switch action {
    case .loadUser(let id):
        state.isLoading = true
        state.errorMessage = nil

        return environment.userRepository
            .fetchUser(id: id)
            .receive(on: environment.mainQueue)
            .catchToEffect()
            .map(UserAction.userResponse)

    case .userResponse(.success(let user)):
        state.isLoading = false
        state.user = user
        return .none

    case .userResponse(.failure(let error)):
        state.isLoading = false
        state.errorMessage = error.localizedDescription
        return .none

    case .updateName(let name):
        guard var user = state.user else { return .none }
        user.name = name

        return environment.userRepository
            .updateUser(user)
            .receive(on: environment.mainQueue)
            .catchToEffect()
            .map(UserAction.updateResponse)

    case .updateResponse(.success):
        return .none

    case .updateResponse(.failure(let error)):
        state.errorMessage = error.localizedDescription
        return .none
    }
}

// View
struct UserView: View {
    let store: Store<UserState, UserAction>

    var body: some View {
        WithViewStore(store) { viewStore in
            Group {
                if viewStore.isLoading {
                    ProgressView()
                } else if let error = viewStore.errorMessage {
                    Text("Error: \(error)")
                } else if let user = viewStore.user {
                    VStack {
                        Text(user.name)
                        TextField("Name", text: viewStore.binding(
                            get: \.user?.name ?? "",
                            send: UserAction.updateName
                        ))
                    }
                }
            }
            .onAppear {
                viewStore.send(.loadUser(userId))
            }
        }
    }
}
```

---

## BLoC Pattern - Flutter

```dart
// Events
abstract class UserEvent {}
class LoadUser extends UserEvent {
  final String userId;
  LoadUser(this.userId);
}
class UpdateUser extends UserEvent {
  final User user;
  UpdateUser(this.user);
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
    on<UpdateUser>(_onUpdateUser);
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

  Future<void> _onUpdateUser(UpdateUser event, Emitter<UserState> emit) async {
    try {
      await repository.updateUser(event.user);
      emit(UserLoaded(event.user));
    } catch (e) {
      emit(UserError(e.toString()));
    }
  }
}

// Widget
class UserScreen extends StatelessWidget {
  final String userId;

  const UserScreen({required this.userId});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => UserBloc(repository: context.read<UserRepository>())
        ..add(LoadUser(userId)),
      child: BlocBuilder<UserBloc, UserState>(
        builder: (context, state) {
          if (state is UserLoading) {
            return const CircularProgressIndicator();
          } else if (state is UserLoaded) {
            return UserView(user: state.user);
          } else if (state is UserError) {
            return Text('Error: ${state.message}');
          }
          return const SizedBox();
        },
      ),
    );
  }
}
```

---

## Dependency Injection

### iOS (Manual DI / Resolver)

```swift
// Dependency Container
class DependencyContainer {
    static let shared = DependencyContainer()

    lazy var userRepository: UserRepository = {
        UserRepositoryImpl(
            remoteDataSource: remoteDataSource,
            localDataSource: localDataSource
        )
    }()

    lazy var remoteDataSource: UserRemoteDataSource = {
        UserRemoteDataSourceImpl(apiClient: apiClient)
    }()

    lazy var localDataSource: UserLocalDataSource = {
        UserLocalDataSourceImpl()
    }()

    lazy var apiClient: APIClient = {
        APIClient()
    }()
}

// Usage
let viewModel = UserViewModel(
    repository: DependencyContainer.shared.userRepository
)
```

### Android (Dagger Hilt)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideApiService(): ApiService {
        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(MoshiConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository
}

// ViewModel with injection
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

---

**Choose the right architecture pattern for your app's complexity and team size!**

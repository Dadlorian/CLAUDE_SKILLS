# Setting Up Unity Addressables

## Installation
1. Package Manager → Addressables
2. Window → Asset Management → Addressables → Groups

## Converting Assets
```csharp
// 1. Select asset in Project
// 2. Inspector → Check "Addressable"
// 3. Assign to group
```

## Loading Assets
```csharp
using UnityEngine.AddressableAssets;
using UnityEngine.ResourceManagement.AsyncOperations;

public class AddressableLoader : MonoBehaviour
{
    public AssetReference enemyRef;

    async void Start()
    {
        // Load asset
        AsyncOperationHandle<GameObject> handle = enemyRef.LoadAssetAsync<GameObject>();
        await handle.Task;

        if (handle.Status == AsyncOperationStatus.Succeeded)
        {
            GameObject enemy = handle.Result;
            Instantiate(enemy);
        }

        // Release when done
        Addressables.Release(handle);
    }
}
```

## Benefits
- Reduce initial build size
- Load on demand
- Remote content updates
- Memory management

## Build
- Build → New Build → Default Build Script

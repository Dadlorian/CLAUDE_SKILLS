# Unity Input System Guide

## Setup
1. Package Manager → Input System
2. Create Input Actions asset
3. Generate C# class

## Input Actions
```csharp
using UnityEngine.InputSystem;

public class PlayerInput : MonoBehaviour
{
    private PlayerControls controls;

    void Awake()
    {
        controls = new PlayerControls();
    }

    void OnEnable()
    {
        controls.Player.Enable();
        controls.Player.Jump.performed += OnJump;
        controls.Player.Move.performed += OnMove;
    }

    void OnDisable()
    {
        controls.Player.Jump.performed -= OnJump;
        controls.Player.Move.performed -= OnMove;
        controls.Player.Disable();
    }

    void OnJump(InputAction.CallbackContext context)
    {
        Jump();
    }

    void OnMove(InputAction.CallbackContext context)
    {
        Vector2 input = context.ReadValue<Vector2>();
        Move(input);
    }
}
```

## Rebinding
```csharp
controls.Player.Jump.ApplyBindingOverride("<Keyboard>/space");
```

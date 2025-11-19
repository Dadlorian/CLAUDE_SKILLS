# Unity UI (uGUI) Quick Reference

## Canvas Types
- **Screen Space - Overlay**: Always on top
- **Screen Space - Camera**: Renders with camera
- **World Space**: 3D UI in world

## Common Components
```csharp
using UnityEngine.UI;

// Button
button.onClick.AddListener(OnButtonClick);

// Text
text.text = "Score: " + score;

// Image
image.sprite = newSprite;
image.color = Color.red;

// Slider
slider.value = health / maxHealth;
```

## Canvas Optimization
- Disable raycast on non-interactive elements
- Use Canvas Groups for batch operations
- Separate static/dynamic UI into different canvases

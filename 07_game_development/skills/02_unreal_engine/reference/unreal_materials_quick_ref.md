# Unreal Materials Quick Reference

## Material Types
- **Material**: Base material
- **Material Instance**: Runtime-editable parameters
- **Material Function**: Reusable node graphs

## Common Nodes
- **Lerp**: Linear interpolation
- **Multiply**: Multiply colors/values
- **TextureSample**: Sample texture
- **Fresnel**: Edge detection
- **WorldPosition**: Get world coordinates

## Parameters
```cpp
// Dynamic Material Instance
UMaterialInstanceDynamic* DynMaterial = UMaterialInstanceDynamic::Create(BaseMaterial, this);
DynMaterial->SetScalarParameterValue("Glow", 1.5f);
DynMaterial->SetVectorParameterValue("Color", FLinearColor::Red);
```

## PBR Inputs
- Base Color
- Metallic (0-1)
- Roughness (0-1)
- Normal
- Emissive

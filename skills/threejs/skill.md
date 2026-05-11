# Three.js / React Three Fiber Skill

## Performance Rules (4GB RAM)
- Max 50K triangles per scene
- Use instanced meshes for repeated geometry
- LOD (Level of Detail) for complex models
- Compress textures (max 1024x1024)
- Use draco compression for GLTF models
- Dispose geometries/materials on unmount
- RequestAnimationFrame-based rendering only
- Fallback to 2D for devices without WebGL

## Common Patterns
- Floating particles background
- 3D product viewers
- Interactive globe/map
- Animated geometric shapes
- Scroll-driven 3D transitions

## Required: <Canvas> with Suspense fallback
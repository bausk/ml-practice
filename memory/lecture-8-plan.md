# Lecture 8 — Detailed Plan: 3D Scene Understanding, SfM, and Level Construction

**Module:** Computer Vision for Games (Module 2)
**Style:** Hands-on, engaging, demo-driven; each concept paired with a concrete game/drone example.

---

## Part 1: From 2D to 3D — Why 3D Vision Matters (10 min)

- Recap: CNNs see images, but games and robots live in 3D
- Problem framing: how do you get 3D geometry from flat photos?
- Three answers: depth sensors (LiDAR, stereo), depth estimation (monocular ML), geometric reconstruction (SfM)
- **Demo hook:** show a real photogrammetry scan of a location that appears in a AAA game (e.g., Battlefield's real-world reference sites)

---

## Part 2: Structure from Motion — Core Algorithm (25 min)

### 2.1 Intuition
- Human vision: two eyes, parallax → depth. Camera moving = virtual second eye.
- Key insight: if you know where features appear across multiple photos, you can back-calculate both camera positions AND 3D point locations.

### 2.2 Incremental SfM Pipeline (step by step)
1. **Feature extraction** — SIFT/SuperPoint; invariant to scale/rotation/lighting
2. **Feature matching** — find the same point across image pairs
3. **Geometric verification** — fundamental matrix / essential matrix; RANSAC to reject outliers
4. **Initialization** — pick a good seed image pair, triangulate initial points
5. **Image registration** — add new cameras via PnP (Perspective-n-Point)
6. **Triangulation** — extend the sparse point cloud
7. **Bundle adjustment** — jointly minimize reprojection error; the expensive step
- Output: sparse point cloud + camera poses (no appearance/color yet)

### 2.3 SfM vs. related techniques (comparison table)
| | SfM | MVS | SLAM | NeRF | 3D Gaussian Splatting |
|---|---|---|---|---|---|
| Input | Unordered photos | SfM output | Video stream (real-time) | Photos + SfM poses | Photos + SfM poses |
| Output | Sparse points + poses | Dense mesh | Live pose + sparse map | Novel views | Real-time splats |
| Speed | Offline | Offline | Real-time | Hours to train | 30–60 min train |
| Geometry | Best accuracy | Good | Approximate | Moderate | Moderate |
| Render quality | None | Low | None | Photorealistic | Photorealistic |
- SfM feeds into everything else — it's the "skeleton" of the pipeline

### 2.4 Key tools
- **COLMAP** — open source, gold standard accuracy, CLI + GUI
- **RealityCapture** — commercial (free under $1M revenue), fastest on market, UE5 integration
- **Meshroom/AliceVision** — open source, node graph GUI, good for teaching

---

## Part 3: SfM in Drone Navigation (15 min)

### 3.1 Pre-flight mapping workflow
- Drone captures images → SfM+MVS offline → georeferenced orthomosaic + Digital Surface Model
- Used for: mission planning, area coverage, infrastructure inspection
- Tools: Pix4D, OpenDroneMap (open source), DJI Terra

### 3.2 Why drones don't use SfM for real-time flight
- SfM is batch/offline → too slow for live avoidance
- Real-time: **Visual-Inertial Odometry (VIO)** + SLAM (ORB-SLAM3, VINS-Mono)
- SfM map used as a *prior* → SLAM localizes against it

### 3.3 Scale ambiguity problem
- Monocular SfM gives geometry up to unknown scale
- Recovery: GPS tags, IMU integration, known reference objects
- **Discussion point:** why scale matters for a drone (1 m vs 10 m obstacle is very different)

### 3.4 Demo/exercise idea
- OpenDroneMap web demo with drone footage → show resulting orthomosaic in browser (WebODM)

---

## Part 4: From Real World to Game Level (20 min)

### 4.1 Full photogrammetry-to-game pipeline
1. Capture: DSLR photos / drone / phone video
2. SfM alignment → sparse point cloud + camera poses
3. MVS dense reconstruction → dense point cloud or mesh
4. Mesh cleanup + retopology + UV unwrap + PBR textures
5. Import to Unreal Engine 5 / Unity

### 4.2 Who actually does this
- **EA DICE** (Battlefield series): real locations photographed, SfM+MVS processed
- **Call of Duty: Modern Warfare, Star Wars Battlefront**: photogrammetry-scanned environments
- **Quixel Megascans** (Epic Games): 18,000+ scanned assets, free for UE5 users
- Saves months of manual 3D modeling for realistic environments

### 4.3 The 3DGS revolution (2024-2025)
- Gaussian Splatting: phone video → real-time renderable 3D scene in ~45 min
- Real-time at 90+ FPS vs NeRF's seconds/frame
- **Current limitation for games:** no mesh = no collision/physics/LOD
- **Use now:** cinematic backdrops, VR environments, rapid prototyping, pre-vis
- UE5 plugin (XVERSE XScene, Apache 2.0) enables playback
- glTF standardization (`KHR_gaussian_splatting`) arrived August 2025 → expect game engine native support soon

### 4.4 Hybrid workflow (current best practice)
```
Phone/drone video → COLMAP/RealityCapture (poses) →
  ├── PostShot/Nerfstudio → 3DGS (high-quality visual backdrop)
  └── COLMAP dense/OpenMVS → mesh (collision geometry)
Both imported into UE5
```

### 4.5 Hands-on demo idea
- Capture 20–30 photos of a room/object with phone
- Run through Meshroom (free) to get mesh + textures
- Or: use pre-captured dataset and RealityCapture trial

---

## Part 5: Reconstructed Environments for RL Agent Training (15 min)

### 5.1 The problem: RL agents need 3D environments to explore
- Training a navigation bot or game AI requires many hours of in-environment experience
- Building custom 3D training levels by hand is expensive
- Solution: scan real buildings → instant photorealistic training environment

### 5.2 Key platforms
- **Meta Habitat** (habitat-sim) — fast 3D simulator for embodied AI; loads real-world scans
- **Habitat-Matterport 3D (HM3D)** — 1,000 real building scans (homes, stores); standard benchmark
- **Replica Dataset** (Meta) — 18 high-quality indoor scans with semantics; RGB-D + mesh
- **iGibson** (Stanford) — interactive scenes; includes RL starter code (SAC); navigation + object interaction

### 5.3 Scan → training environment pipeline
1. RGB-D scan (or SfM+MVS) → mesh
2. Semantic annotation (rooms, objects, walkable areas)
3. Load into simulator → RL agent trains on: point-goal navigation, object-goal nav, instruction following

### 5.4 Why this matters for games
- Same technique: scan a real location → RL bot learns to navigate it
- Use case: train an FPS bot on a scan of a real building before the game level is finalized
- Use case: evaluate bot difficulty on photorealistic level before manual polish
- AirSim / UnrealCV: UE5 as simulation backend for RL training

### 5.5 Emerging: SLAM3R (CVPR 2025)
- Real-time dense reconstruction from video via feed-forward networks (no explicit SfM/BA)
- Potential: live environment generation during gameplay for adaptive training

### 5.6 Discussion: sim-to-real and real-to-sim gap
- Agents trained in scanned real environments transfer better to real-world robots
- For games: trained in scan → deployed in stylized version of same geometry

---

## Part 6: Connecting to Other Topics in Lecture 8 (5 min recap)

- Object detection (YOLO) → NPC vision using detected objects in reconstructed 3D world
- Depth estimation → cheaper alternative to SfM for getting rough 3D in real-time
- NeRF → photorealistic novel-view synthesis; uses SfM poses as input
- **Full scene understanding pipeline:** detect objects + segment → estimate depth → reconstruct 3D → navigable game world

---

## Practical Exercise Options

**Option A (light):** Use Meshroom + provided photo set → build a mesh, inspect in viewer
**Option B (heavier):** COLMAP CLI on provided images → visualize sparse reconstruction
**Option C (conceptual):** Explore Habitat demo with HM3D scan; run a random-walk agent
**Option D (demo-only):** Live demo: capture phone photos in class → Meshroom or RealityCapture → show result next class

---

## Key Takeaways (student-facing)

1. SfM is the backbone of all 3D reconstruction: it gives you geometry and camera poses.
2. SfM alone is not enough for games — the pipeline is SfM → MVS → mesh → engine.
3. NeRF and 3DGS are revolutionizing appearance; SfM still provides the structure.
4. Real-world scans → game environments: saves weeks of modeling AND enables RL training.
5. Drone navigation = offline SfM map + real-time SLAM; same principle, different time scale.

---

## Tools to Reference

| Tool | Use | Cost |
|---|---|---|
| COLMAP | SfM + dense reconstruction | Free |
| Meshroom / AliceVision | GUI SfM pipeline | Free |
| RealityCapture | Fast SfM+MVS+texturing | Free (<$1M revenue) |
| OpenDroneMap / WebODM | Drone mapping | Free/open source |
| Nerfstudio | NeRF + 3DGS training | Free |
| PostShot | 3DGS from video | Commercial |
| Habitat-sim | RL training in scanned environments | Free (Meta) |
| iGibson | Interactive RL environments | Free (Stanford) |
| XVERSE XScene | 3DGS playback in UE5 | Free (Apache 2.0) |

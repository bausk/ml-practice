import * as THREE from 'three';

const MODE = 'immersive-ar';

async function activateXR(): Promise<void> {
    const canvas = document.createElement("canvas");
    document.body.appendChild(canvas);
    
    const gl = canvas.getContext("", {xrCompatible: true});
    if (!gl) throw new Error("WebGL not supported");

    // initialize scene
    const scene = null;

    // initialize materials
    const materials = [
        new THREE.MeshBasicMaterial({color: 0xff0000}),
        // ...
    ];

    // initialize cube
    const cube = null;
    // set cube position
    cube.position.set(1, 1, 1);
    // add cube to scene
    scene.add(cube);

    
    // initialize renderer
    const renderer = null;
    // disable renderer auto clear

    // initialize camera
    const camera = null;
    // disable camera matrix update

    if (!navigator.xr) {
        throw new Error("WebXR is not supported by your browser");
    }

    try {
        const supported = await navigator.xr.isSessionSupported(MODE);
        if (!supported) {
            throw new Error(`${MODE} mode is not supported by your browser/device`);
        }
    } catch (e) {
        throw new Error('Error checking WebXR support: ' + e);
    }

    const session = await navigator.xr.requestSession(
        MODE,
        {
            requiredFeatures: ['local']
        }
    );

    // initialize XRWebGLLayer
    const baseLayer = null;
    // update render state
    // session.???

    const referenceSpaceTypes: XRReferenceSpaceType[] = [
        'local',
        'local-floor',
        'bounded-floor',
        'unbounded',
        'viewer'
    ];

    let referenceSpace: XRReferenceSpace | null = null;

    // observe how reference space types and request reference space
    // are applied to the scene
    for (const spaceType of referenceSpaceTypes) {
        try {
            // request reference space
            referenceSpace = null;
            console.log('Reference space established:', spaceType);
            break;
        } catch(e) {
            console.log(e);
            console.log('Reference space failed:', spaceType);
            continue;
        }
    }

    if (!referenceSpace) {
        throw new Error('No reference space could be established');
    }

    // Implement onXRFrame
    session.requestAnimationFrame(); // TODO: Implement correct call
}

// Make the function available globally
(window as any).activateXR = activateXR; 
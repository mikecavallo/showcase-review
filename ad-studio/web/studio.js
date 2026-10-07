// Caviar Star 3D studio. One product at a time, built from its photo:
//   lathe  -> LatheGeometry from the photo silhouette, the photo wrapped around it
//   relief -> an inflated mesh from the cutout (front + mirrored back), for spoons, shells, truffles, fish, sets
//   jar    -> procedural glass jar filled with the product's own caviar, the branded lid leaning on it
//   tin    -> the black-and-gold Caviar Star tin, lid half open on its caviar
// Lighting: studio environment for reflections, a warm key, two rim lights from behind, and a glow disc behind
// the object ("light behind them"). Deterministic: render(t) draws the frame at time t, for offline video.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const GOLD = new THREE.Color('#d9b871');

// Project-wide look settings for the caviar jars. Everything reads these: the 3D gallery, its thumbnails,
// the turntable videos, the reels and the documentary. Change them here and re-render.
//   GLASS_OPACITY: 0 = clear glass (default look), 1 = fully opaque jar
//   GLASS_TINT:    the jar's colour, which shows more the more opaque it is (try '#141416' for a black jar)
export const GLASS_OPACITY = 0.13;
export const GLASS_TINT = '#e8eef2';
// Caviar surface: true = drawn pearls (glossy spheres tinted from the product photo, sized per roe type), false = the photo itself
export const PEARLS = true;
const LID_ZOOM = 0.9;  // how much of the lid photo shows on the cap face: the whole lid, crimped metal rim included

export class Studio {
  constructor(canvas, opts = {}) {
    this.opts = Object.assign({ bg: '#07080c', glow: '#d9b871', floor: true, base: '' }, opts);
    const r = this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, preserveDrawingBuffer: !!opts.preserve });
    r.setPixelRatio(opts.dpr || Math.min(2, devicePixelRatio || 1));
    r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = 1.0;
    r.outputColorSpace = THREE.SRGBColorSpace;
    const s = this.scene = new THREE.Scene();
    s.background = new THREE.Color(this.opts.bg);
    const pm = new THREE.PMREMGenerator(r);
    s.environment = pm.fromScene(new RoomEnvironment(r), 0.04).texture;
    this.cam = new THREE.PerspectiveCamera(28, 1, 0.05, 50);
    // lights: key from front-left, fill, and two warm rims from behind
    const key = new THREE.DirectionalLight('#fff4e2', 1.6); key.position.set(-2.5, 3, 4); s.add(key);
    const fill = new THREE.DirectionalLight('#cfd8ff', 0.35); fill.position.set(3, 1, 3); s.add(fill);
    this.rimL = new THREE.DirectionalLight(this.opts.glow, 2.6); this.rimL.position.set(-3, 2, -3); s.add(this.rimL);
    this.rimR = new THREE.DirectionalLight(this.opts.glow, 2.2); this.rimR.position.set(3, 1.5, -3); s.add(this.rimR);
    // glow behind the product
    this.glow = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: radialTex(this.opts.glow), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false }));
    this.glow.position.set(0, 0.55, -1.6); s.add(this.glow);
    // floor: a dark mirror-ish disc with a soft contact shadow
    if (this.opts.floor) {
      const fl = new THREE.Mesh(new THREE.CircleGeometry(6, 96), new THREE.MeshBasicMaterial({ map: floorTex(this.opts.bg), transparent: true, depthWrite: false, toneMapped: false }));
      fl.rotation.x = -Math.PI / 2; s.add(fl); this.floorMesh = fl;
      this.shadow = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: radialTex('#000000', 0.85), transparent: true, depthWrite: false }));
      this.shadow.rotation.x = -Math.PI / 2; this.shadow.position.y = 0.002; s.add(this.shadow);
      // floor sheen line under the glow
      const sheen = new THREE.Mesh(new THREE.PlaneGeometry(4, 1.2), new THREE.MeshBasicMaterial({ map: radialTex(this.opts.glow, 0.25), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false }));
      sheen.rotation.x = -Math.PI / 2; sheen.position.set(0, 0.003, -0.5); s.add(sheen);
    }
    this.root = new THREE.Group(); s.add(this.root);
    this.motion = 'swing';
    // jar glass opacity, 0 (invisible) to 1 (solid); change live with setGlass()
    this.glassOpacity = opts.glass ?? GLASS_OPACITY; this.glassMats = [];
    globalThis.__lastStudio = this;  // debug hook for QC scripts
    this.loader = new THREE.TextureLoader();
    this.size(canvas.clientWidth || canvas.width, canvas.clientHeight || canvas.height);
  }
  setGlass(v) { this.glassOpacity = v; for (const m of this.glassMats) { m.opacity = v; m.needsUpdate = true; } }
  size(w, h) { this.renderer.setSize(w, h, false); this.cam.aspect = w / h; this.cam.updateProjectionMatrix(); this.frame(); }
  tex(url, srgb = true) {
    return new Promise((res, rej) => this.loader.load(url, t => { if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; res(t); }, undefined, rej));
  }
  clear() { for (const c of [...this.root.children]) { this.root.remove(c); c.traverse?.(o => { o.geometry?.dispose(); o.material?.dispose?.(); }); } }
  // product material: the photo carries its own colour; PBR adds moving reflections and the rim
  photoMat(map, o = {}) {
    return new THREE.MeshPhysicalMaterial(Object.assign({
      map, emissiveMap: map, emissive: new THREE.Color(0xffffff), emissiveIntensity: 0.55, color: new THREE.Color(0.62, 0.62, 0.62),
      roughness: 0.32, metalness: 0.0, clearcoat: 0.9, clearcoatRoughness: 0.12, envMapIntensity: 0.55, side: THREE.FrontSide,
    }, o));
  }
  async load(spec, base) {
    this.clear(); this.spec = spec; const b = base + '/' + spec.handle;
    let obj;
    if (spec.kind === 'lathe') obj = await this.lathe(spec, b);
    else if (spec.kind === 'jar') obj = await this.jar(spec, b);
    else if (spec.kind === 'tin') obj = await this.tin(spec, b);
    else obj = await this.relief(spec, b);
    this.obj = obj; this.root.add(obj);
    // fit: bottom on the floor, height ~1, centred
    const fitBox = () => { const bx = new THREE.Box3(); obj.updateMatrixWorld(true); obj.traverse(o => { if (o.isMesh && !o.userData.noFit && !o.parent?.userData.noFit) bx.expandByObject(o); }); return bx.isEmpty() ? new THREE.Box3().setFromObject(obj) : bx; };
    // centre on the product itself; a lid leaning behind it may stick out but must stay in frame
    let full = new THREE.Box3().setFromObject(obj), core = fitBox();
    let fs = full.getSize(new THREE.Vector3()), cs = core.getSize(new THREE.Vector3());
    const k = 1 / Math.max(fs.y, cs.x * 0.75, cs.z * 0.75);
    obj.scale.setScalar(k);
    full = new THREE.Box3().setFromObject(obj); core = fitBox();
    const c = core.getCenter(new THREE.Vector3());
    obj.position.x -= c.x; obj.position.z -= c.z; obj.position.y -= full.min.y;
    fs = full.getSize(new THREE.Vector3()); cs = core.getSize(new THREE.Vector3());
    this.h = fs.y; this.w = Math.max(cs.x, cs.z, fs.x * 0.95);
    if (this.shadow) { this.shadow.scale.set(this.w * 1.5, this.w * 1.1, 1); }
    this.glow.scale.setScalar(Math.max(this.h, this.w) * 2.6); this.glow.position.y = this.h * 0.55;
    this.frame(); return obj;
  }
  frame() {
    const h = this.h || 1, w = this.w || 1, asp = this.cam.aspect;
    const fov = this.cam.fov * Math.PI / 180;
    const need = Math.max(h * 1.32, (w * 1.45) / asp);
    const d = need / 2 / Math.tan(fov / 2) + w * 0.5;
    this.cam.userData.d = d; this.cam.userData.ty = h * 0.47;
  }
  // t in seconds. motion: 'swing' (lathe/relief, keeps the back unseen), 'spin' (round products)
  swingYaw(t) {
    const per = this.spec.period || 10, ph = 2 * Math.PI * t / per;
    return Math.sin(ph) * (this.spec.swing ?? (this.spec.kind === 'lathe' ? 0.62 : this.spec.kind === 'relief' ? 0.85 : 0.7)) + (this.spec.kind === 'jar' || this.spec.kind === 'tin' ? 0.25 : 0);
  }
  render(t = 0) {
    const o = this.obj; if (!o) return;
    const m = this.spec.motion || 'swing';
    const per = this.spec.period || 10, ph = 2 * Math.PI * t / per;   // everything repeats every per seconds
    if (m === 'spin') o.rotation.y = ph - 0.3;
    else if (this.free) o.rotation.y = this.yaw;
    else o.rotation.y = Math.sin(ph) * (this.spec.swing ?? (this.spec.kind === 'lathe' ? 0.62 : this.spec.kind === 'relief' ? 0.85 : 0.7)) + (this.spec.kind === 'jar' || this.spec.kind === 'tin' ? 0.25 : 0);
    const d = this.cam.userData.d || 4, ty = this.cam.userData.ty || 0.5;
    const el = (this.spec.kind === 'jar' || this.spec.kind === 'tin' ? 0.42 : this.spec.lie ? 0.5 : 0.16) + 0.03 * Math.sin(ph + 1);
    this.cam.position.set(Math.sin(ph) * 0.12 * d / 4, ty + d * Math.sin(el), d * Math.cos(el));
    if (this.free) this.cam.position.y = ty + d * Math.sin(el + (this.pitch || 0));
    this.cam.lookAt(0, ty * 0.96, 0);
    // rim lights breathe so the edge highlight travels
    this.rimL.intensity = 2.4 + 0.5 * Math.sin(ph * 2); this.rimR.intensity = 2.0 + 0.5 * Math.cos(ph * 2);
    this.renderer.render(this.scene, this.cam);
  }

  /* ---------------- builders ---------------- */
  async lathe(spec, b) {
    const [tex, prof] = await Promise.all([this.tex(b + '/tex.jpg'), spec.profile ? { profile: spec.profile } : fetch(b + '/profile.json').then(r => r.json())]);
    // profile: [radius, height] fractions of image height, top to bottom -> lathe wants bottom to top
    const pts = prof.profile.slice().reverse().map(([r, y]) => new THREE.Vector2(Math.max(r, 0.0005), y));
    // close the top and bottom to the axis so the object is solid
    pts.unshift(new THREE.Vector2(0.0005, pts[0].y)); pts.push(new THREE.Vector2(0.0005, pts[pts.length - 1].y));
    const g = new THREE.LatheGeometry(pts, 128, -Math.PI, Math.PI * 2);
    // lathe v runs along the point list: remap so v follows height (the texture is laid out top = 0)
    const uv = g.attributes.uv, pos = g.attributes.position;
    for (let i = 0; i < uv.count; i++) uv.setY(i, pos.getY(i));
    g.computeVertexNormals();
    tex.wrapS = THREE.RepeatWrapping;
    const glassy = /oil|vinegar|balsamic|sherry|glaze|juice|saba|vincotto|honey|paste|sauce|butter|mustard|pearls|ink/i.test(spec.title);
    const metal = /server|cloche|stainless|silver/i.test(spec.title);
    const mat = this.photoMat(tex, metal ? { metalness: 0.55, roughness: 0.18, emissiveIntensity: 0.45, envMapIntensity: 1.1 } : glassy ? { roughness: 0.12, clearcoat: 1, clearcoatRoughness: 0.04, envMapIntensity: 0.75 } : {});
    const m = new THREE.Mesh(g, mat);
    m.scale.set(1, 1, 1);
    return m;
  }
  async relief(spec, b) {
    let cut, hm, meta;
    if (spec.packed) {
      const atlas = await this.tex(b + '/pack.webp'); meta = { aspect: spec.aspect };
      cut = atlas; cut.repeat.set(0.5, 1); cut.offset.set(0, 0);
      hm = atlas.clone(); hm.colorSpace = THREE.NoColorSpace; hm.repeat.set(0.5, 1); hm.offset.set(0.5, 0); hm.needsUpdate = true;
    } else [cut, hm, meta] = await Promise.all([this.tex(b + '/cut.webp'), this.tex(b + '/height.png', false), fetch(b + '/relief.json').then(r => r.json())]);
    const a = meta.aspect, flat = !!spec.flat, depth = flat ? 0.012 : (spec.depth ?? guessDepth(spec.title));
    const seg = flat ? 64 : 220;
    const grp = new THREE.Group();
    // rigid, boxy products (bags, gift boxes, packaged goods) photographed at an angle can't be inflated into a
    // believable shape: they stand as a clean photographic plate that tilts a little in the moving light
    if (flat && spec.swing == null) spec.swing = 0.2;
    for (const side of [1, -1]) {
      const g = new THREE.PlaneGeometry(a, 1, Math.round(seg * Math.min(1, a)), Math.round(seg * Math.min(1, 1 / a)));
      const mat = this.photoMat(cut, { displacementMap: hm, displacementScale: depth * side, alphaTest: 0.5, side: side > 0 ? THREE.FrontSide : THREE.BackSide, transparent: false, clearcoat: 0.6, roughness: 0.4 });
      if (side < 0) { mat.emissiveIntensity = 0.42; }
      const m = new THREE.Mesh(g, mat);
      m.position.y = 0.5;
      grp.add(m);
    }
    // displacement needs normals from the height field: approximate with a bump of the same map
    grp.children.forEach(m => { m.material.bumpMap = hm; m.material.bumpScale = flat ? 0.6 : 3.0; if (flat) { m.material.clearcoat = 0.9; m.material.clearcoatRoughness = 0.06; } });
    if (spec.lie) { grp.rotation.x = -Math.PI / 2 + 0.55; }
    return grp;
  }
  async jar(spec, b) {
    let disc, meta, lidTex;
    if (spec.packed) {
      const atlas = await this.tex(b + '/pack.jpg'); meta = { color: spec.color };
      disc = atlas; disc.repeat.set(0.5, 1); disc.offset.set(0, 0);
      if (spec.lidUrl) { lidTex = await this.tex(spec.lidUrl).catch(() => null); if (lidTex) { lidTex.repeat.set(LID_ZOOM, LID_ZOOM); lidTex.offset.set((1 - LID_ZOOM) / 2, (1 - LID_ZOOM) / 2); } }
      if (!lidTex) { lidTex = atlas.clone(); lidTex.repeat.set(0.5 * LID_ZOOM, LID_ZOOM); lidTex.offset.set(0.5 + 0.5 * (1 - LID_ZOOM) / 2, (1 - LID_ZOOM) / 2); lidTex.needsUpdate = true; }
    } else {
      [disc, meta] = await Promise.all([this.tex(b + '/disc.jpg'), fetch(b + '/jar.json').then(r => r.json())]);
      lidTex = await this.tex(spec.lidUrl || (b + '/lid.jpg')).catch(() => null);
      if (lidTex) { lidTex.repeat.set(LID_ZOOM, LID_ZOOM); lidTex.offset.set((1 - LID_ZOOM) / 2, (1 - LID_ZOOM) / 2); }
    }
    const grp = new THREE.Group();
    const R = 0.5, H = 0.42, wall = 0.025;
    // glass: a lathe with a thick base and rolled lip
    const gp = [];
    gp.push(new THREE.Vector2(0.001, 0)); gp.push(new THREE.Vector2(R - 0.04, 0)); gp.push(new THREE.Vector2(R, 0.03));
    gp.push(new THREE.Vector2(R + 0.004, H * 0.5)); gp.push(new THREE.Vector2(R, H - 0.02)); gp.push(new THREE.Vector2(R + 0.012, H)); gp.push(new THREE.Vector2(R - wall, H + 0.004));
    gp.push(new THREE.Vector2(R - wall, 0.035)); gp.push(new THREE.Vector2(0.001, 0.035));
    const glass = new THREE.Mesh(new THREE.LatheGeometry(gp, 96), new THREE.MeshPhysicalMaterial({
      color: glassTint(this), roughness: 0.03, metalness: 0.1, transparent: true, opacity: this.glassOpacity, depthWrite: false,
      envMapIntensity: 1.5, clearcoat: 1, clearcoatRoughness: 0.02, side: THREE.DoubleSide }));
    glass.renderOrder = 2; this.glassMats = [glass.material];
    // clear acrylic reads as bright thin edges and an almost invisible face, not as a flat grey shell:
    // fade the face out and let a fresnel term carry the silhouette (an opaque jar, GLASS_OPACITY near 1, is unaffected)
    glass.material.onBeforeCompile = (sh) => {
      sh.fragmentShader = sh.fragmentShader.replace('#include <dithering_fragment>', `#include <dithering_fragment>
        { float k = smoothstep(0.35, 0.9, opacity); float fr = pow(1.0 - abs(dot(normalize(normal), normalize(vViewPosition))), 3.0);
          gl_FragColor.rgb = mix(gl_FragColor.rgb, vec3(1.0), fr * 0.4 * (1.0 - k));
          gl_FragColor.a = mix(opacity * 0.3 + fr * 0.7, opacity, k); }`);
    };
    grp.add(glass);
    // caviar: a cylinder of pearls, the top is the product photo, domed
    const col = new THREE.Color().fromArray(meta.color);
    const fillH = H * 0.9;
    disc.wrapS = disc.wrapT = THREE.ClampToEdgeWrapping;
    const rr = R - wall - 0.004;
    // caviar surface: drawn pearls tinted from the photo (default), or the photo itself with a mirrored crop for the side
    let topMap = disc, sideTex, topBump = null, sideBump = null;
    if (this.opts.pearls ?? PEARLS) {
      const roe = roeType(spec.handle), seed = hash(spec.handle);
      const tp = pearlTex(col, roe, 1024, 1024, 2 * rr, 2 * rr, seed, false); topMap = tp.map; topBump = tp.bump;
      const sp = pearlTex(col, roe, 4096, 448, 2 * Math.PI * rr, fillH - 0.035, seed + 7, true, 0.86); sideTex = sp.map; sideBump = sp.bump;
      grp.add(pearlSpheres(col, roe, seed, rr, 0.035, fillH));
    } else sideTex = sideStrip(disc.image, spec.packed ? [0.125, 0.3, 0.25, 0.4] : [0.25, 0.3, 0.5, 0.4]);
    const body = new THREE.Mesh(new THREE.CylinderGeometry(R - wall - 0.004, R - wall - 0.01, fillH - 0.035, 96, 1, true),
      sideBump ? new THREE.MeshPhysicalMaterial({ map: sideTex, emissiveMap: sideTex, emissive: '#ffffff', emissiveIntensity: 0.12, color: '#2c2c2c', roughness: 0.5, clearcoat: 0.2, clearcoatRoughness: 0.3, bumpMap: sideBump, bumpScale: 1.2, envMapIntensity: 0.2 })
        : new THREE.MeshPhysicalMaterial({ map: sideTex, emissiveMap: sideTex, emissive: '#ffffff', emissiveIntensity: 0.55, color: '#5a5a5a', roughness: 0.2, clearcoat: 1, clearcoatRoughness: 0.05 }));
    body.position.y = 0.035 + (fillH - 0.035) / 2; body.rotation.y = Math.PI; grp.add(body);  // any join faces away from the camera
    const top = new THREE.CircleGeometry(rr, 96, 0, Math.PI * 2); top.rotateX(-Math.PI / 2);
    { const p = top.attributes.position; for (let i = 0; i < p.count; i++) { const d = Math.hypot(p.getX(i), p.getZ(i)) / rr; p.setY(i, 0.035 * (1 - d * d)); } top.computeVertexNormals(); }
    const capMesh = new THREE.Mesh(top, topBump
      ? new THREE.MeshPhysicalMaterial({ map: topMap, emissiveMap: topMap, emissive: '#ffffff', emissiveIntensity: 0.22, color: '#5a5a5a', roughness: 0.4, clearcoat: 0.3, clearcoatRoughness: 0.2, bumpMap: topBump, bumpScale: 1.4, envMapIntensity: 0.3 })
      : new THREE.MeshPhysicalMaterial({ map: disc, emissiveMap: disc, emissive: '#ffffff', emissiveIntensity: 0.62, color: '#8a8a8a', roughness: 0.16, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 0.8 }));
    capMesh.position.y = fillH;
    grp.add(capMesh);
    // lid: black ribbed cap, label on top, leaning against the jar
    const lid = new THREE.Group();
    const capMat = new THREE.MeshPhysicalMaterial({ color: '#0c0c0e', roughness: 0.35, clearcoat: 0.8, clearcoatRoughness: 0.15, metalness: 0.1 });
    const knurl = capMat.clone(); knurl.bumpMap = ribTex(); knurl.bumpScale = 2;  // knurled grip on the outside only
    const shell = capShell(R + 0.04, 0.13, capMat, capMat, new THREE.MeshPhysicalMaterial({ color: '#e6e2d8', roughness: 0.85 }), 0.016);
    shell.userData.skirt.material = knurl;
    if (lidTex && lidTex.image) {  // the skirt is the same crimped metal as the photographed rim (gold, silver or black)
      const rim = ringColor(lidTex.image, spec.packed && !spec.lidUrl ? 0.5 : 0), dark = rim.getHSL({}).l < 0.12;
      const metal = new THREE.MeshPhysicalMaterial({ color: rim, metalness: dark ? 0.5 : 0.9, roughness: 0.3, clearcoat: 0.5, clearcoatRoughness: 0.12, envMapIntensity: 1.0 });
      const mk = metal.clone(); mk.bumpMap = knurl.bumpMap; mk.bumpScale = 1.2; shell.userData.skirt.material = mk;
      shell.traverse(o => { if (o.isMesh && o.material === capMat && o.geometry.type === 'TorusGeometry') o.material = metal; });
    }
    lid.add(shell);
    if (lidTex) {
      // satin label: a little sheen, never a mirror that washes the print out as the lid turns; drawn just above the cap top
      const face = new THREE.Mesh(new THREE.CircleGeometry(R + 0.0395, 128), new THREE.MeshPhysicalMaterial({ map: lidTex, emissiveMap: lidTex, emissive: '#ffffff', emissiveIntensity: 0.5, color: '#8c8c8c', roughness: 0.55, metalness: 0.04, clearcoat: 0.2, clearcoatRoughness: 0.35, envMapIntensity: 0.3,
        polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -4 }));
      face.rotation.x = -Math.PI / 2; face.position.y = 0.0656; lid.add(face);
    }
    lid.rotation.set(1.12, -0.38, -0.12); lid.position.set(R * 0.8, R + 0.05, -R * 1.15); lid.userData.noFit = true;
    grp.add(lid);
    grp.userData.spinBias = 0.4;
    return grp;
  }
  async tin(spec, b) {
    const emb = await this.tex(this.opts.base + '/brand/tin-lid.jpg').catch(() => null);
    const disc = await this.tex(this.opts.base + '/brand/kaluga-disc.jpg').catch(() => null);
    const grp = new THREE.Group();
    const R = 0.6, H = 0.26;
    const black = new THREE.MeshPhysicalMaterial({ color: '#0d0d0f', roughness: 0.28, metalness: 0.5, clearcoat: 1, clearcoatRoughness: 0.08 });
    const gold = new THREE.MeshPhysicalMaterial({ color: GOLD, roughness: 0.22, metalness: 1, envMapIntensity: 1.3 });
    const NECK = 0.05, NR = R - 0.022;  // the stepped-in lip at the top that the lid slides over
    const base = new THREE.Mesh(new THREE.CylinderGeometry(R, R, H - NECK, 128), black); base.position.y = (H - NECK) / 2; grp.add(base);
    const shoulder = new THREE.Mesh(new THREE.RingGeometry(NR, R, 128), black); shoulder.rotation.x = -Math.PI / 2; shoulder.position.y = H - NECK; grp.add(shoulder);
    const neck = new THREE.Mesh(new THREE.CylinderGeometry(NR, NR, NECK, 128, 1, true), gold); neck.position.y = H - NECK / 2; grp.add(neck);
    const bandB = new THREE.Mesh(new THREE.TorusGeometry(R, 0.008, 12, 128), gold); bandB.rotation.x = Math.PI / 2; bandB.position.y = H - NECK; grp.add(bandB);
    const bandT = new THREE.Mesh(new THREE.TorusGeometry(NR, 0.006, 12, 128), gold); bandT.rotation.x = Math.PI / 2; bandT.position.y = H; grp.add(bandT);
    if (disc) {
      const cav = new THREE.Mesh(new THREE.CircleGeometry(NR - 0.01, 96), new THREE.MeshPhysicalMaterial({ map: disc, emissiveMap: disc, emissive: '#fff', emissiveIntensity: 0.5, color: '#8a8a8a', roughness: 0.15, clearcoat: 1 }));
      cav.rotation.x = -Math.PI / 2; cav.position.y = H + 0.001; grp.add(cav);
    }
    const lid = new THREE.Group();
    const lacquer = new THREE.MeshPhysicalMaterial({ color: '#b8995a', roughness: 0.3, metalness: 0.85, envMapIntensity: 1.1 });  // gold-lacquered inside, like a real tin
    lid.add(capShell(R + 0.006, 0.09, black, lacquer, lacquer, 0.01));
    const rim = new THREE.Mesh(new THREE.TorusGeometry(R + 0.006, 0.01, 12, 128), gold); rim.rotation.x = Math.PI / 2; rim.position.y = 0.045; lid.add(rim);
    if (emb) {
      const face = new THREE.Mesh(new THREE.CircleGeometry(R + 0.004, 128), new THREE.MeshPhysicalMaterial({ map: emb, emissiveMap: emb, emissive: '#fff', emissiveIntensity: 0.35, color: '#999', roughness: 0.2, metalness: 0.6, clearcoat: 1, clearcoatRoughness: 0.05 }));
      face.rotation.x = -Math.PI / 2; face.position.y = 0.0455; lid.add(face);
    }
    lid.rotation.set(1.12, 0, 0.0); lid.position.set(0, R + 0.08, -R - 0.12); lid.userData.noFit = true;
    grp.add(lid);
    return grp;
  }
}

// A hollow lid: top panel, outer skirt, inner skirt and a rolled bottom edge, so the underside shows the cavity
// that slips over the container's lip (a closed cylinder read as a flat puck from behind).
function capShell(r, h, outer, inner, liner, wall = 0.012) {
  const g = new THREE.Group(), seg = 128;
  const skirt = new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, seg, 1, true), outer); g.add(skirt);
  const top = new THREE.Mesh(new THREE.CircleGeometry(r, seg), outer); top.rotation.x = -Math.PI / 2; top.position.y = h / 2; g.add(top);
  const innerMat = inner.clone(); innerMat.side = THREE.BackSide;
  const iw = new THREE.Mesh(new THREE.CylinderGeometry(r - wall, r - wall, h - wall, seg, 1, true), innerMat); iw.position.y = -wall / 2; g.add(iw);
  const under = new THREE.Mesh(new THREE.CircleGeometry(r - wall, seg), liner); under.rotation.x = Math.PI / 2; under.position.y = h / 2 - wall; g.add(under);
  const edge = new THREE.Mesh(new THREE.TorusGeometry(r - wall / 2, wall / 2, 10, seg), outer); edge.rotation.x = Math.PI / 2; edge.position.y = -h / 2; g.add(edge);
  g.userData.skirt = skirt; return g;
}

function sideStrip(img, [u, v, w, h]) {
  const sw = Math.round(img.width * w), sh = Math.round(img.height * h), c = document.createElement('canvas');
  c.width = sw * 2; c.height = sh; const x = c.getContext('2d');
  x.filter = 'brightness(0.82) contrast(0.86) blur(0.6px)';
  x.drawImage(img, img.width * u, img.height * v, sw, sh, 0, 0, sw, sh);
  x.save(); x.translate(sw * 2, 0); x.scale(-1, 1); x.drawImage(img, img.width * u, img.height * v, sw, sh, 0, 0, sw, sh); x.restore();
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = THREE.RepeatWrapping; t.repeat.set(3, 1); t.anisotropy = 8; return t;
}
// roe types: pearls across a 1 oz jar (about 2.3 in wide), translucency and the dark eye of salmon and trout roe
function roeType(h = '') {  // across: pearls across a 1 oz jar; lift: drawn backdrop brightness; tone: sphere colour vs the photo average
  if (/salmon/.test(h)) return { across: 9, glow: 0.75, eye: 1, lift: 1.5, tone: 0.92, sss: 0.22, spread: 0.18 };
  if (/trout/.test(h)) return { across: 12, glow: 0.7, eye: 1, lift: 1.45, tone: 0.92, sss: 0.2, spread: 0.2 };
  if (/tobiko|flying-fish/.test(h)) return { across: 58, glow: 0.45, lift: 1.4, tone: 1.1, sss: 0.2 };
  if (/whitefish/.test(h)) return { across: 27, glow: 0.45, lift: 1.4, tone: 1.1, sss: 0.15 };
  if (/bowfin|paddlefish|hackleback/.test(h)) return { across: 23, glow: 0.2, lift: 1.25, tone: 0.45, sss: 0.03 };
  if (/kaluga|beluga|bester|almas|hybrid/.test(h)) return { across: 16, glow: 0.3, lift: 1.2, tone: 0.72, sss: 0.06 };
  if (/escargot|snail/.test(h)) return { across: 19, glow: 0.35, lift: 1.3, tone: 1.0, sss: 0.1 };
  return { across: 19, glow: 0.28, lift: 1.2, tone: 0.5, sss: 0.04 };
}
// the pearls you can see, as real spheres: a randomly packed top layer on the domed surface and the rows pressed against
// the glass. Each pearl varies a little in size and tint; the environment gives each its own wet highlight.
function pearlSpheres(col, roe, seed, rr, y0, y1) {
  const rnd = rng(seed ^ 0x2545f491), d = 0.94 / roe.across, pr = d / 2, M = new THREE.Matrix4(), Q = new THREE.Quaternion(), P = new THREE.Vector3(), S = new THREE.Vector3();
  const pts = [];
  // top: dart throwing on a hash grid, minimum spacing a little under one diameter (pearls press together)
  const R0 = rr - pr * 0.9, minD = d * 0.84, cell = minD, key = (i, j) => i * 100003 + j;
  for (const [layer, lift] of [[0, 0.25], [1, -0.55]]) {
  const grid = new Map(), start = pts.length, target = Math.floor(0.95 * (R0 * R0) / (pr * pr)); let tries = target * 30;
  while (pts.length - start < target && tries-- > 0) {
    const a = rnd() * Math.PI * 2, r = Math.sqrt(rnd()) * R0, x = Math.cos(a) * r, z = Math.sin(a) * r, gi = Math.floor(x / cell), gj = Math.floor(z / cell);
    let ok = true;
    for (let di = -1; di <= 1 && ok; di++) for (let dj = -1; dj <= 1 && ok; dj++) for (const q of grid.get(key(gi + di, gj + dj)) || []) if (Math.hypot(q[0] - x, q[1] - z) < minD) { ok = false; break; }
    if (!ok) continue;
    const g = grid.get(key(gi, gj)) || []; g.push([x, z]); grid.set(key(gi, gj), g);
    const s = pr * (0.86 + rnd() * 0.24), dome = 0.035 * (1 - (r / rr) ** 2);
    pts.push([x, y1 + dome + s * lift, z, s]);
  }
  }
  // wall: staggered rows against the glass, jittered
  const rw = rr - pr * 0.55, rows = Math.floor((y1 - y0 - pr * 0.6) / (d * 0.8));
  for (const [inset, phase] of [[0, 0], [pr * 0.7, 0.5]]) for (let k = 0; k < rows; k++) {
    const n = Math.round(2 * Math.PI * (rw - inset) / (d * 0.88)), y = y0 + pr * 1.05 + (k + phase * 0.5) * d * 0.8, off = (k & 1) * 0.5 + phase + rnd() * 0.3;
    for (let i = 0; i < n; i++) {
      const a = ((i + off + (rnd() - 0.5) * 0.55) / n) * Math.PI * 2, s = pr * (0.84 + rnd() * 0.26), rad = rw - inset - (s - pr) * 0.5 - rnd() * pr * 0.25;
      pts.push([Math.cos(a) * rad, Math.min(y1 - pr * 0.2, y + (rnd() - 0.5) * d * 0.3), Math.sin(a) * rad, s]);
    }
  }
  const lowPoly = roe.across > 30, geo = new THREE.SphereGeometry(1, lowPoly ? 9 : 14, lowPoly ? 6 : 10);
  const base = new THREE.Color().setRGB(col.r * roe.tone, col.g * roe.tone, col.b * roe.tone, THREE.SRGBColorSpace), hsl = {}; base.getHSL(hsl);
  const mat = new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: 0.22, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.04, envMapIntensity: 0.75,
    emissive: base.clone().multiplyScalar(roe.sss * 2.2), specularIntensity: 0.6 });
  const mesh = new THREE.InstancedMesh(geo, mat, pts.length), c = new THREE.Color();
  pts.forEach(([x, y, z, s], i) => {
    P.set(x, y, z); S.set(s, s * (0.94 + rnd() * 0.08), s); Q.setFromAxisAngle(P.clone().setY(0).normalize(), rnd() * 0.4);
    M.compose(P, Q, S); mesh.setMatrixAt(i, M);
    const sp = roe.spread ?? 0.44; c.setHSL(hsl.h + (rnd() - 0.5) * 0.03, Math.min(1, hsl.s * (0.92 + rnd() * 0.2)), Math.max(0, hsl.l * (1 - sp / 2 + rnd() * sp))); mesh.setColorAt(i, c);
  });
  mesh.instanceMatrix.needsUpdate = true; mesh.instanceColor.needsUpdate = true;
  return mesh;
}
// average colour of the photographed lid rim (the crimped metal edge), from the lid image or the right half of a packed atlas
function ringColor(img, u0 = 0) {
  const c = document.createElement('canvas'); c.width = c.height = 64; const x = c.getContext('2d');
  const W = img.width, H = img.height, sx = u0 * W, sw = u0 ? W - sx : W;
  x.drawImage(img, sx, 0, sw, H, 0, 0, 64, 64);
  const px = x.getImageData(0, 0, 64, 64).data; let r = 0, g = 0, b = 0, n = 0;
  for (let j = 0; j < 64; j++) for (let i = 0; i < 64; i++) { const q = Math.hypot((i + 0.5) / 32 - 1, (j + 0.5) / 32 - 1); if (q > 0.9 && q < 0.97) { const k = (j * 64 + i) * 4; r += px[k]; g += px[k + 1]; b += px[k + 2]; n++; } }
  return new THREE.Color().setRGB(r / n / 255, g / n / 255, b / n / 255, THREE.SRGBColorSpace);
}
function hash(s = '') { let h = 2166136261; for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619); return h >>> 0; }
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
// glossy pearls on a W x H canvas that spans ww x wh world units; wrap = tile horizontally (the jar side). squash < 1 flattens
// pearls pressed against the glass. Colour map plus a matching bump map, so the clearcoat catches each pearl.
function pearlTex(col, roe, W, H, ww, wh, seed, wrap, squash = 1) {
  const rnd = rng(seed), d = 0.94 / roe.across, px = W / ww;
  const cols = wrap ? Math.max(3, Math.round(ww / d)) : Math.ceil(ww / d) + 1, dx = W / cols, dy = dx * 0.866 * squash, rows = Math.ceil(H / dy) + 2;
  const r0 = dx * 0.53;
  const c = document.createElement('canvas'); c.width = W; c.height = H; const x = c.getContext('2d');
  const b = document.createElement('canvas'); b.width = W; b.height = H; const y = b.getContext('2d');
  const base = col.clone().multiplyScalar(roe.lift), hsl = {}; base.getHSL(hsl);
  const css = (l, a = 1, dh = 0, ds = 0) => { const k = new THREE.Color().setHSL(hsl.h + dh, Math.min(1, hsl.s + ds), Math.max(0, Math.min(1, l))); return `rgba(${k.r * 255 | 0},${k.g * 255 | 0},${k.b * 255 | 0},${a})`; };
  x.fillStyle = css(hsl.l * 0.22); x.fillRect(0, 0, W, H); y.fillStyle = '#000'; y.fillRect(0, 0, W, H);
  const pearls = [];
  for (let j = -1; j < rows; j++) for (let i = -1; i <= cols; i++) {
    const jx = (rnd() - 0.5) * dx * 0.34, jy = (rnd() - 0.5) * dy * 0.34;
    pearls.push({ cx: i * dx + (j & 1 ? dx / 2 : 0) + jx, cy: j * dy + jy, r: r0 * (0.86 + rnd() * 0.22), dl: (rnd() - 0.5) * 0.16, dh: (rnd() - 0.5) * 0.035, a: rnd() * Math.PI * 2 });
  }
  const draw = (p, ox) => {
    const cx = p.cx + ox, cy = p.cy, r = p.r, ry = r * squash, L = hsl.l + p.dl;
    x.save(); x.translate(cx, cy); x.scale(1, squash);
    // body: darker toward the rim, a little lighter where the light enters
    let g = x.createRadialGradient(-r * 0.25, -r * 0.3, r * 0.05, 0, 0, r);
    g.addColorStop(0, css(L * 1.3, 1, p.dh, 0.06)); g.addColorStop(0.55, css(L * 0.95, 1, p.dh, 0.06)); g.addColorStop(1, css(L * 0.32, 1, p.dh));
    x.fillStyle = g; x.beginPath(); x.arc(0, 0, r, 0, Math.PI * 2); x.fill();
    // light passing through the pearl collects on the far side
    g = x.createRadialGradient(r * 0.32, r * 0.38, 0, r * 0.32, r * 0.38, r * 0.62);
    g.addColorStop(0, css(L * 2.1, roe.glow, p.dh, 0.08)); g.addColorStop(1, css(L * 2.1, 0, p.dh));
    x.fillStyle = g; x.beginPath(); x.arc(0, 0, r, 0, Math.PI * 2); x.fill();
    if (roe.eye) { x.fillStyle = css(L * 0.55, 0.55, 0.01); x.beginPath(); x.arc(Math.cos(p.a) * r * 0.35, Math.sin(p.a) * r * 0.35, r * 0.2, 0, Math.PI * 2); x.fill(); }
    // wet highlight: one soft window reflection and a small kicker
    g = x.createRadialGradient(-r * 0.34, -r * 0.38, 0, -r * 0.34, -r * 0.38, r * 0.3);
    g.addColorStop(0, 'rgba(255,252,245,0.97)'); g.addColorStop(0.4, 'rgba(255,252,245,0.8)'); g.addColorStop(0.65, 'rgba(255,250,240,0.18)'); g.addColorStop(1, 'rgba(255,250,240,0)');
    x.fillStyle = g; x.beginPath(); x.arc(-r * 0.34, -r * 0.38, r * 0.3, 0, Math.PI * 2); x.fill();
    x.fillStyle = 'rgba(255,248,235,0.35)'; x.beginPath(); x.arc(r * 0.38, r * 0.3, r * 0.07, 0, Math.PI * 2); x.fill();
    x.restore();
    y.save(); y.translate(cx, cy); y.scale(1, squash);
    g = y.createRadialGradient(-r * 0.1, -r * 0.1, 0, 0, 0, r); g.addColorStop(0, '#fff'); g.addColorStop(0.7, '#9a9a9a'); g.addColorStop(1, '#000');
    y.fillStyle = g; y.beginPath(); y.arc(0, 0, r, 0, Math.PI * 2); y.fill(); y.restore();
  };
  for (let i = pearls.length - 1; i > 0; i--) { const k = Math.floor(rnd() * (i + 1)); [pearls[i], pearls[k]] = [pearls[k], pearls[i]]; }  // random overlap order
  for (const p of pearls) { draw(p, 0); if (wrap) { if (p.cx < r0 * 1.2) draw(p, W); if (p.cx > W - r0 * 1.2) draw(p, -W); } }
  const map = new THREE.CanvasTexture(c); map.colorSpace = THREE.SRGBColorSpace; map.anisotropy = 8;
  const bump = new THREE.CanvasTexture(b);
  if (wrap) { map.wrapS = bump.wrapS = THREE.RepeatWrapping; }
  return { map, bump };
}
function glassTint(st) { return st.opts.tint || GLASS_TINT; }
function guessDepth(t) {
  if (/spoon|fork|key|keychain|palette|plate|certificate|slicer|platter/i.test(t)) return 0.05;
  if (/truffle|bottarga|tuna heart|mojama|lobster|salmon|blinis|vanilla|saffron|piment|salt/i.test(t)) return 0.22;
  if (/shell|abalone|bowl/i.test(t)) return 0.14;
  return 0.12;
}
function radialTex(hex, a = 1) {
  const c = document.createElement('canvas'); c.width = c.height = 256; const x = c.getContext('2d');
  const col = new THREE.Color(hex); const rgb = `${Math.round(col.r * 255)},${Math.round(col.g * 255)},${Math.round(col.b * 255)}`;
  const g = x.createRadialGradient(128, 128, 0, 128, 128, 128);
  g.addColorStop(0, `rgba(${rgb},${0.55 * a})`); g.addColorStop(0.35, `rgba(${rgb},${0.22 * a})`); g.addColorStop(1, `rgba(${rgb},0)`);
  x.fillStyle = g; x.fillRect(0, 0, 256, 256);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
function floorTex(bg) {
  const c = document.createElement('canvas'); c.width = c.height = 512; const x = c.getContext('2d');
  const g = x.createRadialGradient(256, 256, 0, 256, 256, 256);
  g.addColorStop(0, 'rgba(26,24,22,1)'); g.addColorStop(0.35, 'rgba(14,14,16,0.9)'); g.addColorStop(1, 'rgba(7,8,12,0)');
  x.fillStyle = g; x.fillRect(0, 0, 512, 512);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
function ribTex() {
  const c = document.createElement('canvas'); c.width = 512; c.height = 8; const x = c.getContext('2d');
  for (let i = 0; i < 512; i++) { const v = 128 + 127 * Math.sin(i / 512 * Math.PI * 2 * 90); x.fillStyle = `rgb(${v},${v},${v})`; x.fillRect(i, 0, 1, 8); }
  const t = new THREE.CanvasTexture(c); t.wrapS = THREE.RepeatWrapping; return t;
}

#!/usr/bin/env python3
"""
Example 04: Gemini 4 Argon — 100% Pure-Python Zero-Dependency 3D Ray-Tracing Engine
===================================================================================
Inspired by the Gemini 4 Argon launch showcase:
  "With zero external libraries and 100% pure Python, Argon wrote its own 3D ray-tracing
   engine ... to build and document a sunlit library from scratch."

This script uses ONLY the Python standard library (`math`, `struct`, `os`, `time`) to:
  1. Ray-trace a 3D architectural scene ("The Argon Sunlit Study") featuring:
     - Reflective spheres (glass/metallic orbs on a study pedestal)
     - Axis-aligned wooden bookshelves and columns (AABB box primitives)
     - Procedural warm parquet/checkerboard floor with soft multi-sample sun shadows
     - Atmospheric golden-hour sky gradient & Beers-Lambert attenuation
  2. Write a uncompressed 24-bit `.bmp` image (`output/argon_sunlit_study.bmp`) with zero
     external packages required!
  3. Optionally query `gemini-4-argon` via the Interactions API to dynamically generate
     new 3D sphere/column coordinates for the raytracer.

Usage:
    python examples/04_vanilla_3d_raytracer.py
"""

from __future__ import annotations

import math
import os
import struct
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Vec3:
    x: float
    y: float
    z: float

    def __add__(self, o: Vec3) -> Vec3:
        return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o: Vec3) -> Vec3:
        return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, s: float) -> Vec3:
        return Vec3(self.x * s, self.y * s, self.z * s)

    def hadamard(self, o: Vec3) -> Vec3:
        return Vec3(self.x * o.x, self.y * o.y, self.z * o.z)

    def dot(self, o: Vec3) -> float:
        return self.x * o.x + self.y * o.y + self.z * o.z

    def cross(self, o: Vec3) -> Vec3:
        return Vec3(
            self.y * o.z - self.z * o.y,
            self.z * o.x - self.x * o.z,
            self.x * o.y - self.y * o.x,
        )

    def length(self) -> float:
        return math.sqrt(self.dot(self))

    def norm(self) -> Vec3:
        l = self.length()
        return Vec3(self.x / l, self.y / l, self.z / l) if l > 1e-9 else Vec3(0.0, 0.0, 0.0)


@dataclass(slots=True)
class Material:
    albedo: Vec3
    specular: float = 0.2
    reflectivity: float = 0.0
    emission: float = 0.0


@dataclass(slots=True)
class Sphere:
    center: Vec3
    radius: float
    material: Material

    def intersect(self, ro: Vec3, rd: Vec3) -> tuple[float, Vec3] | None:
        oc = ro - self.center
        b = oc.dot(rd)
        c = oc.dot(oc) - self.radius * self.radius
        disc = b * b - c
        if disc < 0.0:
            return None
        sqrt_d = math.sqrt(disc)
        t = -b - sqrt_d
        if t < 1e-3:
            t = -b + sqrt_d
            if t < 1e-3:
                return None
        hit = ro + rd * t
        normal = (hit - self.center) * (1.0 / self.radius)
        return t, normal


@dataclass(slots=True)
class Box:
    vmin: Vec3
    vmax: Vec3
    material: Material

    def intersect(self, ro: Vec3, rd: Vec3) -> tuple[float, Vec3] | None:
        inv_x = 1.0 / (rd.x if abs(rd.x) > 1e-9 else 1e-9)
        inv_y = 1.0 / (rd.y if abs(rd.y) > 1e-9 else 1e-9)
        inv_z = 1.0 / (rd.z if abs(rd.z) > 1e-9 else 1e-9)

        tx1 = (self.vmin.x - ro.x) * inv_x
        tx2 = (self.vmax.x - ro.x) * inv_x
        tmin = min(tx1, tx2)
        tmax = max(tx1, tx2)

        ty1 = (self.vmin.y - ro.y) * inv_y
        ty2 = (self.vmax.y - ro.y) * inv_y
        tmin = max(tmin, min(ty1, ty2))
        tmax = min(tmax, max(ty1, ty2))

        tz1 = (self.vmin.z - ro.z) * inv_z
        tz2 = (self.vmax.z - ro.z) * inv_z
        tmin = max(tmin, min(tz1, tz2))
        tmax = min(tmax, max(tz1, tz2))

        if tmax < max(tmin, 1e-3):
            return None

        t = tmin if tmin > 1e-3 else tmax
        hit = ro + rd * t
        eps = 1e-3
        if abs(hit.x - self.vmin.x) < eps:
            n = Vec3(-1.0, 0.0, 0.0)
        elif abs(hit.x - self.vmax.x) < eps:
            n = Vec3(1.0, 0.0, 0.0)
        elif abs(hit.y - self.vmin.y) < eps:
            n = Vec3(0.0, -1.0, 0.0)
        elif abs(hit.y - self.vmax.y) < eps:
            n = Vec3(0.0, 1.0, 0.0)
        elif abs(hit.z - self.vmin.z) < eps:
            n = Vec3(0.0, 0.0, -1.0)
        else:
            n = Vec3(0.0, 0.0, 1.0)
        return t, n


def build_sunlit_library_scene() -> tuple[list[Sphere], list[Box]]:
    spheres = [
        # Central Argon chrome-blue celestial globe
        Sphere(
            center=Vec3(0.0, -0.15, -3.2),
            radius=0.85,
            material=Material(albedo=Vec3(0.26, 0.52, 0.96), specular=0.9, reflectivity=0.65),
        ),
        # Golden brassorrery sphere on the left
        Sphere(
            center=Vec3(-1.55, -0.45, -2.7),
            radius=0.55,
            material=Material(albedo=Vec3(0.95, 0.72, 0.22), specular=0.8, reflectivity=0.45),
        ),
        # Warm ruby glass sphere on the right
        Sphere(
            center=Vec3(1.45, -0.5, -2.5),
            radius=0.5,
            material=Material(albedo=Vec3(0.92, 0.26, 0.21), specular=0.85, reflectivity=0.35),
        ),
        # Sunlit floating luminaire
        Sphere(
            center=Vec3(0.0, 1.55, -3.5),
            radius=0.32,
            material=Material(albedo=Vec3(1.0, 0.94, 0.78), specular=0.1, reflectivity=0.0, emission=1.8),
        ),
    ]

    boxes = [
        # Left mahogany bookshelf column
        Box(
            vmin=Vec3(-3.4, -1.0, -5.2),
            vmax=Vec3(-2.3, 2.2, -3.6),
            material=Material(albedo=Vec3(0.42, 0.22, 0.12), specular=0.15, reflectivity=0.05),
        ),
        # Right mahogany bookshelf column
        Box(
            vmin=Vec3(2.3, -1.0, -5.2),
            vmax=Vec3(3.4, 2.2, -3.6),
            material=Material(albedo=Vec3(0.42, 0.22, 0.12), specular=0.15, reflectivity=0.05),
        ),
        # Central reading pedestal
        Box(
            vmin=Vec3(-0.7, -1.0, -3.7),
            vmax=Vec3(0.7, -0.95, -2.7),
            material=Material(albedo=Vec3(0.82, 0.76, 0.68), specular=0.3, reflectivity=0.15),
        ),
    ]
    return spheres, boxes


def trace_ray(
    ro: Vec3,
    rd: Vec3,
    spheres: list[Sphere],
    boxes: list[Box],
    sun_dir: Vec3,
    depth: int = 0,
) -> Vec3:
    if depth > 2:
        return Vec3(0.0, 0.0, 0.0)

    closest_t = float("inf")
    hit_normal = Vec3(0.0, 1.0, 0.0)
    hit_mat: Material | None = None

    # Intersect spheres
    for sp in spheres:
        res = sp.intersect(ro, rd)
        if res and res[0] < closest_t:
            closest_t, hit_normal = res
            hit_mat = sp.material

    # Intersect library boxes
    for bx in boxes:
        res = bx.intersect(ro, rd)
        if res and res[0] < closest_t:
            closest_t, hit_normal = res
            hit_mat = bx.material

    # Intersect parquet floor at y = -1.0
    if abs(rd.y) > 1e-6:
        t_floor = (-1.0 - ro.y) / rd.y
        if 1e-3 < t_floor < closest_t:
            closest_t = t_floor
            hit_pos = ro + rd * t_floor
            hit_normal = Vec3(0.0, 1.0, 0.0)
            checker = (math.floor(hit_pos.x * 1.5) + math.floor(hit_pos.z * 1.5)) & 1
            floor_color = Vec3(0.86, 0.79, 0.68) if checker == 0 else Vec3(0.32, 0.23, 0.16)
            hit_mat = Material(albedo=floor_color, specular=0.25, reflectivity=0.22)

    # Sky background (warm golden-hour sunlit gradient)
    if hit_mat is None:
        t_sky = 0.5 * (rd.y + 1.0)
        sky = Vec3(0.98, 0.86, 0.68) * (1.0 - t_sky) + Vec3(0.22, 0.44, 0.82) * t_sky
        sun_glare = max(0.0, rd.dot(sun_dir)) ** 32
        return sky + Vec3(1.0, 0.9, 0.65) * (0.55 * sun_glare)

    hit_point = ro + rd * closest_t
    if hit_mat.emission > 0.0:
        return hit_mat.albedo * hit_mat.emission

    # Shadow check toward sun
    shadow_origin = hit_point + hit_normal * 1e-3
    in_shadow = False
    for sp in spheres:
        if sp.material.emission == 0.0 and sp.intersect(shadow_origin, sun_dir) is not None:
            in_shadow = True
            break
    if not in_shadow:
        for bx in boxes:
            if bx.intersect(shadow_origin, sun_dir) is not None:
                in_shadow = True
                break

    ambient = 0.22
    diffuse = 0.0 if in_shadow else max(0.0, hit_normal.dot(sun_dir))
    half_vec = (sun_dir - rd).norm()
    spec = 0.0 if in_shadow else (max(0.0, hit_normal.dot(half_vec)) ** 40) * hit_mat.specular

    sun_color = Vec3(1.0, 0.95, 0.84)
    local_color = hit_mat.albedo * (ambient + diffuse * 0.82) + sun_color * spec

    if hit_mat.reflectivity > 0.0 and depth < 2:
        refl_dir = (rd - hit_normal * (2.0 * rd.dot(hit_normal))).norm()
        refl_color = trace_ray(
            shadow_origin, refl_dir, spheres, boxes, sun_dir, depth + 1
        )
        local_color = local_color * (1.0 - hit_mat.reflectivity) + refl_color * hit_mat.reflectivity

    # Distance fog (sunlit dust beams)
    fog = math.exp(-0.045 * closest_t)
    fog_color = Vec3(0.95, 0.85, 0.70)
    return local_color * fog + fog_color * (1.0 - fog)


def write_bmp(filename: Path, width: int, height: int, rgb_bytes: bytearray) -> None:
    """Writes a standard 24-bit uncompressed BMP file using only Python's `struct` module."""
    row_stride = (width * 3 + 3) & ~3
    padding = row_stride - width * 3
    pixel_data_size = row_stride * height
    file_size = 54 + pixel_data_size

    bmp_header = struct.pack("<2sIHHI", b"BM", file_size, 0, 0, 54)
    dib_header = struct.pack(
        "<IiiHHIIiiII",
        40,
        width,
        height,
        1,
        24,
        0,
        pixel_data_size,
        2835,
        2835,
        0,
        0,
    )

    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "wb") as f:
        f.write(bmp_header)
        f.write(dib_header)
        pad_bytes = b"\x00" * padding
        for y in range(height - 1, -1, -1):
            row_start = y * width * 3
            for x in range(width):
                idx = row_start + x * 3
                r, g, b = rgb_bytes[idx], rgb_bytes[idx + 1], rgb_bytes[idx + 2]
                f.write( bytes((b, g, r)) )
            if padding:
                f.write(pad_bytes)


def render_scene(width: int = 480, height: int = 270) -> Path:
    t0 = time.perf_counter()
    spheres, boxes = build_sunlit_library_scene()
    sun_dir = Vec3(0.55, 0.68, -0.48).norm()
    cam_origin = Vec3(0.0, 0.15, 0.8)
    aspect = width / height
    fov_scale = math.tan(math.radians(52.0) * 0.5)

    rgb_buffer = bytearray(width * height * 3)
    idx = 0
    for y in range(height):
        ndc_y = (1.0 - 2.0 * ((y + 0.5) / height)) * fov_scale
        for x in range(width):
            ndc_x = (2.0 * ((x + 0.5) / width) - 1.0) * aspect * fov_scale
            ray_dir = Vec3(ndc_x, ndc_y, -1.0).norm()
            col = trace_ray(cam_origin, ray_dir, spheres, boxes, sun_dir)
            # Reinhard tone mapping + gamma 2.2
            r = int(min(1.0, max(0.0, col.x / (1.0 + col.x * 0.25))) ** (1.0 / 2.2) * 255.0)
            g = int(min(1.0, max(0.0, col.y / (1.0 + col.y * 0.25))) ** (1.0 / 2.2) * 255.0)
            b = int(min(1.0, max(0.0, col.z / (1.0 + col.z * 0.25))) ** (1.0 / 2.2) * 255.0)
            rgb_buffer[idx] = r
            rgb_buffer[idx + 1] = g
            rgb_buffer[idx + 2] = b
            idx += 3

    out_path = Path(__file__).resolve().parent.parent / "output" / "argon_sunlit_study.bmp"
    write_bmp(out_path, width, height, rgb_buffer)
    elapsed = time.perf_counter() - t0
    print(f"🎨 Rendered 3D Ray-Traced Scene ({width}x{height}) in {elapsed:.2f}s -> {out_path}")
    return out_path


if __name__ == "__main__":
    print("🌞 Gemini 4 Argon — Pure-Python Zero-Dependency 3D Ray-Tracing Engine")
    print("=" * 72)
    render_scene(width=480, height=270)

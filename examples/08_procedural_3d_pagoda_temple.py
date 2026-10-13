#!/usr/bin/env python3
"""
Example 08: Gemini 4 Argon — Procedural 3D Pagoda Temple Generator (.OBJ Mesh)
==============================================================================
Built 100% from scratch in pure Python (zero external dependencies) to showcase
procedural 3D architectural geometry generation:
  - Generates a multi-tiered 3D Pagoda Temple with curved catenary/parabolic upturned
    eaves, corner columns, stone foundation, and a golden Sorin finial spire.
  - Exports a standard Wavefront `.obj` 3D mesh (`output/argon_pagoda_temple.obj`)
    that can be opened in Blender, Three.js, MeshLab, or macOS/Windows 3D viewers.

Usage:
    python examples/08_procedural_3d_pagoda_temple.py
"""

from __future__ import annotations

import math
from pathlib import Path


class ObjMeshBuilder:
    def __init__(self) -> None:
        self.vertices: list[tuple[float, float, float]] = []
        self.faces: list[tuple[int, int, int, int] | tuple[int, int, int]] = []

    def add_vertex(self, x: float, y: float, z: float) -> int:
        self.vertices.append((x, y, z))
        return len(self.vertices)  # 1-indexed for Wavefront .OBJ

    def add_box(
        self, cx: float, cy: float, cz: float, sx: float, sy: float, sz: float
    ) -> None:
        hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
        v = [
            self.add_vertex(cx - hx, cy - hy, cz - hz),
            self.add_vertex(cx + hx, cy - hy, cz - hz),
            self.add_vertex(cx + hx, cy + hy, cz - hz),
            self.add_vertex(cx - hx, cy + hy, cz - hz),
            self.add_vertex(cx - hx, cy - hy, cz + hz),
            self.add_vertex(cx + hx, cy - hy, cz + hz),
            self.add_vertex(cx + hx, cy + hy, cz + hz),
            self.add_vertex(cx - hx, cy + hy, cz + hz),
        ]
        self.faces.extend(
            [
                (v[0], v[1], v[2], v[3]),
                (v[5], v[4], v[7], v[6]),
                (v[4], v[0], v[3], v[7]),
                (v[1], v[5], v[6], v[2]),
                (v[3], v[2], v[6], v[7]),
                (v[4], v[5], v[1], v[0]),
            ]
        )

    def add_curved_pagoda_roof(
        self, base_y: float, inner_span: float, outer_span: float, roof_height: float, rings: int = 6
    ) -> None:
        """Generates a 4-sided swept pagoda roof with upturned parabolic corner eaves."""
        ring_indices: list[list[int]] = []
        for r in range(rings + 1):
            t = r / rings  # 0 at top ridge, 1 at outer eave tip
            span = inner_span * (1.0 - t) + outer_span * t
            # Parabolic drop with upturned eave flare near t -> 1
            flare = 0.38 * (t ** 3) * roof_height
            y = base_y + roof_height * (1.0 - t) ** 1.35 + flare
            pts = [
                self.add_vertex(-span, y, -span),
                self.add_vertex(span, y, -span),
                self.add_vertex(span, y, span),
                self.add_vertex(-span, y, span),
            ]
            ring_indices.append(pts)

        for r in range(rings):
            upper = ring_indices[r]
            lower = ring_indices[r + 1]
            for side in range(4):
                nxt = (side + 1) % 4
                self.faces.append((upper[side], lower[side], lower[nxt], upper[nxt]))

    def export_obj(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Procedural 3D Pagoda Temple generated from scratch\n")
            f.write("o ArgonPagodaTemple\n")
            for x, y, z in self.vertices:
                f.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
            for face in self.faces:
                f.write("f " + " ".join(str(idx) for idx in face) + "\n")


def build_pagoda_temple() -> Path:
    mesh = ObjMeshBuilder()

    # Stone foundation terrace
    mesh.add_box(0.0, 0.3, 0.0, 7.2, 0.6, 7.2)
    mesh.add_box(0.0, 0.75, 0.0, 6.0, 0.3, 6.0)

    # 5 Pagoda Tiers with progressively tapering spans
    curr_y = 0.9
    for tier in range(5):
        scale = 0.82 ** tier
        core_span = 3.8 * scale
        tier_height = 1.35 * (0.9 ** tier)
        eave_span = 2.95 * scale

        # Timber core room
        mesh.add_box(0.0, curr_y + tier_height * 0.5, 0.0, core_span, tier_height, core_span)

        # 4 Corner Pillars
        pillar_offset = core_span * 0.52
        for px in (-pillar_offset, pillar_offset):
            for pz in (-pillar_offset, pillar_offset):
                mesh.add_box(px, curr_y + tier_height * 0.5, pz, 0.18 * scale, tier_height, 0.18 * scale)

        # Swept Pagoda Roof with upturned eaves
        mesh.add_curved_pagoda_roof(
            base_y=curr_y + tier_height - 0.1,
            inner_span=core_span * 0.42,
            outer_span=eave_span,
            roof_height=0.65 * scale,
        )
        curr_y += tier_height + 0.38 * scale

    # Sorin Golden Spire at apex
    mesh.add_box(0.0, curr_y + 0.9, 0.0, 0.16, 1.8, 0.16)

    out_path = Path(__file__).resolve().parent.parent / "output" / "argon_pagoda_temple.obj"
    mesh.export_obj(out_path)
    print(
        f"🏯 Generated 3D Pagoda Temple Mesh: {len(mesh.vertices)} vertices, "
        f"{len(mesh.faces)} faces -> {out_path}"
    )
    return out_path


if __name__ == "__main__":
    build_pagoda_temple()

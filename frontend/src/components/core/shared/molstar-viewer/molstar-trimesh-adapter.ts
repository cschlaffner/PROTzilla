import { Mesh } from "molstar/lib/mol-geo/geometry/mesh/mesh";
import { MeshBuilder } from "molstar/lib/mol-geo/geometry/mesh/mesh-builder";
import { Vec3 } from "molstar/lib/mol-math/linear-algebra";
import { Shape } from "molstar/lib/mol-model/shape";
import { PluginStateObject } from "molstar/lib/mol-plugin-state/objects";
import { StateTransforms } from "molstar/lib/mol-plugin-state/transforms";
import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { StateTransformer } from "molstar/lib/mol-state";
import { Task } from "molstar/lib/mol-task";
import { Color } from "molstar/lib/mol-util/color";
import { ParamDefinition as PD } from "molstar/lib/mol-util/param-definition";

export interface TrimeshLike {
  vertices: number[][];
  faces: number[][];
}

interface AddPolyhedronOptions {
  color?: number;
  alpha?: number;
  label?: string;
}

const ProtzillaTransforms = StateTransformer.builderFactory("protzilla");

const TrimeshShape = ProtzillaTransforms({
  name: "trimesh-shape",
  display: { name: "Trimesh Shape" },
  from: PluginStateObject.Root,
  to: PluginStateObject.Shape.Provider,
  params: {
    mesh: PD.Value<TrimeshLike>({ vertices: [], faces: [] }, { isHidden: true }),
    color: PD.Color(Color(0xff8800)),
    label: PD.Text("Polyhedron"),
  },
})({
  canAutoUpdate: () => true,
  apply({ params }) {
    return Task.create("Create Trimesh Shape", () => {
      return new PluginStateObject.Shape.Provider(
        {
          label: params.label,
          data: params.mesh,
          params: Mesh.Params,
          geometryUtils: Mesh.Utils,
          getShape: (_ctx, data) => {
            const builder = MeshBuilder.createState(data.vertices.length, data.faces.length);
            builder.currentGroup = 0;

            for (const face of data.faces) {
              if (face.length !== 3) continue;
              const a = data.vertices[face[0]];
              const b = data.vertices[face[1]];
              const c = data.vertices[face[2]];
              if (a === undefined || b === undefined || c === undefined) continue;

              MeshBuilder.addTriangle(
                builder,
                Vec3.create(a[0], a[1], a[2]),
                Vec3.create(b[0], b[1], b[2]),
                Vec3.create(c[0], c[1], c[2]),
              );
            }

            const mesh = MeshBuilder.getMesh(builder);
            return Shape.create(
              params.label,
              data,
              mesh,
              () => params.color,
              () => 1,
              () => params.label,
            );
          },
        },
        { label: params.label },
      );
    });
  },
});

export async function addTrimeshPolyhedron(
  plugin: PluginUIContext,
  mesh: TrimeshLike,
  options: AddPolyhedronOptions = {},
) {
  if (mesh.vertices.length === 0 || mesh.faces.length === 0) return;

  const label = options.label ?? "Polyhedron";
  const color = Color(options.color ?? 0xff8800);
  const alpha = options.alpha ?? 0.35;

  await plugin
    .build()
    .toRoot()
    .apply(TrimeshShape, { mesh, color, label })
    .apply(StateTransforms.Representation.ShapeRepresentation3D, { alpha })
    .commit();
}

import { SectionTitle } from "@protzilla/core";
import { createPluginUI } from "molstar/lib/mol-plugin-ui";
import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { PluginCommands } from 'molstar/lib/mol-plugin/commands';
import { Unit } from 'molstar/lib/mol-model/structure';
import { Vec3 } from "molstar/lib/mol-math/linear-algebra";
import { Color } from "molstar/lib/mol-util/color";
import { StructureElement } from 'molstar/lib/mol-model/structure';
import { OrderedSet } from 'molstar/lib/mol-data/int';
import { renderReact18 } from "molstar/lib/mol-plugin-ui/react18";
import React, { useEffect, useRef, useState } from "react";
import { styled } from "styled-components";
import "./molstar-theme.scss";

const Container = styled.div`
  width: 100%;
  height: 100vh;
  position: relative;
  display: flex;
  flex-direction: column;
`;

const CanvasWrapper = styled.div`
  flex: 1;
  position: relative;
  top: 86px;
`;

interface MolstarViewerProps {
  cifText: string;
  crosslinks?: Crosslink[];
}

interface Crosslink {
  chain: string;
  resid1: number;
  atom1: string;
  resid2: number;
  atom2: string;
  color?: string;
  radius?: number;
}

const MolstarViewer: React.FC<MolstarViewerProps> = ({ cifText, crosslinks = [] }) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  console.log(cifText);

  const ErrorTitle = styled(SectionTitle)`
    color: ${({ theme }) => theme.colors.caution};
    * {
      color: inherit !important;
    }
    margin: 15px  
  `;

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let plugin: PluginUIContext | null = null;

    const init = async () => {
      try {
        setIsLoading(true);
        setError(null);

        plugin = await createPluginUI({
          target: container,
          render: renderReact18,
        });

        if (!cifText) {
          throw new Error("No CIF data provided");
        }

        const data = await plugin.builders.data.rawData({
          data: cifText,
          label: "structure",
        });

        const trajectory = await plugin.builders.structure.parseTrajectory(data, "mmcif");
        await plugin.builders.structure.hierarchy.applyPreset(trajectory, "default");

        console.log("noch da");

        const model = await plugin.builders.structure.createModel(trajectory);
        const structure = await plugin.builders.structure.createStructure(model);

        // --- Direkt die erste Unit und die ersten 2 Elemente nehmen ---
        const unit = structure.data!.units[0];
        if (!unit) throw new Error("No atomic unit found");
        if (unit.elements.length < 2) throw new Error("Not enough atoms in the unit");

        const e1 = unit.elements[0];
        const e2 = unit.elements[1];

        //const posA = Vec3.create(unit.conformation.x(e1), unit.conformation.y(e1), unit.conformation.z(e1));
        //const posB = Vec3.create(unit.conformation.x(e2), unit.conformation.y(e2), unit.conformation.z(e2));

        // Nehmen wir deine Koordinaten:
        const coordsA = [0, 0, 0];
        const coordsB = [10, 5, 2];

        // Erstellen echte Vec3 Objekte
        const posA = Vec3.create(coordsA[0], coordsA[1], coordsA[2]);
        const posB = Vec3.create(coordsB[0], coordsB[1], coordsB[2]);

        console.log("Atom positions:", posA, posB);

        // --- Zylinder als Crosslink ---
        const shapes = [{
          type: 'cylinder' as const,
          positionA: posA,
          positionB: posB,
          radius: 0.2,
          color: Color(0xff0000),
        }];

        await plugin.builders.structure.representation.addRepresentation(structure, {
          type: 'shape-group' as any,
          typeParams: { shapes },
          colorTheme: { name: 'uniform' },
          sizeTheme: { name: 'uniform' },
        });

        /*console.log("Units count:", structure.data!.units.length);
        for (const unit of structure.data!.units) {
            console.log(unit.kind, unit.elements.length);
        }
        console.log("noch da 2");

        // --- Helper: Atomposition abrufen ---

        const getAtomPosition = (structureObj: any, chain: string, resid: number, atomName: string) => {
          const { units } = structureObj.data;

          console.log("noch da helper 1");
          for (const unit of units) {
            if (unit.kind !== 0) continue; // 0 = atomic Unit
            if (!unit.model.atomicHierarchy) continue;

          console.log("noch da helper 2");

            const { elements, model } = unit;
            const atoms = model.atomicHierarchy.atoms;
            if (!atoms) continue;

            let foundPos: Vec3 | null = null;

            OrderedSet.forEach(elements, (e) => {
              const asymId = atoms.label_asym_id?.value(e);
              const seqId  = atoms.label_seq_id?.value(e);
              const atomId = atoms.label_atom_id?.value(e);

              console.log("Ids:", asymId, seqId, atomId); 

              if (!asymId || !seqId || !atomId) return false;
              //evtl. Kommentar, dass das im cif fehlt? 

              console.log("noch da helper 3");

              if (asymId.toUpperCase() === chain.toUpperCase() &&
                  String(seqId) === String(resid) &&
                  atomId.toUpperCase() === atomName.toUpperCase()) {
                const pos = Vec3();
                unit.conformation.position(e, pos);
                foundPos = pos;
                return true; // Stop Iteration
              }
              return false; // continue
            });

            if (foundPos) return foundPos;
          }

          return null;
        };

        console.log("noch da 3");

        // --- Crosslinks als Zylinder erzeugen ---
        const shapes = crosslinks.map(link => {
          const posA = getAtomPosition(structure, link.chain, link.resid1, link.atom1);
          const posB = getAtomPosition(structure, link.chain, link.resid2, link.atom2);
          if (!posA || !posB) return null;

          console.log("noch da 4");

          console.log("posA", posA);
          console.log("posB", posB);

          return {
            type: 'cylinder' as const,                  // Shape Typ
            positionA: Vec3.clone(posA),                 // Startpunkt
            positionB: Vec3.clone(posB),                 // Endpunkt
            radius: link.radius ?? 0.2,                  // Radius
            color: Color(link.color 
              ? parseInt(link.color.replace(/^#/, ''), 16) 
              : 0xff0000)                                // Farbe als Mol* Color
          };
        }).filter(Boolean);

        // --- Shape-Group Representation hinzufügen ---
        if (shapes.length > 0) {
          await plugin.builders.structure.representation.addRepresentation(structure, {
            type: 'shape-group' as any,          // built-in Repr-Typ
            typeParams: { shapes },              // Array von Shape-Objekten
            colorTheme: { name: 'uniform' },
            sizeTheme: { name: 'uniform' }
          });
        }*/

        //await plugin.builders.structure.hierarchy.applyPreset(trajectory, "default");
        /*const model = await plugin.builders.structure.createModel(trajectory);
        const structure = await plugin.builders.structure.createStructure(model);

        const struct = structure.obj!.data; // struct ist jetzt vom Typ Structure
        // ⚡ Minimal Hardcoded Example: 2 Atome aus erster Unit
        const unit = struct.units[0];

        const e1 = unit.elements[0];
        const e2 = unit.elements[200];

        // ⚡ WICHTIG: Vec3 als Output übergeben
        const posA = Vec3();
        const posB = Vec3();

        unit.conformation.position(e1, posA);
        unit.conformation.position(e2, posB);

        // Cylinder zeichnen
        const shapes = [{
          type: 'cylinder',
          positionA: posA,
          positionB: posB,
          radius: 0.5, // größer machen für Sichtbarkeit
          color: Color(0xffffff)
        }];

        await plugin.builders.structure.representation.addRepresentation(structure, {
          type: 'shape-group' as any,
          typeParams: { shapes },
          colorTheme: { name: 'uniform' },
          sizeTheme: { name: 'uniform' }
        });*/

        /*const structure = await plugin.builders.structure.createStructure(model);

        // 5️⃣ Helper: Atom-Position abrufen
        const getAtomPosition = (structureObj: any, chain: string, resid: number, atomName: string) => {
          const { units } = structureObj.data;
          for (const unit of units) {
            if (unit.kind !== "atomic") continue;
            const { elements, model } = unit;
            const atoms = model.atomicHierarchy.atoms;
            for (const e of elements) {
              if (
                atoms.label_asym_id.value(e) === chain &&
                atoms.label_seq_id.value(e) === resid &&
                atoms.label_atom_id.value(e) === atomName
              ) {
                return structureObj.data.getAtomLocation(e);
              }
            }
          }
          return null;
        };

        // 6️⃣ Crosslinks zeichnen
        const shapes = crosslinks.map(link => {
          const posA = getAtomPosition(structure, link.chain, link.resid1, link.atom1);
          const posB = getAtomPosition(structure, link.chain, link.resid2, link.atom2);
          if (!posA || !posB) return null;

          return {
            type: 'cylinder' as const,
            positionA: Vec3.clone(posA),
            positionB: Vec3.clone(posB),
            radius: link.radius ?? 0.2,
            color: Color(link.color ? parseInt(link.color.replace(/^#/, ''), 16) : 0xff0000)
          };
        }).filter(Boolean);

        // Repräsentation hinzufügen
        if (shapes.length > 0) {
          await plugin.builders.structure.representation.addRepresentation(structure, {
            type: 'shape-group' as any,          // built-in Repr-Typ
            typeParams: { shapes },       // Array von Shape-Objekten
            colorTheme: { name: 'uniform' },
            sizeTheme: { name: 'uniform' }
          });
        }*/
        


        console.log("noch da 5");


        setIsLoading(false);
      } catch (err: unknown) {
        console.error("MolstarViewer Error:", err);
        const message = err instanceof Error ? err.message : String(err);
        setError(message);
        setIsLoading(false);
      }
    };

    void init();

    return () => {
      if (plugin !== null) {
        try {
          plugin.dispose();
        } catch (disposeErr) {
          console.warn("Error disposing Molstar plugin:", disposeErr);
        }
      }
    };
  }, [cifText, crosslinks]);

  return (
    <Container>
      {isLoading && <SectionTitle baseComponent="h4" description="Structure is loading..." />}
      {error && <ErrorTitle baseComponent="h4" description={error} />}
      <CanvasWrapper ref={containerRef} />
    </Container>
  );
};

export default MolstarViewer;

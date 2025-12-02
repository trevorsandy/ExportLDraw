import bpy
import json
import glob
import os
import sys


def process_file(file):
    print(file)
    if not os.path.isfile(file): return None
    if not os.path.basename(file).startswith('3626'): return None
    with open(file, "r", encoding='utf-8') as f:
        contents = f.read()
        if contents.startswith('0 Minifig Head ') or contents.startswith("0 Minifig Head\n"):
            return file
            return contents
    return None


def get_parts():
    files = glob.glob(r"d:\ldraw\parts\*")

    parts = []
    for file in files:
        p = process_file(file)
        if p is not None:
            parts.append(p)

    filepath = bpy.data.filepath
    dirname = os.path.dirname(filepath)
    with open(f"d:/desktop/parts.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(parts, indent=2))

    print(f"\nTotal parts processed: {len(parts)}")

    return parts


def process_part(part):
    out_root = fr"d:/desktop/heads"
    os.makedirs(out_root, exist_ok=True)

    try:
        bpy.ops.object.select_all(action='DESELECT')

        for obj in list(bpy.data.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        print(len(bpy.data.objects))

        for mesh in list(bpy.data.meshes):
            bpy.data.meshes.remove(mesh)
        print(len(bpy.data.meshes))

        bpy.ops.ldraw_exporter.import_operator(
            filepath=part,
            ldraw_path=r"d:\ldraw",
            make_gaps=False,
            import_scale=1.0,
        )

        bpy.context.view_layer.objects.active = bpy.context.scene.objects[0]
        for obj in bpy.context.scene.objects:
            obj.ldraw_props.export_polygons = True
            obj.ldraw_props.export_precision = 4
            if not obj.select_get():
                obj.select_set(True)

        bpy.ops.ldraw_exporter.export_operator(
            filepath=fr"{out_root}/{os.path.basename(part)}",
            ldraw_path=r"d:/ldraw",
        )
    except Exception as e:
        print('=' * 50)
        print(e)
        print('=' * 50)


def do(parts):
    for part in parts:
        process_part(part)


if __name__ == "__main__":
    parts = get_parts()
    print(len(parts))

    # p = parts[0:50]
    # p = parts[50:100]
    # p = parts[100:150]
    # p = parts[150:200]
    # p = parts[200:250]
    # p = parts[250:300]
    # p = parts[300:350]
    # p = parts[350:400]

    do(parts)

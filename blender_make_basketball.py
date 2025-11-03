import bpy
import os
from math import pi


def clear_scene():
	# Delete all existing objects
	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.object.delete(use_global=False)
	# Remove orphan data
	for block in bpy.data.meshes:
		if block.users == 0:
			bpy.data.meshes.remove(block)
	for block in bpy.data.materials:
		if block.users == 0:
			bpy.data.materials.remove(block)


def ensure_output_dir():
	base_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
	out_dir = os.path.join(base_dir, "output")
	os.makedirs(out_dir, exist_ok=True)
	return out_dir


def add_camera_and_lights():
	# Camera
	bpy.ops.object.camera_add(location=(0.0, -3.2, 1.4), rotation=(pi / 3.0, 0.0, 0.0))
	camera = bpy.context.object
	bpy.context.scene.camera = camera

	# Key light (Area)
	bpy.ops.object.light_add(type='AREA', location=(2.0, -2.0, 3.0))
	area = bpy.context.object
	area.data.energy = 2000.0
	area.data.size = 2.0

	# Sun light
	bpy.ops.object.light_add(type='SUN', location=(-3.0, 3.0, 5.0))
	sun = bpy.context.object
	sun.data.energy = 3.0

	# Fill light (Point)
	bpy.ops.object.light_add(type='POINT', location=(0.0, 2.0, 2.2))
	fill = bpy.context.object
	fill.data.energy = 1200.0

	return camera, (area, sun, fill)


def make_basketball_material(name: str = "Basketball") -> bpy.types.Material:
	mat = bpy.data.materials.new(name)
	mat.use_nodes = True
	nodes = mat.node_tree.nodes
	links = mat.node_tree.links

	# Clear default nodes
	for n in list(nodes):
		nodes.remove(n)

	# Nodes
	output = nodes.new("ShaderNodeOutputMaterial")
	output.location = (900, 0)
	bsdf = nodes.new("ShaderNodeBsdfPrincipled")
	bsdf.location = (650, 0)
	links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

	# Base leather color
	rgb_color = nodes.new("ShaderNodeRGB")
	rgb_color.location = (100, 250)
	# Orange leather color
	rgb_color.outputs[0].default_value = (0.84, 0.37, 0.12, 1.0)
	links.new(rgb_color.outputs[0], bsdf.inputs["Base Color"])

	# Leather roughness variation
	noise_rough = nodes.new("ShaderNodeTexNoise")
	noise_rough.location = (100, -120)
	noise_rough.inputs["Scale"].default_value = 130.0
	noise_rough.inputs["Detail"].default_value = 5.0
	noise_rough.inputs["Roughness"].default_value = 0.35

	map_range = nodes.new("ShaderNodeMapRange")
	map_range.location = (300, -120)
	map_range.inputs[1].default_value = 0.2
	map_range.inputs[2].default_value = 0.8
	map_range.inputs[3].default_value = 0.55
	map_range.inputs[4].default_value = 0.9
	links.new(noise_rough.outputs["Fac"], map_range.inputs["Value"])
	links.new(map_range.outputs["Result"], bsdf.inputs["Roughness"])

	# Leather micro normal via noise + bump
	noise_norm = nodes.new("ShaderNodeTexNoise")
	noise_norm.location = (100, -360)
	noise_norm.inputs["Scale"].default_value = 200.0
	noise_norm.inputs["Detail"].default_value = 2.0

	bump_main = nodes.new("ShaderNodeBump")
	bump_main.location = (450, -360)
	bump_main.inputs["Strength"].default_value = 0.12
	links.new(noise_norm.outputs["Fac"], bump_main.inputs["Height"])
	links.new(bump_main.outputs["Normal"], bsdf.inputs["Normal"])

	# Seam mask using Object coordinates bands
	texcoord = nodes.new("ShaderNodeTexCoord")
	texcoord.location = (-700, 80)
	separate = nodes.new("ShaderNodeSeparateXYZ")
	separate.location = (-500, 80)
	links.new(texcoord.outputs["Object"], separate.inputs["Vector"])

	# Helper function: |axis| ~ 0 band using smoothstep via Map Range
	def band_on_axis(axis_output_name: str, loc_x: int, loc_y: int, width: float):
		abs_node = nodes.new("ShaderNodeMath")
		abs_node.location = (loc_x, loc_y)
		abs_node.operation = 'ABSOLUTE'
		links.new(getattr(separate.outputs, axis_output_name), abs_node.inputs[0])

		mapr = nodes.new("ShaderNodeMapRange")
		mapr.location = (loc_x + 180, loc_y)
		mapr.inputs[1].default_value = 0.0  # From Min
		mapr.inputs[2].default_value = width  # From Max (band half width)
		mapr.inputs[3].default_value = 1.0  # To Min
		mapr.inputs[4].default_value = 0.0  # To Max (invert band)
		mapr.clamp = True
		links.new(abs_node.outputs[0], mapr.inputs[0])
		return mapr

	band_x = band_on_axis("X", -300, 220, 0.04)  # Meridian seam
	band_z = band_on_axis("Z", -300, 20, 0.04)   # Equator seam

	# Two rotated meridian bands to mimic curved seams
	mapping1 = nodes.new("ShaderNodeMapping")
	mapping1.location = (-700, -230)
	mapping1.inputs["Rotation"].default_value[2] = 0.45
	mapping2 = nodes.new("ShaderNodeMapping")
	mapping2.location = (-700, -430)
	mapping2.inputs["Rotation"].default_value[2] = -0.45

	sep1 = nodes.new("ShaderNodeSeparateXYZ")
	sep1.location = (-500, -230)
	links.new(texcoord.outputs["Object"], mapping1.inputs["Vector"])
	links.new(mapping1.outputs["Vector"], sep1.inputs["Vector"])

	sep2 = nodes.new("ShaderNodeSeparateXYZ")
	sep2.location = (-500, -430)
	links.new(texcoord.outputs["Object"], mapping2.inputs["Vector"])
	links.new(mapping2.outputs["Vector"], sep2.inputs["Vector"])

	def band_on_x_from_sep(sep_node, loc_x: int, loc_y: int, width: float):
		abs_node = nodes.new("ShaderNodeMath")
		abs_node.location = (loc_x, loc_y)
		abs_node.operation = 'ABSOLUTE'
		links.new(sep_node.outputs["X"], abs_node.inputs[0])

		mapr = nodes.new("ShaderNodeMapRange")
		mapr.location = (loc_x + 180, loc_y)
		mapr.inputs[1].default_value = 0.0
		mapr.inputs[2].default_value = width
		mapr.inputs[3].default_value = 1.0
		mapr.inputs[4].default_value = 0.0
		mapr.clamp = True
		links.new(abs_node.outputs[0], mapr.inputs[0])
		return mapr

	band_r1 = band_on_x_from_sep(sep1, -300, -230, 0.04)
	band_r2 = band_on_x_from_sep(sep2, -300, -430, 0.04)

	# Combine all seam bands (multiply = logical AND of inverted bands -> we want union of seams, so use min via 'Multiply' after inverting correctly)
	# Easier: Use maximum of bands (where 1 = seam) then clamp
	max1 = nodes.new("ShaderNodeMath"); max1.operation = 'MAXIMUM'; max1.location = (20, 120)
	links.new(band_x.outputs[0], max1.inputs[0])
	links.new(band_z.outputs[0], max1.inputs[1])

	max2 = nodes.new("ShaderNodeMath"); max2.operation = 'MAXIMUM'; max2.location = (200, 120)
	links.new(max1.outputs[0], max2.inputs[0])
	links.new(band_r1.outputs[0], max2.inputs[1])

	max3 = nodes.new("ShaderNodeMath"); max3.operation = 'MAXIMUM'; max3.location = (380, 120)
	links.new(max2.outputs[0], max3.inputs[0])
	links.new(band_r2.outputs[0], max3.inputs[1])

	# Darken color on seams
	mix_color = nodes.new("ShaderNodeMixRGB")
	mix_color.location = (430, 260)
	mix_color.blend_type = 'MULTIPLY'
	mix_color.inputs[1].default_value = (0.12, 0.12, 0.12, 1.0)  # seam dark color
	links.new(rgb_color.outputs[0], mix_color.inputs[2])
	links.new(max3.outputs[0], mix_color.inputs[0])
	links.new(mix_color.outputs[0], bsdf.inputs["Base Color"])

	# Increase roughness on seams slightly
	mix_rough = nodes.new("ShaderNodeMixRGB")
	mix_rough.location = (430, -120)
	mix_rough.blend_type = 'MIX'
	mix_rough.inputs[1].default_value = (0.9, 0.9, 0.9, 1.0)
	links.new(max3.outputs[0], mix_rough.inputs[0])
	links.new(map_range.outputs["Result"], mix_rough.inputs[2])

	# Convert mix_rough (RGB) to single channel for roughness
	separate_rough = nodes.new("ShaderNodeSeparateRGB")
	separate_rough.location = (600, -120)
	links.new(mix_rough.outputs[0], separate_rough.inputs[0])
	links.new(separate_rough.outputs["R"], bsdf.inputs["Roughness"])

	# Grooves: add an extra bump inverted on seams
	bump_groove = nodes.new("ShaderNodeBump")
	bump_groove.location = (450, -560)
	bump_groove.inputs["Strength"].default_value = 0.25
	bump_groove.inputs["Distance"].default_value = 0.02
	links.new(max3.outputs[0], bump_groove.inputs["Height"])

	# Combine groove bump with micro bump
	normal_mix = nodes.new("ShaderNodeMixRGB")
	normal_mix.location = (620, -420)
	normal_mix.blend_type = 'MIX'
	normal_mix.inputs[0].default_value = 0.5
	links.new(bump_main.outputs["Normal"], normal_mix.inputs[1])
	links.new(bump_groove.outputs["Normal"], normal_mix.inputs[2])
	# Use Normal Map combination via Normal input through another Bump node (safer)
	bump_final = nodes.new("ShaderNodeBump")
	bump_final.location = (800, -420)
	bump_final.inputs["Strength"].default_value = 1.0
	links.new(bump_groove.outputs["Normal"], bump_final.inputs["Normal"])  # chain groove as normal input
	links.new(noise_norm.outputs["Fac"], bump_final.inputs["Height"])      # and use noise as height
	links.new(bump_final.outputs["Normal"], bsdf.inputs["Normal"])         # final normal

	return mat


def build_basketball(radius: float = 1.0) -> bpy.types.Object:
	# Sphere
	bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=radius)
	ball = bpy.context.object
	bpy.ops.object.shade_smooth()

	# Subdivision (optional for smoother silhouette)
	bpy.ops.object.modifier_add(type='SUBSURF')
	ball.modifiers["Subdivision"].levels = 2
	ball.modifiers["Subdivision"].render_levels = 2

	# Material
	mat = make_basketball_material()
	if ball.data.materials:
		ball.data.materials[0] = mat
	else:
		ball.data.materials.append(mat)

	return ball


def add_ground():
	bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0.0, 0.0, -1.0))
	ground = bpy.context.object
	bpy.ops.object.shade_smooth()
	# Simple matte ground material
	mat = bpy.data.materials.new("Ground")
	mat.use_nodes = True
	nodes = mat.node_tree.nodes
	links = mat.node_tree.links
	for n in list(nodes):
		nodes.remove(n)
	out = nodes.new("ShaderNodeOutputMaterial"); out.location = (300, 0)
	bsdf = nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (100, 0)
	bsdf.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1.0)
	bsdf.inputs["Roughness"].default_value = 0.9
	links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
	ground.data.materials.append(mat)
	return ground


def main():
	clear_scene()
	ensure_output_dir()
	add_camera_and_lights()
	ball = build_basketball(radius=1.0)
	add_ground()

	# Position ball slightly above ground
	ball.location.z = 0.0

	# Set cycles or eevee
	scene = bpy.context.scene
	scene.render.engine = 'BLENDER_EEVEE'
	scene.eevee.taa_render_samples = 64
	scene.eevee.taa_samples = 32

	# World background
	world = bpy.data.worlds.get("World")
	if world:
		world.use_nodes = True
		nodes = world.node_tree.nodes
		bg = nodes.get("Background")
		if bg:
			bg.inputs[0].default_value = (0.04, 0.04, 0.05, 1.0)
			bg.inputs[1].default_value = 1.0

	# Save and export
	out_dir = ensure_output_dir()
	blend_path = os.path.join(out_dir, "basketball.blend")
	obj_path = os.path.join(out_dir, "basketball.obj")
	glb_path = os.path.join(out_dir, "basketball.glb")

	# Save blend
	bpy.ops.wm.save_as_mainfile(filepath=blend_path)

	# Export OBJ
	bpy.ops.export_scene.obj(filepath=obj_path, use_selection=False, use_materials=True)

	# Export glTF binary
	bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB', use_selection=False)


if __name__ == "__main__":
	main()





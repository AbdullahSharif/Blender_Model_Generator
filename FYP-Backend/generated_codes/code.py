import bpy
import random
import numpy as np
import random

def delete_all_objects():
	for object in bpy.data.objects:
		bpy.data.objects.remove(object)

def decrease_size(obj):
	obj.delta_scale = [ obj.delta_scale[0] - 1.4 / 1.5, obj.delta_scale[1] - 1.4 / 1.5, obj.delta_scale[2] - 1.4 / 1.5 ]

def add_shrinkwrap(data, target):
	con = data.constraints.new('SHRINKWRAP')
	con.target = target
	con.shrinkwrap_type = 'PROJECT'
	con.project_axis = 'NEG_Z'
def place_shrubs(a, b, size, scale):
	bushes = []
	beta_random = (np.random.default_rng().beta(a, b, size=(size, 2)) * scale)
	with bpy.data.libraries.load(r'C:\Users\hp\Documents\FYP\FYP-playground\canberry_bush.blend') as (data_from, data_to):
		data_to.objects.append(data_from.objects[0])
	bushes.append(data_to.objects[0])
	for i in beta_random:
		bush_instance = bushes[random.randint(0, len(bushes) - 1)].copy()
		bush_instance.location = [i[0], i[1], 3]
		bpy.context.collection.objects.link(bush_instance)
		add_shrinkwrap(bush_instance, bpy.context.object)
def place_cactus(a, b, size, scale):
	cactuses = []
	beta_random = (np.random.default_rng().beta(a, b, size=(size, 2)) * scale)
	with bpy.data.libraries.load(r'C:\Users\hp\Documents\FYP\FYP-playground\cactus_3.blend') as (data_from, data_to):
		data_to.objects.append(data_from.objects[0])
	cactuses.append(data_to.objects[0])
	with bpy.data.libraries.load(r'C:\Users\hp\Documents\FYP\FYP-playground\cactus_2.blend') as (data_from, data_to):
		data_to.objects.append(data_from.objects[0])
	cactuses.append(data_to.objects[0])
	with bpy.data.libraries.load(r'C:\Users\hp\Documents\FYP\FYP-playground\cactus_1.blend') as (data_from, data_to):
		data_to.objects.append(data_from.objects[0])
	cactuses.append(data_to.objects[0])
	for i in beta_random:
		cactus_instance = cactuses[random.randint(0, len(cactuses) - 1)].copy()
		decrease_size(cactus_instance)
		# Set location and rotation
		cactus_instance.location = [i[0], i[1], 3]
		bpy.context.collection.objects.link(cactus_instance)
		add_shrinkwrap(cactus_instance, bpy.context.object)
def create_desert(size, scale, viewport_resolution, spatial_size, choppiness, repeat_x, repeat_y, color, num_of_cactus, num_of_shrubs):
	bpy.ops.mesh.primitive_plane_add(size=size, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=scale)
	bpy.ops.object.modifier_add(type='OCEAN')
	bpy.context.object.modifiers['Ocean'].viewport_resolution = viewport_resolution
	bpy.context.object.modifiers['Ocean'].size = 0.5
	bpy.context.object.modifiers['Ocean'].spatial_size = spatial_size
	bpy.context.object.modifiers['Ocean'].depth = 500
	bpy.context.object.modifiers['Ocean'].random_seed = random.randint(1, 100)
	bpy.context.object.modifiers['Ocean'].wave_scale = 1
	bpy.context.object.modifiers['Ocean'].wave_scale_min = 0.61
	bpy.context.object.modifiers['Ocean'].choppiness = choppiness
	bpy.context.object.modifiers['Ocean'].repeat_x = repeat_x
	bpy.context.object.modifiers['Ocean'].repeat_y = repeat_y
	mat = bpy.data.materials.new(name='Material')
	mat.diffuse_color = color
	mat.specular_intensity = 0
	mat.roughness = 1
	bpy.context.object.data.materials.append(mat)
	place_cactus(1, 1, num_of_cactus, 80)
	place_shrubs(1, 1, num_of_shrubs, 80)

bpy.ops.wm.save_as_mainfile(filepath='./generated_scene.blend')

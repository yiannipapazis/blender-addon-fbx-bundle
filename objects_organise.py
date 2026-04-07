import bpy, bmesh
import os
import mathutils
from mathutils import Vector
import math
import random
import re
import json
import imp

from . import platforms
imp.reload(platforms)


def is_object_valid(obj):
	# Objects to include in a bundle as 'export-able'
	if obj.hide_viewport:
		return False

	# Ignore objects that are not in any collection (e.g. MESHMachine stashed objects)
	if len(obj.users_collection) == 0:
		return False

	# Ensure the object is in the current view layer to avoid selection errors
	if obj.name not in bpy.context.view_layer.objects:
		return False
		
	return obj.type == 'MESH' or obj.type == 'FONT' or obj.type == 'CURVE' or obj.type == 'EMPTY' or obj.type == 'ARMATURE'


def get_objects(fast=True):
	objects = []
	for obj in bpy.context.selected_objects:
		objects.append(obj)

	# Include all children?
	if len(objects) > 0:
		
		limit = 100  # max depth

		def collect_recursive(obj, depth):
			if obj not in objects:
				objects.append(obj)
			
			if depth < limit: #Don't exceed limit on traversal depth
				for child in obj.children:
					collect_recursive(child, depth+1)
		
		if bpy.context.scene.FBXBundleSettings.mode_bundle == 'PARENT':
			# Collect parent and children objects
			roots = []

			# Collect roots from input selection
			for obj in objects:
				root = obj
				for i in range(limit):
					if root.parent:
						root = root.parent
					else:
						break
				if root not in roots:
					roots.append(root)

			# Traverse loops and its nested elements
			for root in roots:
				collect_recursive(root, 0)

		elif bpy.context.scene.FBXBundleSettings.mode_bundle == 'COLLECTION':
			# Collect group objects
			if not fast:
				# Collect groups from input selection
				groups = []
				for obj in objects:
					groups += [g for g in obj.users_collection if g not in groups]

				# Collect objects of groups
				# TODO needs to check view layer collection
				for grp in groups:
					objects += [o for o in grp.objects if o not in objects]

		elif bpy.context.scene.FBXBundleSettings.mode_bundle == 'SCENE':
			# Include all objects of the scene
			for obj in bpy.context.scene.objects:
				if obj not in objects:
					objects.append(obj)
		
		elif bpy.context.scene.FBXBundleSettings.mode_bundle == 'COLLECTION_INSTANCE':
			# Collect children obejcts
			for obj in objects:
				collect_recursive(obj, 0)


	filtered = []
	for obj in objects:
		if is_object_valid(obj):
			filtered.append(obj)

	return sort_objects_name(filtered)



def sort_objects_name(objects):
	names = {}
	for obj in objects:
		names[obj.name] = obj

	# now sort
	sorted_objects = []
	for key in sorted(names.keys()):
		sorted_objects.append(names[key])

	return sorted_objects



def get_objects_animation(objects):
	# Detect if animation
	use_animation = False
	for obj in objects:
		if get_object_animation(obj):
			use_animation = True
			break
	return use_animation



def get_object_animation(obj):
	if obj:
		#Check for animation data on object
		if obj.animation_data:
			return True

		# Check for armature modifiers
		for mod in obj.modifiers:
			if mod.type == 'ARMATURE':
				return True

	# No animation found
	return False



def recent_store(bundles):
	dic = {}
	dic['selection'] = []
	dic['bundles'] = []
	for name,objects in bundles.items():
		dic['bundles'].append(name)
		for obj in objects:
			dic['selection'].append(obj.name)

	bpy.context.scene.FBXBundleSettings.recent = json.dumps(dic).encode().decode()



def recent_get_label():
	recent = bpy.context.scene.FBXBundleSettings.recent
	mode = bpy.context.scene.FBXBundleSettings.target_platform

	if mode in platforms.platforms:
		if len(recent) > 0:
			dic = json.loads(recent.encode().decode())
			ext = platforms.platforms[mode].extension
			if 'bundles' in dic and len(dic['bundles']) > 0:
				# names = [name+"."+ext for name in dic['bundles']]
				names = [name for name in dic['bundles']]

				return "Re-Export: ".format(len(dic['bundles']))+", ".join(names)

	return "Re-Export"



def recent_load_objects():
	recent = bpy.context.scene.FBXBundleSettings.recent
	if len(recent) > 0:
		dic = json.loads(recent.encode().decode())
		if 'selection' in dic and len(dic['selection']) > 0:
			objects = []
			for name in dic['selection']:
				if name in bpy.data.objects:
					objects.append(bpy.data.objects[name])
			return objects
	return []
	


0
def get_bundles(fast=False):
	objects = get_objects(fast=fast)
    
	bundles = {}
	for obj in objects:
		key = get_key(obj)
		if key not in bundles.keys():
			bundles[key] = [obj]
		else:
			bundles[key].append(obj)
	
	if len(bundles) == 1 and 'UNDEFINED' in bundles:
		bundles.clear() 

	return bundles



def get_pivot(objects):
	mode_bundle = bpy.context.scene.FBXBundleSettings.mode_bundle

	if not objects:
		return Vector((0, 0, 0))

	obj = objects[0]
	root = obj
	if mode_bundle == 'PARENT' or mode_bundle == 'COLLECTION_INSTANCE':
		# climb up to the root parent
		for i in range(100): # safety break
			if root.parent:
				root = root.parent
			else:
				break
	
	if mode_bundle == 'PARENT':
		return root.location

	if mode_bundle == 'COLLECTION_INSTANCE':
		if root.instance_collection:
			return root.location

	return Vector((0,0,0))



def get_key(obj):
	mode_bundle = bpy.context.scene.FBXBundleSettings.mode_bundle

	if mode_bundle == 'PARENT':
		# Use group name
		if obj.parent:
			limit = 100
			obj_parent = obj.parent
			for i in range(limit):
				if obj_parent.parent:
					obj_parent = obj_parent.parent
				else:
					break
			return obj_parent.name
		else:
			return obj.name

	elif mode_bundle == 'COLLECTION':
		# TODO Make this work
		# Use group name
		if len(obj.users_collection) >= 1:
			return obj.users_collection[0].name
	
	elif mode_bundle == 'COLLECTION_INSTANCE':
		# Use collection instance name
		if True:
			if obj.parent:
				limit = 100
				obj_parent = obj.parent
				for i in range(limit):
					if obj_parent.parent:
						obj_parent = obj_parent.parent
					else:
						break
				if obj_parent.instance_collection:
					return obj_parent.instance_collection.name
			elif obj.instance_collection:
				return obj.instance_collection.name
		else:
			if obj.instance_collection:
				return obj.instance_collection.name
		

	elif mode_bundle == 'SCENE':
		# Use scene name
		return bpy.context.scene.name

	return "UNDEFINED"



class ObjectBounds:
	obj = None
	min = Vector((0,0,0))
	max = Vector((0,0,0))
	size = Vector((0,0,0))
	center = Vector((0,0,0))

	def __init__(self, obj):
		self.obj = obj
		corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

		self.min = Vector((corners[0].x, corners[0].y, corners[0].z))
		self.max = Vector((corners[0].x, corners[0].y, corners[0].z))
		for corner in corners:
			self.min.x = min(self.min.x, corner.x)
			self.min.y = min(self.min.y, corner.y)
			self.min.z = min(self.min.z, corner.z)
			self.max.x = max(self.max.x, corner.x)
			self.max.y = max(self.max.y, corner.y)
			self.max.z = max(self.max.z, corner.z)

		self.size = self.max - self.min
		self.center = self.min+(self.max-self.min)/2


	def combine(self, other):
		self.min.x = min(self.min.x, other.min.x)
		self.min.y = min(self.min.y, other.min.y)
		self.min.z = min(self.min.z, other.min.z)
		self.max.x = max(self.max.x, other.max.x)
		self.max.y = max(self.max.y, other.max.y)
		self.max.z = max(self.max.z, other.max.z)

		self.size = self.max - self.min
		self.center = self.min+(self.max-self.min)/2

	def is_colliding(self, other):
		def is_collide_1D(A_min, A_max, B_min, B_max):
			# One line is inside the other
			length_A = A_max-A_min
			length_B = B_max-B_min
			center_A = A_min + length_A/2
			center_B = B_min + length_B/2
			return abs(center_A - center_B) <= (length_A+length_B)/2

		collide_x = is_collide_1D(self.min.x, self.max.x, other.min.x, other.max.x)
		collide_y = is_collide_1D(self.min.y, self.max.y, other.min.y, other.max.y)
		collide_z = is_collide_1D(self.min.z, self.max.z, other.min.z, other.max.z)
		return collide_x and collide_y and collide_z


def consolidate_objects(objects, apply_normals=True, merge_uvs=True, convert_mesh=True):
	for obj in objects:
		if obj.type in ('MESH','EMPTY'):
			# TODO multi thread this. Only need to run duplicates make real once
			bpy.ops.object.select_all(action='DESELECT')
			# Select and make active
			bpy.context.view_layer.objects.active = obj
			obj.select_set(state=True)

			# Copy object data
			if obj.data:
				copy = obj.data.copy()
				obj.data = copy
			
			bpy.ops.object.duplicates_make_real()
			
        	# Test if operation did anything
			exten = bpy.context.selected_objects
			if len(exten) < 2:
				continue
			
			# Recursively add new objects
			exten = [o for o in exten if o != obj]
			objects.extend(exten)
			objects.remove(obj)

			bpy.ops.object.select_all(action='DESELECT')
			bpy.context.view_layer.objects.active = obj
			obj.select_set(state=True)
			bpy.ops.object.delete()
	
	# After we've insured that there's no more instanced objects - apply modifiers
	for obj in objects:
		bpy.ops.object.select_all(action="DESELECT")
		obj.select_set(state=True)
		bpy.context.view_layer.objects.active = obj
		obj.hide_viewport = False

		# Apply modifiers
		if obj.type == 'MESH':
			bpy.ops.object.convert(target='MESH')
	
	# Reselect objects list
	bpy.ops.object.select_all(action='DESELECT')
	[o.select_set(state=True) for o in objects]
	
	# Find a mesh object so we can run convert operator
	make_mesh_type_active(objects)

	bpy.ops.object.make_single_user(
			type='SELECTED_OBJECTS', object=False, obdata=True)
	
	# TODO figure out a better way to preserve auto smooth
	if apply_normals:
		for obj in objects:				
			if obj.type == 'MESH':
				data = obj.data
				if data.use_auto_smooth:
					mod = obj.modifiers.new("Split Normals","EDGE_SPLIT")
					mod.split_angle = data.auto_smooth_angle
	
	if convert_mesh:
		bpy.ops.object.convert(target='MESH', keep_original=False)
		bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

	if merge_uvs:
		# Consolidate UVs
		uv_map_name = "UVMap"
		for obj in objects:
			#bpy.context.view_layer.objects.active = obj
			if obj.type == 'MESH':
				for layer in obj.data.uv_layers:
					if layer.active_render:
						active = layer
						active.name = uv_map_name
					else:
						if not layer.name == "Lightmap":
							obj.data.uv_layers.remove(layer)

	# Consolidate UVs
	uv_map_name = "UVMap"
	for obj in objects:
		bpy.context.view_layer.objects.active = obj
		if obj.type == 'MESH':
			for layer in obj.data.uv_layers:
				if layer.active_render:
					active = layer
					active.name = uv_map_name
				else:
					if not layer.name == "Lightmap":
						obj.data.uv_layers.remove(layer)

	#Find Mesh Type Again
	make_mesh_type_active(objects)

	return objects

def make_mesh_type_active(objects):
		for obj in objects:
			if obj.type == 'MESH':
				bpy.context.view_layer.objects.active = obj
				break
			continue

import bpy, bmesh
import imp
import string
import random
from mathutils import Vector


from . import objects_organise

from . import modifier
imp.reload(modifier) 

class Settings(modifier.Settings):
    	active = bpy.props.BoolProperty (
		name="Active",
		default=False
	)

class Modifier(modifier.Modifier):
	label = "Lightmap UV"
	id = 'lightmap_uv'
	url = ""
	
	def __init__(self):
		super().__init__()	
			
	def process_objects(self, name, objects):
		bpy.ops.object.gpro_converttogeo(maxDept=0)
		selected_objects = bpy.context.selected_objects
		bpy.context.view_layer.objects.active = selected_objects[0]
		bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
		bpy.ops.object.convert(target='MESH', keep_original=False)
		bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

		selected_objects = bpy.context.selected_objects
		uv_name = "Light Map"
		for obj in selected_objects:
			if obj.type == 'MESH':                
				bpy.context.view_layer.objects.active = obj
				obj.data.uv_layers.new(name=uv_name)
				obj.data.uv_layers.active = obj.data.uv_layers[uv_name]
				obj.data.uv_layers[uv_name].active_render = True
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.uv.lightmap_pack()
				bpy.ops.object.mode_set(mode='OBJECT')

		objects = selected_objects
		return objects


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))
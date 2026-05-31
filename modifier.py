import bpy
import bmesh
import operator
import mathutils
from mathutils import Vector

import importlib as imp

from . import op_modifier_apply
imp.reload(op_modifier_apply)

from . import modifiers
imp.reload(modifiers)


class Settings(bpy.types.PropertyGroup):
	active: bpy.props.BoolProperty (
		name="Active",
		default=False
	)


class Modifier:
	label = "Modifier"
	id = 'modifier'
	url = ""
	settings_class = Settings

	def __init__(self):
		pass

	#region Description
	
	def settings_path(self):
		return "FBXBundle_modifier_{}".format(self.id)


	def register(self):
		print("Register base class Settings for: {}".format(self.__class__.__name__))
		bpy.utils.register_class(self.settings_class)
		setattr(bpy.types.Scene, self.settings_path(), bpy.props.PointerProperty(type=self.settings_class))


	def unregister(self):
		bpy.utils.unregister_class(self.settings_class)
		delattr(bpy.types.Scene, self.settings_path())


	def get(self, key):
		return eval("bpy.context.scene.{}.{}".format(self.settings_path(), key))
	

	def draw(self, layout):
		row = layout.row(align=True)
		row.prop( eval("bpy.context.scene."+self.settings_path()) , "active", text="")
		row.label(text="{}".format(self.label), icon='MODIFIER')

		r = row.row(align=True)
		r.enabled = self.get("active")
		r.alignment = 'RIGHT'
		r.operator( op_modifier_apply.op.bl_idname, icon='FILE_TICK' ).modifier_index = modifiers.modifiers.index(self)

		r = row.row(align=True)
		r.alignment = 'RIGHT'
		r.operator("wm.url_open", text="", icon='QUESTION').url = self.url
		


	def print(self):
		pass
		# print("Modifier '{}'' mode: {}".format(label, mode))


	def process_objects(self, name, objects):
		return objects


	def process_name(self, name):
		return name


	def process_path(self, name, path):
		return path

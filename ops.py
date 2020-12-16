
###############################################################################
##                                                                           ##
##   MCutter add-on for Blender 2.83    Copyright (C) 2020  Pan Thistle      ##
##                                                                           ##
##   This program is free software: you can redistribute it and/or modify    ##
##   it under the terms of the GNU General Public License as published by    ##
##   the Free Software Foundation, either version 3 of the License, or       ##
##   (at your option) any later version.                                     ##
##                                                                           ##
##   This program is distributed in the hope that it will be useful,         ##
##   but WITHOUT ANY WARRANTY; without even the implied warranty of          ##
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           ##
##   GNU General Public License for more details.                            ##
##                                                                           ##
##   You should have received a copy of the GNU General Public License       ##
##   along with this program.  If not, see <https://www.gnu.org/licenses/>.  ##
##                                                                           ##
###############################################################################


# ------------------------------------------------------------------------------
#    IMPORTS
# ------------------------------------------------------------------------------
import bpy
import bmesh
import math
from mathutils import Matrix, Quaternion, Vector
# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
#    SHARED FUNCTIONS
# ------------------------------------------------------------------------------
def copy_tgt_settings(from_ob, to_ob):
    to_ob.target_wire = from_ob.target_wire
    to_ob.target_bevel_width = from_ob.target_bevel_width
    to_ob.target_bevel_clamp_overlap = from_ob.target_bevel_clamp_overlap
    to_ob.target_bevel_res = from_ob.target_bevel_res
    to_ob.target_bevel_profile = from_ob.target_bevel_profile

def copy_ctr_settings(from_ob, to_ob):
    to_ob.cutter_profile = from_ob.cutter_profile
    to_ob.cutter_bool_op = from_ob.cutter_bool_op
    to_ob.cutter_res = from_ob.cutter_res
    to_ob.frame = from_ob.frame
    to_ob.frame_size = from_ob.frame_size
    to_ob.frame_curve = from_ob.frame_curve
    to_ob.frame_res = from_ob.frame_res
    to_ob.radial = from_ob.radial
    to_ob.radial_steps = from_ob.radial_steps
    to_ob.radial_axis = from_ob.radial_axis
    to_ob.radial_angle = from_ob.radial_angle
    to_ob.radial_radius = from_ob.radial_radius
    to_ob.radial_offset = from_ob.radial_offset
    to_ob.radial_offset_symm = from_ob.radial_offset_symm
    to_ob.wave_freq = from_ob.wave_freq
    to_ob.wave_amp = from_ob.wave_amp
    to_ob.wave_phase = from_ob.wave_phase
    to_ob.wave_flip = from_ob.wave_flip
    to_ob.cutter_size = from_ob.cutter_size
    to_ob.cutter_rot = from_ob.cutter_rot
    to_ob.rot_local = from_ob.rot_local
    to_ob.cutter_pos = from_ob.cutter_pos
    to_ob.pos_local = from_ob.pos_local
    to_ob.bevel_width = from_ob.bevel_width
    to_ob.bevel_clamp_overlap = from_ob.bevel_clamp_overlap
    to_ob.bevel_res = from_ob.bevel_res
    to_ob.bevel_profile = from_ob.bevel_profile
    for i_from, i_to in zip(from_ob.arr_coll, to_ob.arr_coll):
        i_to.count = i_from.count
        i_to.offset = i_from.offset

def target_mod_remove(target, mod_name):
    mod = target.modifiers.get(mod_name)
    if mod and mod.type == 'BOOLEAN':
        target.modifiers.remove(mod)

def cutter_add(prop_name, prop_val, coll):
    me = bpy.data.meshes.new(prop_name)
    ob = bpy.data.objects.new(prop_name, me)
    ob[prop_name] = prop_val
    coll.objects.link(ob)
    return ob.name
    
def temps_remove(scene, coll_name):
    coll = scene.collection.children.get(coll_name)
    if coll:
        for ob in coll.objects:
            if ob.type == 'MESH':
                me = ob.data
                bpy.data.objects.remove(ob)
                if me.users == 0:
                    bpy.data.meshes.remove(me)
        if (not coll.objects) and (not coll.children):
            bpy.data.collections.remove(coll)
# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
#    CALLBACK FUNCTIONS
# ------------------------------------------------------------------------------
def update_style(self, context):
    if self.cutter_profile == 'Rectangle':
        self.frame_curve = False
# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
#    PROPERTIES
# ------------------------------------------------------------------------------
class CUT_array(bpy.types.PropertyGroup):
    """Cutter array modifiers item properties"""
    name: bpy.props.StringProperty(default = 'ModName')
    count: bpy.props.IntProperty(
        name = 'Count', description = 'Iterations, 1 disables the array', 
        default = 1, min = 1, soft_max = 20
        )
    offset: bpy.props.FloatVectorProperty(
        name = 'Offset', description = 'Array item offset', 
        default = [0.0, 0.3, 0.0], size = 3
        )
# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
#    OPERATORS
# ------------------------------------------------------------------------------
class MCUTTER_OT_restart(bpy.types.Operator):
    bl_label = "Restart"
    bl_idname = "mcutter.restart"
    bl_description = "Start over"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        scene = context.scene
        props = scene.ptmc_props
        if props.temps_clear:
            target = scene.objects.get(props.target_name)
            if target and target.type == 'MESH':
                me = target.data
                bpy.data.objects.remove(target)
                if me.users == 0:
                    bpy.data.meshes.remove(me)
            temps_remove(scene, props.coll_name)
        props.ul_coll.clear()
        props.target_old_mods_remove = True
        props.target_apply_scale = True
        context.area.tag_redraw()
        return {'FINISHED'}

class MCUTTER_OT_target_set(bpy.types.Operator):
    bl_label = "Set Target"
    bl_idname = "mcutter.target_set"
    bl_description = "Create target object [a copy of the active mesh]"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    @classmethod
    def poll(self, context):
        ob = context.object
        return ((ob is not None) and (ob.type == 'MESH') and 
                (len(ob.data.polygons) > 0))

    def execute(self, context):
        scene = context.scene
        props = scene.ptmc_props
        props.target_name = self.target_add(context)
        target = scene.objects.get(props.target_name)
        if props.target_old_mods_remove:
            target.modifiers.clear()
        if props.target_apply_scale:
            ms = Matrix()
            for i in range(3):
                ms[i][i] = target.scale[i]
            target.data.transform(ms)
            target.matrix_world @= ms.inverted()
        props.coll_name = self.new_collection(scene, 
                                    f'{props.base_name}_{target.name}_Temp')
        coll = scene.collection.children.get(props.coll_name)
        props.ob_id = 1
        cutter = scene.objects.get(cutter_add(props.base_name, 
                                                props.ob_id, coll))
        item = props.ul_coll.add()
        item.uid = props.ob_id
        item.name = f'{props.base_name}_{props.ob_id}'
        item.p_name = f'{props.base_name}_{props.ob_id}'
        for i in range(2):
            arr = item.arr_coll.add()
            arr.name = f'Array_{i + 1}'
        cutter.hide_viewport = True
        cutter.show_wire = False
        self.init_props(props)
        context.area.tag_redraw()
        return {'FINISHED'}

    def init_props(self, props):
        props.target_bevel_width = 0.0
        props.target_bool_effects = True
        props.target_wire = False
        props.copy_setts = True
        props.temps_clear = True
        props.ul_idx = len(props.ul_coll) - 1        

    def item_collection(self, scene, item):
        collections = item.users_collection
        if collections:
            return collections[0]
        return scene.collection

    def new_collection(self, scene, name):
        coll = bpy.data.collections.new(name)
        scene.collection.children.link(coll)
        return coll.name
    
    def target_add(self, context):
        source = context.object
        target = source.copy()
        target.data = source.data.copy()
        coll = self.item_collection(context.scene, source)
        coll.objects.link(target)
        source.hide_viewport = True
        target.hide_viewport = False
        target.show_wire = False
        bpy.ops.object.select_all(action = 'DESELECT')
        context.view_layer.objects.active = target
        target.select_set(True)
        return target.name

class MCUTTER_OT_show_target(bpy.types.Operator):
    bl_label = "Show Target"
    bl_idname = "mcutter.show_target"
    bl_description = "Show target in viewport"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        props = scene.ptmc_props
        target = scene.objects.get(props.target_name)
        target.hide_viewport = False
        target.show_wire = props.target_wire
        for mod in target.modifiers:
            if mod.type == 'BOOLEAN':
                mod.show_viewport = props.target_bool_effects
        return {'FINISHED'}

class MCUTTER_OT_add_item(bpy.types.Operator):
    bl_label = "Cutter Add"
    bl_idname = "mcutter.add_item"
    bl_description = "Add new cutter"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def invoke(self, context, event):
        props = context.scene.ptmc_props
        old_item = props.ul_coll[props.ul_idx]
        props.ob_id += 1
        item = props.ul_coll.add()
        item.uid = props.ob_id
        item.name = f'{props.base_name}_{props.ob_id}'
        item.p_name = f'{props.base_name}_{props.ob_id}'
        for i in range(2):
            arr = item.arr_coll.add()
            arr.name = f'Array_{i + 1}'
        if props.copy_setts:
            copy_ctr_settings(old_item, item)
        props.ul_idx = len(props.ul_coll) - 1
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptmc_props
        coll = scene.collection.children.get(props.coll_name)
        cutter = scene.objects.get(cutter_add(props.base_name, 
                                                props.ob_id, coll))
        cutter.hide_viewport = True
        cutter.show_wire = False
        return {'FINISHED'}

class MCUTTER_OT_remove_item(bpy.types.Operator):
    bl_label = "Cutter Remove"
    bl_idname = "mcutter.remove_item"
    bl_description = "Remove selected cutter"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    @classmethod
    def poll(self, context):
        return (len(context.scene.ptmc_props.ul_coll) > 1)
    
    def execute(self, context):
        scene = context.scene
        props = scene.ptmc_props
        target = scene.objects.get(props.target_name)
        coll = scene.collection.children.get(props.coll_name)
        idx = props.ul_idx
        item = props.ul_coll[idx]
        target_mod_remove(target, item.p_name)
        self.cutter_remove(props.base_name, item.uid, target, coll)
        props.ul_coll.remove(idx)
        props.ul_idx = min(max(0, idx - 1), len(props.ul_coll) - 1) 
        return {'FINISHED'}

    def cutter_remove(self, name, uid, target, coll):
        for ob in coll.objects:
            if (ob.keys() and ob.get(name) and (ob[name] == uid) and 
                (ob.type == 'MESH') and (ob is not target)):  
                me = ob.data
                bpy.data.objects.remove(ob)
                if me.users == 0:
                    bpy.data.meshes.remove(me)
                break

class MCUTTER_OT_update(bpy.types.Operator):
    bl_label = "Update"
    bl_idname = "mcutter.update"
    bl_description = "Run object updates"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    bevel_tabs: bpy.props.EnumProperty(
        items=(
        ('TARGET', 'Target', 'Target bevel'),
        ('CUTTER', 'Cutter', 'Cutter Bevel'),
        ),
        name = "Bevel",
        description = "Option",
        default = "TARGET",
        )
    array_tabs: bpy.props.EnumProperty(
        items=(
        ('RADIAL', 'Radial', 'Radial array'),
        ('MOD', 'Modifiers', 'Array modifiers'),
        ),
        name = "Array",
        description = "Option",
        default = "RADIAL",
        )
    vis_style: bpy.props.BoolProperty(
        name = 'Style', description = 'Style options', 
        default = True)
    vis_resol: bpy.props.BoolProperty(
        name = 'Resolution', description = 'Resolution - Bevel', 
        default = False)
    vis_trans: bpy.props.BoolProperty(
        name = 'Transforms', description = 'Size - Transforms', 
        default = False)
    vis_array: bpy.props.BoolProperty(
        name = 'Arrays', description = 'Radial - Modifiers', 
        default = False)
    target_visible: bpy.props.BoolProperty(
        name = 'Target', description = 'Show target', 
        default = True
        )
    target_wire: bpy.props.BoolProperty(
        name = 'Wire', description = 'Show target edges', 
        default = False
        )
    cutter_visible: bpy.props.BoolProperty(
        name = 'Cutter', description = 'Show Cutter', 
        default = False
        )
    cutter_wire: bpy.props.BoolProperty(
        name = 'Wire', description = 'Show cutter edges', 
        default = False
        )
    cutter_effect: bpy.props.BoolProperty(
        name = 'Effect', description = 'Show effect', 
        default = True
        )
    arr_coll: bpy.props.CollectionProperty(type = CUT_array)
    cutter_profile: bpy.props.EnumProperty(
        items = (
        ('Rectangle', 'Rectangle', 'rectangle profile'),
        ('Ellipse', 'Ellipse', 'ellipse profile'),
        ('Wave', 'Wave', 'wave profile'),
        ),
        name = 'Profile',
        description = 'Select profile',
        default = 'Ellipse',
        update = update_style
        )
    cutter_bool_op: bpy.props.EnumProperty(
        items = (
        ('DIFFERENCE', 'Difference', 'difference boolean'),
        ('UNION', 'Union', 'union boolean'),
        ('INTERSECT', 'Intersect', 'intersect boolean'),
        ),
        name = 'Boolean',
        description = 'Select boolean operation',
        default = 'DIFFERENCE',
        )
    cutter_size: bpy.props.FloatVectorProperty(
        name = 'Size', description = 'Cutter dimensions', 
        default = [2.5, 0.1, 2.5], min = 0.0001, size = 3
        )
    cutter_res: bpy.props.IntProperty(
        name = 'Profile Segs', description = 'Profile segments', 
        default = 4, min = 3, soft_max = 90
        )
    frame: bpy.props.BoolProperty(
        name = 'Frame', description = 'Use frame cutter', 
        default = False
        )
    frame_size: bpy.props.FloatProperty(
        name = 'Frame Size', description = 'Frame diameter', 
        default = 0.1, min = 0.0001
        )
    frame_curve: bpy.props.BoolProperty(
        name = 'Frame Curve', description = 'Use curve frame', 
        default = False
        )
    frame_res: bpy.props.IntProperty(
        name = 'Frame Segs', description = 'Frame segments', 
        default = 12, min = 3, soft_max = 90
        )
    radial: bpy.props.BoolProperty(
        name = 'Radial', description = 'Use radial cutter', 
        default = False
        )
    radial_axis: bpy.props.EnumProperty(
        items = (
        ('X', 'X', 'radial x axis'),
        ('Y', 'Y', 'radial y axis'),
        ('Z', 'Z', 'radial z axis'),
        ),
        name = 'Radial Axis',
        description = 'Radial rotation axis',
        default = 'Y'
        )
    radial_angle: bpy.props.FloatProperty(
        name = 'Angle', description = 'Radial angle', 
        default = 1.570796326794, subtype = 'ANGLE'
        )
    radial_steps: bpy.props.IntProperty(
        name = 'Steps', description = 'Radial iterations', 
        default = 2, min = 1, soft_max = 12
        )
    radial_radius: bpy.props.FloatProperty(
        name = 'Radius', description = 'Radial radius', 
        default = 0.5
        )
    radial_offset: bpy.props.FloatProperty(
        name = 'Offset', description = 'Radial offset', 
        default = 0.0
        )
    radial_offset_symm: bpy.props.BoolProperty(
        name = 'Offset Mirror', description = 'Radial offset symmetry', 
        default = False
        )
    wave_freq: bpy.props.FloatProperty(
        name = 'Frequency', description = 'Wave frequency', 
        default = 0.5
        )
    wave_amp: bpy.props.FloatProperty(
        name = 'Amplitude', description = 'Wave amplitude', 
        default = 0.2, min = 0.0
        )
    wave_phase: bpy.props.FloatProperty(
        name = 'Phase', description = 'Wave phase', 
        default = 0.0
        )
    wave_flip: bpy.props.BoolProperty(
        name = 'Flip', description = 'Wave flip profile axes', 
        default = False
        )
    cutter_rot: bpy.props.FloatVectorProperty(
        name = 'Rotation', description = 'Rotate the cutter', 
        default = [0.0, 0.0, 0.0], size = 3, subtype = 'EULER'
        )
    rot_local: bpy.props.BoolProperty(
        name = 'Relative', description = 'Inherits Target Rotation', 
        default = True
        )
    cutter_pos: bpy.props.FloatVectorProperty(
        name = 'Position', description = 'Position the cutter', 
        default = [0.0, 0.0, 0.0], size = 3, subtype = 'TRANSLATION'
        )
    pos_local: bpy.props.BoolProperty(
        name = 'Relative', description = 'Inherits Target Location', 
        default = True
        )
    bevel_width: bpy.props.FloatProperty(
        name = 'Width', description = 'Bevel width', 
        default = 0.0, min = 0.0
        )
    bevel_clamp_overlap: bpy.props.BoolProperty(
        name = 'Clamp Overlap', description = 'Clamp width to avoid overlap', 
        default = False
        )
    bevel_res: bpy.props.IntProperty(
        name = 'Segments', description = 'Bevel segments', 
        default = 2, min = 1, soft_max = 8
        )
    bevel_profile: bpy.props.FloatProperty(
        name = 'Profile', description = 'Bevel profile', 
        default = 0.5, min = 0.0, max = 1.0
        )
    target_bevel_width: bpy.props.FloatProperty(
        name = 'Width', description = 'Bevel width', 
        default = 0.0, min = 0.0
        )
    target_bevel_clamp_overlap: bpy.props.BoolProperty(
        name = 'Clamp Overlap', description = 'Clamp width to avoid overlap', 
        default = True
        )
    target_bevel_res: bpy.props.IntProperty(
        name = 'Segments', description = 'Bevel segments', 
        default = 2, min = 1, soft_max = 8
        )
    target_bevel_profile: bpy.props.FloatProperty(
        name = 'Profile', description = 'Bevel profile', 
        default = 0.5, min = 0.0, max = 1.0
        )

    def invoke(self, context, event):
        props = context.scene.ptmc_props
        item = props.ul_coll[props.ul_idx]
        self.arr_coll.clear()
        for i in range(2):
            arr = self.arr_coll.add()
            arr.name = f'Array_{i+1}'
        copy_ctr_settings(item, self)
        copy_tgt_settings(props, self)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptmc_props
        target = scene.objects.get(props.target_name)
        coll = scene.collection.children.get(props.coll_name)
        item = props.ul_coll[props.ul_idx]
        cutter = self.cutter_get(props.base_name, item.uid, target, coll)
        if cutter is None:
            idx = props.ul_idx
            target_mod_remove(target, item.p_name)
            if len(props.ul_coll) > 1:
                props.ul_coll.remove(idx)
                props.ul_idx = min(max(0, idx - 1), len(props.ul_coll) - 1) 
            self.report({'WARNING'}, 'MCutter object not found')
            return {'CANCELLED'}
        self.cutter_transform(cutter, target)
        if self.cutter_profile == 'Wave':
            self.cutter_mesh_update_wave(cutter.data)
        elif self.cutter_profile == 'Ellipse':
            self.cutter_mesh_update_ellipse(cutter.data)
        else:
            self.cutter_mesh_update_rectangle(cutter.data)
        self.mesh_options_update(cutter.data, True, True)
        self.mesh_options_update(target.data, True, True)
        self.cutter_mods_update(cutter)
        self.target_mods_update(target, item.p_name, cutter)
        copy_ctr_settings(self, item)
        copy_tgt_settings(self, props)
        target.hide_viewport = not self.target_visible
        target.show_wire = self.target_wire
        cutter.hide_viewport = not self.cutter_visible
        cutter.show_wire = self.cutter_wire
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col_main = box.column()
        row = col_main.row()
        split = row.split()
        col = split.column()
        col.prop(self, 'target_visible', toggle = True)
        col = split.column()
        col.enabled = self.target_visible
        col.prop(self, 'target_wire', toggle = True)
        col = split.column()
        col.enabled = self.target_visible
        col.prop(self, 'cutter_effect', toggle = True)
        row = col_main.row()
        split = row.split()
        col = split.column()
        col.prop(self, 'cutter_visible', toggle = True)
        col = split.column()
        col.enabled = self.cutter_visible
        col.prop(self, 'cutter_wire', toggle = True)

        box = layout.box()
        row = box.row(align = True)
        row.prop(self, 'cutter_profile', text = '')
        row.prop(self, 'cutter_bool_op', text = '')

        col = box.column(align = True)
        row = col.row()
        row.prop(self, 'vis_style', 
                icon = 'TRIA_DOWN' if self.vis_style else 'TRIA_RIGHT', 
                icon_only = True, emboss = False)
        row.label(text = 'Style options')
        if self.vis_style:
            #col = box.column(align = True)
            row = box.row()
            split = row.split()
            col = split.column()
            col.prop(self, 'frame', toggle = True)
            col = split.column()
            col.enabled = self.frame
            col.prop(self, 'frame_size')
            col = split.column()
            col.enabled = self.frame and (self.cutter_profile != 'Rectangle')
            col.prop(self, 'frame_curve', toggle = True)
            if self.cutter_profile == 'Wave':
                col = box.column(align = True)
                row = col.row()
                split = row.split()
                split.prop(self, 'wave_flip')
                split.prop(self, 'wave_amp')
                row = col.row()
                split = row.split()
                split.prop(self, 'wave_freq')
                split.prop(self, 'wave_phase')

        col = box.column(align = True)
        row = col.row()
        row.prop(self, 'vis_resol', 
                icon = 'TRIA_DOWN' if self.vis_resol else 'TRIA_RIGHT', 
                icon_only = True, emboss = False)
        row.label(text = 'Resolution - Bevel')
        if self.vis_resol:
            col = box.column(align = True)
            row = col.row()
            split = row.split()
            col = split.column()
            col.enabled = (self.cutter_profile != 'Rectangle')
            col.prop(self, 'cutter_res')
            col = split.column()
            col.enabled = self.frame_curve and self.frame
            col.prop(self, 'frame_res')            
            col = box.column(align = True)
            col.label(text = 'Bevel')
            row = col.row(align = True)
            row.prop(self, 'bevel_tabs', expand = True)
            if self.bevel_tabs == 'TARGET':
                row = col.row(align = True)
                row.prop(self, 'target_bevel_width')
                row.prop(self, 'target_bevel_clamp_overlap')
                row = col.row(align = True)
                row.prop(self, 'target_bevel_res')
                row.prop(self, 'target_bevel_profile')
            else:
                row = col.row(align = True)
                row.prop(self, 'bevel_width')
                row.prop(self, 'bevel_clamp_overlap')
                row = col.row(align = True)
                row.prop(self, 'bevel_res')
                row.prop(self, 'bevel_profile')
        
        col = box.column(align = True)
        row = col.row()
        row.prop(self, 'vis_trans', 
                icon = 'TRIA_DOWN' if self.vis_trans else 'TRIA_RIGHT', 
                icon_only = True, emboss = False)
        row.label(text = 'Transforms')
        if self.vis_trans:
            #col = box.column(align = True)
            row = box.row(align = True)
            row.prop(self, 'cutter_size')
            row = col.row(align = True)
            split = row.split()
            col = split.column()
            col.label(text = 'Position:')
            col.prop(self, 'cutter_pos', text = '')
            col.prop(self, 'pos_local')
            col = split.column()
            col.label(text = 'Rotation:')
            col.prop(self, 'cutter_rot', text = '')
            col.prop(self, 'rot_local')

        col = box.column(align = True)
        row = col.row()
        row.prop(self, 'vis_array', 
                icon = 'TRIA_DOWN' if self.vis_array else 'TRIA_RIGHT', 
                icon_only = True, emboss = False)
        row.label(text = 'Arrays')
        if self.vis_array:
            #col = box.column(align = True)
            row = box.row(align = True)
            row.prop(self, 'array_tabs', expand = True)
            if self.array_tabs == 'RADIAL':
                col = box.column(align = True)
                row = col.row()
                split = row.split()
                col = split.column()
                col.prop(self, 'radial', text = 'Enable', toggle = True)
                col = split.column()
                col.enabled = self.radial
                col.prop(self, 'radial_steps')
                col = split.column()
                col.enabled = self.radial
                col.prop(self, 'radial_radius')
                col = box.column(align = True)
                row = col.row()
                split = row.split()
                split.enabled = self.radial
                split.prop(self, 'radial_axis', text = '')
                split.prop(self, 'radial_angle')
                col = box.column(align = True)
                row = col.row()
                split = row.split()
                split.enabled = self.radial
                split.prop(self, 'radial_offset')
                split.prop(self, 'radial_offset_symm')
            else:
                for mod in self.arr_coll:
                    col = box.column(align = True)
                    col.label(text = f'{mod.name}')
                    row = col.row()
                    row.prop(mod, 'count')
                    row = col.row()
                    row.prop(mod, 'offset')

    def cutter_get(self, name, uid, target, coll):
        found = None        
        for ob in coll.objects:
            if (ob.keys() and ob.get(name) and (ob[name] == uid) and 
                (ob.type == 'MESH') and (ob is not target)):
                found = ob
                break
        return found

    def cutter_transform(self, cutter, target):
        c_rot = self.cutter_rot.to_quaternion()
        c_loc = self.cutter_pos
        t_loc, t_rot, t_sca = target.matrix_world.decompose()
        rot = (t_rot @ c_rot) if self.rot_local else c_rot
        cutter.rotation_mode = 'XYZ'
        cutter.rotation_euler = rot.to_euler()
        loc = (t_rot @ c_loc + t_loc) if self.pos_local else c_loc
        cutter.location = loc

    def radial_rotation(self, steps):
        da = self.radial_angle
        offset = self.radial_offset
        radius = self.radial_radius
        if self.radial_offset_symm:
            dv = [-offset if i%2 else offset for i in range(steps)]
        else:
            dv = [offset * i for i in range(steps)]
        if self.radial_axis == 'X':
            coords = [Vector((dv[i], radius * math.cos(i * da), 
                    radius * math.sin(i * da))) for i in range(steps)]
            axis = Vector((1, 0, 0))
        elif self.radial_axis == 'Y':
            coords = [Vector((radius * math.cos(i * da), dv[i], 
                    radius * math.sin(i * da))) for i in range(steps)]
            axis = Vector((0, -1, 0)) 
        else:
            coords = [Vector((radius * math.cos(i * da), 
                    radius * math.sin(i * da), dv[i])) for i in range(steps)]
            axis = Vector((0, 0, 1))
        rot = [Quaternion(axis, i * da) for i in range(steps)]
        return coords, rot

    def p_cuboid(self, rad):
        return [Vector((rad[0], -rad[1], -rad[2])), 
                Vector((rad[0], -rad[1], rad[2])), 
                Vector((-rad[0], -rad[1], rad[2])), 
                Vector((-rad[0], -rad[1], -rad[2])),
                Vector((rad[0], rad[1], -rad[2])), 
                Vector((rad[0], rad[1], rad[2])), 
                Vector((-rad[0], rad[1], rad[2])), 
                Vector((-rad[0], rad[1], -rad[2]))]

    def p_cuboid_frame(self, rad_a, rad_b):
        y = rad_a[1]
        return [Vector((rad_b[0], -y, -rad_b[2])), 
                Vector((rad_b[0], y, -rad_b[2])), 
                Vector((rad_a[0], y, -rad_a[2])), 
                Vector((rad_a[0], -y, -rad_a[2])),
                Vector((rad_b[0], -y, rad_b[2])), 
                Vector((rad_b[0], y, rad_b[2])), 
                Vector((rad_a[0], y, rad_a[2])), 
                Vector((rad_a[0], -y, rad_a[2])),
                Vector((-rad_b[0], -y, rad_b[2])), 
                Vector((-rad_b[0], y, rad_b[2])), 
                Vector((-rad_a[0], y, rad_a[2])), 
                Vector((-rad_a[0], -y, rad_a[2])),
                Vector((-rad_b[0], -y, -rad_b[2])), 
                Vector((-rad_b[0], y, -rad_b[2])), 
                Vector((-rad_a[0], y, -rad_a[2])), 
                Vector((-rad_a[0], -y, -rad_a[2]))]

    def cuboid_add_faces(self, bm, verts):
        for i in range(3):
            bm.faces.new([verts[i], verts[i + 4], verts[i + 5], verts[i + 1]])
        bm.faces.new([verts[4], verts[0], verts[3], verts[7]])
        bm.faces.new(verts[:4])
        bm.faces.new(verts[4:][::-1])

    def cuboid_frame_add_faces(self, bm, verts):
        for i in range(3):
            loop = i * 4
            for j in range(3):
                bm.faces.new((verts[loop + j], verts[loop + j + 1], 
                            verts[loop + j + 5], verts[loop + j + 4]))
            bm.faces.new((verts[loop], verts[loop + 4], verts[loop + 7], 
                            verts[loop + 3]))
        for i in range(1, 4):
            bm.faces.new([verts[i], verts[i - 1], verts[i - 5], verts[i - 4]])
        bm.faces.new([verts[0], verts[3], verts[-1], verts[-4]])

    def mesh_update_rect_plain(self, bm, radii):
        coords = self.p_cuboid(radii)
        verts = [bm.verts.new(co) for co in coords]
        self.cuboid_add_faces(bm, verts)

    def mesh_update_rect_radial(self, bm, radii):
        steps = self.radial_steps
        coords = self.p_cuboid(radii)
        coords_rad, rot = self.radial_rotation(steps)
        for i in range(steps):
            verts = [bm.verts.new(rot[i] @ co + coords_rad[i]) for co in coords]
            self.cuboid_add_faces(bm, verts)

    def mesh_update_rect_frame(self, bm, radii, f_rad):
        coords = self.p_cuboid_frame(radii, (radii[0] + f_rad, 0, 
                                        radii[2] + f_rad))
        verts = [bm.verts.new(co) for co in coords]
        self.cuboid_frame_add_faces(bm, verts)

    def mesh_update_rect_radial_frame(self, bm, radii, f_rad):
        steps = self.radial_steps
        coords = self.p_cuboid_frame(radii, (radii[0] + f_rad, 0, 
                                        radii[2] + f_rad))
        coords_rad, rot = self.radial_rotation(steps)
        for i in range(steps):
            verts = [bm.verts.new(rot[i] @ co + coords_rad[i]) for co in coords]
            self.cuboid_frame_add_faces(bm, verts)

    def cutter_mesh_update_rectangle(self, me):
        radii = [self.cutter_size[i] / 2 for i in range(3)]
        f_rad = self.frame_size / 2
        steps = self.radial_steps
        bm = bmesh.new(use_operators = False)
        if self.radial and self.frame:
            self.mesh_update_rect_radial_frame(bm, radii, f_rad)
        elif self.frame:
            self.mesh_update_rect_frame(bm, radii, f_rad)
        elif self.radial:
            self.mesh_update_rect_radial(bm, radii)
        else:
            self.mesh_update_rect_plain(bm, radii)  
        bm.to_mesh(me)
        me.update()
        bm.free()

    def p_ellipse(self, rad, res):
        da = 2 * math.pi / res
        return [Vector((rad[0] * math.cos(i * da), 0, 
                rad[2] * math.sin(i * da))) for i in range(res)]

    def f_ellipse(self, rad, res):
        da = 2 * math.pi / res
        return [Vector((0, rad[1] * math.cos(i * da), 
                rad[2] * math.sin(i * da))) for i in range(res)]

    def cylinder_coords(self, radii, res):
        coords = self.p_ellipse(radii, res)
        vy = Vector((0, radii[1], 0))
        return [co - vy for co in coords] + [co + vy for co in coords]

    def cylinder_add_faces(self, bm, verts, res):
        for i in range(res - 1):
            bm.faces.new([verts[i], verts[i + res], verts[i + res + 1], 
                            verts[i + 1]])
        bm.faces.new([verts[res], verts[0], verts[res - 1], verts[-1]])
        bm.faces.new(verts[:res])
        bm.faces.new(verts[res:][::-1])

    def cylinder_frame_coords(self, radii, res, f_rad):
        path = self.p_ellipse((radii[0] + f_rad, 0, radii[2] + f_rad), res)
        ring = [
                Vector((0, radii[1], -f_rad)), Vector((0, radii[1], f_rad)), 
                Vector((0, -radii[1], f_rad)), Vector((0, -radii[1], -f_rad))
                ]
        axis = Vector((0, -1, 0))
        hpi = math.pi / 2
        da = 2 * math.pi / res
        return [Quaternion(axis, hpi + i * da) @ ring[j] + path[i] 
                            for i in range(res) for j in range(4)]

    def cylinder_frame_add_faces(self, bm, verts, res):
        for i in range(res - 1):
            loop = i * 4
            for j in range(3):
                bm.faces.new((verts[loop + j], verts[loop + j + 1], 
                            verts[loop + j + 5], verts[loop + j + 4]))
            bm.faces.new((verts[loop], verts[loop + 4], verts[loop + 7], 
                        verts[loop + 3]))
        for i in range(1, 4):
            bm.faces.new([verts[i], verts[i - 1], verts[i - 5], verts[i - 4]])
        bm.faces.new([verts[0], verts[3], verts[-1], verts[-4]])

    def torus_coords(self, radii, res, f_rad, f_res):
        path = self.p_ellipse((radii[0] + f_rad, 0, radii[2] + f_rad), res)
        ring = self.f_ellipse((0, radii[1], f_rad), f_res)
        axis = Vector((0, -1, 0))
        hpi = math.pi / 2
        da = 2 * math.pi / res
        return [Quaternion(axis, hpi + i * da) @ ring[j] + path[i] 
                            for i in range(res) for j in range(f_res)]

    def torus_add_faces(self, bm, verts, res, f_res):
        for i in range(res - 1):
            loop = i * f_res
            for j in range(f_res - 1):
                bm.faces.new((verts[loop + j], verts[loop + j + 1], 
                            verts[loop + f_res + j + 1], 
                            verts[loop + f_res + j]))
            bm.faces.new((verts[loop], verts[loop + f_res], 
                        verts[loop + 2 * f_res - 1], 
                        verts[loop + f_res - 1]))
        for i in range(1, f_res):
            bm.faces.new([verts[i], verts[i - 1], verts[-f_res - 1 + i], 
                        verts[-f_res + i]])
        bm.faces.new([verts[0], verts[f_res - 1], verts[-1], verts[-f_res]])

    def mesh_update_elli_plain(self, bm, radii):
        res = self.cutter_res
        coords = self.cylinder_coords(radii, res)
        verts = [bm.verts.new(co) for co in coords]
        self.cylinder_add_faces(bm, verts, res)

    def mesh_update_elli_radial(self, bm, radii):
        res = self.cutter_res
        steps = self.radial_steps
        coords = self.cylinder_coords(radii, res)
        coords_rad, rot = self.radial_rotation(steps)
        for i in range(steps):
            verts = [bm.verts.new(rot[i] @ co + coords_rad[i]) for co in coords]
            self.cylinder_add_faces(bm, verts, res)

    def mesh_update_elli_frame(self, bm, radii, f_rad):
        res = self.cutter_res
        coords = self.cylinder_frame_coords(radii, res, f_rad)
        verts = [bm.verts.new(co) for co in coords]
        self.cylinder_frame_add_faces(bm, verts, res)
        
    def mesh_update_elli_radial_frame(self, bm, radii, f_rad):
        res = self.cutter_res
        steps = self.radial_steps
        coords = self.cylinder_frame_coords(radii, res, f_rad)
        coords_rad, rot = self.radial_rotation(steps)
        for i in range(steps):
            verts = [bm.verts.new(rot[i] @ co + coords_rad[i]) for co in coords]
            self.cylinder_frame_add_faces(bm, verts, res)

    def mesh_update_elli_frame_curve(self, bm, radii, f_rad):
        res = self.cutter_res
        f_res = self.frame_res
        coords = self.torus_coords(radii, res, f_rad, f_res)
        verts = [bm.verts.new(co) for co in coords]
        self.torus_add_faces(bm, verts, res, f_res)
            
    def mesh_update_elli_radial_frame_curve(self, bm, radii, f_rad):
        res = self.cutter_res
        f_res = self.frame_res
        steps = self.radial_steps
        coords = self.torus_coords(radii, res, f_rad, f_res)
        coords_rad, rot = self.radial_rotation(steps) 
        for i in range(steps):
            verts = [bm.verts.new(rot[i] @ co + coords_rad[i]) for co in coords]
            self.torus_add_faces(bm, verts, res, f_res)

    def cutter_mesh_update_ellipse(self, me):
        radii = [self.cutter_size[i] / 2 for i in range(3)]
        f_rad = self.frame_size / 4
        bm = bmesh.new(use_operators = False)
        if self.radial and self.frame_curve and self.frame:
            self.mesh_update_elli_radial_frame_curve(bm, radii, f_rad)
        elif self.frame_curve and self.frame:
            self.mesh_update_elli_frame_curve(bm, radii, f_rad)
        elif self.radial and self.frame:
            self.mesh_update_elli_radial_frame(bm, radii, f_rad)
        elif self.frame:
            self.mesh_update_elli_frame(bm, radii, f_rad)
        elif self.radial:
            self.mesh_update_elli_radial(bm, radii)
        else:
            self.mesh_update_elli_plain(bm, radii)
        bm.to_mesh(me)
        me.update()
        bm.free()

    def p_wave_ring(self, path, path_res, ring, ring_res):
        path_pad = [path[0]] + path + [path[-1]]
        rot = [(path_pad[i + 1] - path_pad[i - 1]).to_track_quat('X', 'Z') 
                    for i in range(1, path_res + 1)]
        return [rot[i] @ ring[j] + path[i] for i in range(path_res) 
                    for j in range(ring_res)]

    def p_wave(self, rad, res):
        amp = self.wave_amp
        freq = self.wave_freq
        phase = self.wave_phase
        dx = 2 * rad[0] / (res - 1)
        dw = freq * 2 * math.pi / (res - 1)
        return [Vector((-rad[0] + i * dx, 0, 
                        rad[2] + amp * math.sin(i * dw + phase))) 
                            for i in range(res)]

    def wave_wall_coords(self, radii, res):
        coords = self.p_wave(radii, res)
        rev = Quaternion(Vector((1, 0, 0)), math.pi)
        coords = coords + [rev @ co for co in coords][::-1]
        loop = len(coords)
        vy = Vector((0, radii[1], 0))
        coords = [co - vy for co in coords]
        coords += [co + 2 * vy for co in coords]
        if self.wave_flip:
            y_fix = Quaternion(Vector((0, 1, 0)), math.pi / 2)
            coords = [y_fix @ co for co in coords]
        return coords, loop
        
    def wave_wall_add_faces(self, bm, verts, loop):
        for i in range(loop - 1):
            bm.faces.new([verts[i + 1], verts[i + loop + 1], 
                        verts[i + loop], verts[i]])
        bm.faces.new([verts[-1], verts[loop - 1], verts[0], verts[loop]])
        bm.faces.new(verts[:loop][::-1])
        bm.faces.new(verts[loop:])
        
    def wave_tube_flat_coords(self, radii, res, f_rad):
        coords_p = self.p_wave((radii[0], 0, radii[2] + f_rad), res)    
        coords_f = [Vector((0, radii[1], -f_rad)), 
                    Vector((0, radii[1], f_rad)), 
                    Vector((0, -radii[1], f_rad)), 
                    Vector((0, -radii[1], -f_rad))]
        coords = self.p_wave_ring(coords_p, res, coords_f, 4)
        rev = Quaternion(Vector((1, 0, 0)), math.pi)
        if self.wave_flip:
            y_fix = Quaternion(Vector((0, 1, 0)), math.pi / 2)
            coords = [y_fix @ co for co in coords]
            rev = Quaternion(Vector((0, 0, 1)), math.pi)
        return coords, rev

    def wave_tube_round_coords(self, radii, res, f_rad, f_res):
        coords_p = self.p_wave((radii[0], 0, radii[2] + f_rad), res)
        coords_f = self.f_ellipse((0, radii[1], f_rad), f_res)
        coords = self.p_wave_ring(coords_p, res, coords_f, f_res)
        rev = Quaternion(Vector((1, 0, 0)), math.pi)
        if self.wave_flip:
            y_fix = Quaternion(Vector((0, 1, 0)), math.pi / 2)
            coords = [y_fix @ co for co in coords]
            rev = Quaternion(Vector((0, 0, 1)), math.pi)
        return coords, rev

    def wave_tube_add_faces(self, bm, verts, res, f_res):
        bm.faces.new(verts[:f_res][::-1])
        bm.faces.new(verts[(res - 1) * f_res:])
        for i in range(res - 1):
            loop = i * f_res
            for j in range(f_res - 1):
                bm.faces.new((verts[loop + j], verts[loop + j + 1], 
                            verts[loop + f_res + j + 1], 
                            verts[loop + f_res + j]))
            bm.faces.new((verts[loop], verts[loop + f_res], 
                            verts[loop + 2 * f_res - 1], 
                            verts[loop + f_res - 1]))

    def mesh_update_wave_plain(self, bm, radii, res):
        coords, loop = self.wave_wall_coords(radii, res)
        verts = [bm.verts.new(co) for co in coords]
        self.wave_wall_add_faces(bm, verts, loop)

    def mesh_update_wave_radial(self, bm, radii, res):
        steps = self.radial_steps
        coords, loop = self.wave_wall_coords(radii, res)
        coords_rad, rot = self.radial_rotation(steps)
        for i in range(steps):
            verts = [bm.verts.new(rot[i] @ co + coords_rad[i]) for co in coords]
            self.wave_wall_add_faces(bm, verts, loop)

    def mesh_update_wave_frame(self, bm, radii, res, f_rad):
        coords, rev = self.wave_tube_flat_coords(radii, res, f_rad)
        verts = [bm.verts.new(co) for co in coords]
        self.wave_tube_add_faces(bm, verts, res, 4)
        verts = [bm.verts.new(rev @ co) for co in coords]
        self.wave_tube_add_faces(bm, verts, res, 4)

    def mesh_update_wave_radial_frame(self, bm, radii, res, f_rad):
        steps = self.radial_steps
        coords, rev = self.wave_tube_flat_coords(radii, res, f_rad)
        coords_rad, rot = self.radial_rotation(steps)
        for i in range(steps):
            verts = [bm.verts.new(rot[i] @ co + coords_rad[i]) for co in coords]
            self.wave_tube_add_faces(bm, verts, res, 4)
            verts = [bm.verts.new(rot[i] @ (rev @ co) + coords_rad[i]) 
                        for co in coords]    
            self.wave_tube_add_faces(bm, verts, res, 4)
        
    def mesh_update_wave_frame_curve(self, bm, radii, res, f_rad):
        f_res = self.frame_res
        coords, rev = self.wave_tube_round_coords(radii, res, f_rad, f_res)
        verts = [bm.verts.new(co) for co in coords]
        self.wave_tube_add_faces(bm, verts, res, f_res)
        verts = [bm.verts.new(rev @ co) for co in coords]    
        self.wave_tube_add_faces(bm, verts, res, f_res)
        
    def mesh_update_wave_radial_frame_curve(self, bm, radii, res, f_rad):
        f_res = self.frame_res
        steps = self.radial_steps
        coords, rev = self.wave_tube_round_coords(radii, res, f_rad, f_res)
        coords_rad, rot = self.radial_rotation(steps)
        for i in range(steps):
            verts = [bm.verts.new(rot[i] @ co + coords_rad[i]) for co in coords]
            self.wave_tube_add_faces(bm, verts, res, f_res)
            verts = [bm.verts.new(rot[i] @ (rev @ co) + coords_rad[i]) 
                        for co in coords]
            self.wave_tube_add_faces(bm, verts, res, f_res) 

    def cutter_mesh_update_wave(self, me):
        radii = [self.cutter_size[i] / 2 for i in range(3)]
        res = self.cutter_res + 1
        f_rad = self.frame_size / 4
        bm = bmesh.new(use_operators = False)
        if self.radial and self.frame_curve and self.frame:
            self.mesh_update_wave_radial_frame_curve(bm, radii, res, f_rad)
        elif self.frame_curve and self.frame:
            self.mesh_update_wave_frame_curve(bm, radii, res, f_rad)
        elif self.radial and self.frame:
            self.mesh_update_wave_radial_frame(bm, radii, res, f_rad)
        elif self.frame:
            self.mesh_update_wave_frame(bm, radii, res, f_rad)
        elif self.radial:
            self.mesh_update_wave_radial(bm, radii, res)
        else:
            self.mesh_update_wave_plain(bm, radii, res)
        bm.to_mesh(me)
        me.update()
        bm.free()

    def mesh_options_update(self, me, smooth_shade, smooth_norm):
        smooth_lst = [smooth_shade] * len(me.polygons)
        me.polygons.foreach_set("use_smooth", smooth_lst)
        me.use_auto_smooth = smooth_norm

    def cutter_mods_update(self, cutter):
        for arr in self.arr_coll:
            found = False
            mod = cutter.modifiers.get(arr.name)
            if mod and mod.type == 'ARRAY':
                found = True
            if not found: 
                mod = cutter.modifiers.new(name = arr.name, type = 'ARRAY')
            mod.fit_type = 'FIXED_COUNT'
            mod.count = arr.count
            mod.use_relative_offset = False
            mod.use_object_offset = False
            mod.use_constant_offset = True
            mod.constant_offset_displace = arr.offset 
            mod.show_expanded = False
        found = False
        mod = cutter.modifiers.get('Bevel')
        if mod and mod.type == 'BEVEL':
            found = True
        if not found: 
            mod = cutter.modifiers.new(name = 'Bevel', type = 'BEVEL')
        mod.width = self.bevel_width
        mod.use_clamp_overlap = self.bevel_clamp_overlap
        mod.segments = self.bevel_res
        mod.profile = self.bevel_profile
        mod.loop_slide = True
        mod.harden_normals = False
        mod.limit_method = 'ANGLE'
        mod.angle_limit = math.pi / 6
        mod.show_expanded = False
        self.modifier_move_to_top(cutter, 'Bevel', 'BEVEL')

    def target_mods_update(self, target, mod_name, cutter):
        found = False
        mod = target.modifiers.get(mod_name)
        if mod and mod.type == 'BOOLEAN':
            found = True
        if not found:
            mod = target.modifiers.new(name = mod_name, type = 'BOOLEAN')    
        mod.operation = self.cutter_bool_op
        mod.object = cutter
        mod.show_viewport = self.cutter_effect
        mod.show_expanded = False
        found = False
        mod = target.modifiers.get('Bevel')
        if mod and mod.type == 'BEVEL':
            found = True
        if not found: 
            mod = target.modifiers.new(name = 'Bevel', type = 'BEVEL')
        mod.width = self.target_bevel_width
        mod.use_clamp_overlap = self.target_bevel_clamp_overlap
        mod.segments = self.target_bevel_res
        mod.profile = self.target_bevel_profile
        mod.loop_slide = True
        mod.harden_normals = True
        mod.limit_method = 'ANGLE'
        mod.angle_limit = math.pi / 6
        mod.show_expanded = False
        self.modifier_move_to_bottom(target, 'Bevel', 'BEVEL')

    def modifier_move_to_top(self, ob, name, type):
        mod = ob.modifiers.get(name)
        if mod and mod.type == type:
            bpy.context.view_layer.objects.active = ob
            while ob.modifiers.find(name) != 0:
                bpy.ops.object.modifier_move_up(modifier = name)

    def modifier_move_to_bottom(self, ob, name, type):
        mod = ob.modifiers.get(name)
        if mod and mod.type == type:
            bpy.context.view_layer.objects.active = ob
            id_last = len(ob.modifiers) - 1
            while ob.modifiers.find(name) < id_last:
                bpy.ops.object.modifier_move_down(modifier = name)

class MCUTTER_OT_hide_cutters(bpy.types.Operator):
    bl_label = "Hide cutters"
    bl_idname = "mcutter.hide_cutters"
    bl_description = "Hide all cutters in viewport"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        coll = scene.collection.children.get(scene.ptmc_props.coll_name)
        for ob in coll.objects:
            ob.hide_viewport = True
        return {'FINISHED'}

class MCUTTER_OT_finalize(bpy.types.Operator):
    bl_label = "Finalize"
    bl_idname = "mcutter.finalize"
    bl_description = "Apply all modifiers to target mesh object"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        scene = context.scene
        props = scene.ptmc_props
        target = scene.objects.get(props.target_name)
        if target.modifiers:
            self.modifier_apply_all(context, target)
        temps_remove(scene, props.coll_name)
        props.ul_coll.clear()
        props.target_old_mods_remove = True
        props.target_apply_scale = True
        context.area.tag_redraw()
        return {'FINISHED'}

    def modifier_apply_all(self, context, ob):
        dg = context.evaluated_depsgraph_get()
        ob_eval = ob.evaluated_get(dg)
        mesh_from_eval = bpy.data.meshes.new_from_object(ob_eval)
        ob.modifiers.clear()
        me_old = ob.data
        ob.data = mesh_from_eval
        bpy.data.meshes.remove(me_old)
# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
#    REGISTER/UNREGISTER
# ------------------------------------------------------------------------------
classes = (
    CUT_array,
    MCUTTER_OT_restart,
    MCUTTER_OT_target_set,
    MCUTTER_OT_show_target,
    MCUTTER_OT_add_item,
    MCUTTER_OT_remove_item,
    MCUTTER_OT_update,
    MCUTTER_OT_hide_cutters,
    MCUTTER_OT_finalize,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

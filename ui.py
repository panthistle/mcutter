
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

class UIL_item(bpy.types.PropertyGroup):
    """UIL collection item (cutter) properties"""
    name: bpy.props.StringProperty(default = 'name')
    p_name: bpy.props.StringProperty(default = 'p_name')
    uid: bpy.props.IntProperty(default = 0)
    arr_coll: bpy.props.CollectionProperty(type = CUT_array)
    cutter_profile: bpy.props.EnumProperty(
        items = (
        ('Rectangle', 'Rectangle', 'rectangle profile'),
        ('Ellipse', 'Ellipse', 'ellipse profile'),
        ('Wave', 'Wave', 'wave profile'),
        ),
        name = 'Profile',
        description = 'Select profile',
        default = 'Ellipse'
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
        default = 2, min = 1, soft_max = 90
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

class MCUTTER_properties(bpy.types.PropertyGroup):
    """MCutter add-on properties"""
    base_name: bpy.props.StringProperty(default = 'MCutter')
    temps_clear: bpy.props.BoolProperty(
        name = 'Remove Temps', description = 'Remove all temporary objects', 
        default = True
        )
    ul_coll: bpy.props.CollectionProperty(type = UIL_item)
    ul_idx: bpy.props.IntProperty(name = 'MCutter item', default = 0)
    ob_id: bpy.props.IntProperty(default = 0)
    coll_name: bpy.props.StringProperty(default = '')
    copy_setts: bpy.props.BoolProperty(
        name = 'Copy settings', description = 'Copy settings to new cutter', 
        default = True
        )
    target_name: bpy.props.StringProperty(default = '')
    target_apply_scale: bpy.props.BoolProperty(
        name = 'Apply Scale', description = 'Apply Scale', 
        default = True
        )
    target_old_mods_remove: bpy.props.BoolProperty(
        name = 'Remove Modifiers', 
        description = 'Remove existing modifiers. Original is not affected', 
        default = True
        )
    target_bool_effects: bpy.props.BoolProperty(
        name = 'Effects', description = 'Show boolean effects', 
        default = True
        )
    target_wire: bpy.props.BoolProperty(
        name = 'Wire', description = 'Show target edges', 
        default = False
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
# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
#    UI LIST
# ------------------------------------------------------------------------------
class MCUTTER_UL_lst(bpy.types.UIList):
    """UI List"""
    def draw_item(self, context, layout, data, item, icon, active_data, 
                    active_propname, index):
        self.use_filter_show = False
        scene = context.scene
        props = scene.ptmc_props
        t = scene.objects.get(props.target_name)
        coll = scene.collection.children.get(props.coll_name)
        found = False
        for ob in coll.objects:
            if (ob.keys() and ob.get(props.base_name) and 
                (ob[props.base_name] == item.uid) and 
                (ob.type == 'MESH') and (ob is not t)):  
                found = True
                break
        if found:
            layout.prop(item, 'name', text = '', emboss = False, 
                        icon = 'DRIVER_DISTANCE')
        else:
            layout.label(text = item.name, icon = 'QUESTION')
# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
#    UI PANEL
# ------------------------------------------------------------------------------
def state_active(scene, props):
    t = scene.objects.get(props.target_name)
    t_ok = (t is not None) and (t.type == 'MESH')
    c_ok = scene.collection.children.get(props.coll_name)
    return t_ok and c_ok and props.ul_coll

class MCUTTER_PT_ui:
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "MCutter"

class MCUTTER_PT_ui_start(MCUTTER_PT_ui, bpy.types.Panel):
    bl_label = "MCutter 0.1.6"

    @classmethod
    def poll(cls, context):
        return not state_active(context.scene, context.scene.ptmc_props)

    def draw(self, context):
        props = context.scene.ptmc_props
        ctx_ob = context.object 
        check_ok = ((ctx_ob is not None) and (ctx_ob.type == 'MESH') and 
                    (len(ctx_ob.data.polygons) > 0))
        layout = self.layout
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text = f'Source:  {ctx_ob.name}' if check_ok else 
                    'Select mesh object')
        col = layout.column(align = True)
        col.enabled = check_ok
        row = col.row(align = True)
        row.prop(props, 'target_old_mods_remove')
        row.prop(props, 'target_apply_scale')
        col.operator('mcutter.target_set')

class MCUTTER_PT_ui_main(MCUTTER_PT_ui, bpy.types.Panel):
    bl_label = "MCutter 0.1.6"

    @classmethod
    def poll(cls, context):
        return state_active(context.scene, context.scene.ptmc_props)

    def draw(self, context):
        layout = self.layout

class MCUTTER_PT_ui_display(MCUTTER_PT_ui, bpy.types.Panel):
    bl_label = "Display options"
    bl_parent_id = "MCUTTER_PT_ui_main"

    def draw(self, context):
        props = context.scene.ptmc_props
        layout = self.layout
        col = layout.column(align = True)
        row = col.row()         
        row.prop(props, 'target_bool_effects')
        row.prop(props, 'target_wire')
        row = col.row()
        row.operator('mcutter.show_target', text = f'Show  {props.target_name}')
        row = col.row()
        row.operator('mcutter.hide_cutters')
        
class MCUTTER_PT_ui_stack(MCUTTER_PT_ui, bpy.types.Panel):
    bl_label = "Cutter stack"
    bl_parent_id = "MCUTTER_PT_ui_main"

    def draw(self, context):
        props = context.scene.ptmc_props
        layout = self.layout
        col = layout.column(align = True)
        row = col.row()
        row.template_list("MCUTTER_UL_lst", "", props, "ul_coll", props, 
                            "ul_idx", rows = 2, maxrows = 3)
        box = layout.box()
        row = box.row(align = True)
        row.operator('mcutter.add_item', text = 'Add')
        row.operator('mcutter.remove_item', text = 'Remove')
        row = box.row()
        row.prop(props, 'copy_setts')
        
        box = layout.box()
        row = box.row()
        row.operator('mcutter.update')

class MCUTTER_PT_ui_final(MCUTTER_PT_ui, bpy.types.Panel):
    bl_label = "Finalize - Restart"
    bl_parent_id = "MCUTTER_PT_ui_main"

    def draw(self, context):
        layout = self.layout
        props = context.scene.ptmc_props
        row = layout.row()
        row.prop(props, 'temps_clear')
        row = layout.row()
        split = row.split()
        col = split.column()
        col.operator('mcutter.restart')
        col = split.column()  
        col.operator('mcutter.finalize')

class MCUTTER_PT_ui_info(MCUTTER_PT_ui, bpy.types.Panel):
    bl_label = "Cutter summary"
    bl_parent_id = "MCUTTER_PT_ui_main"

    def draw(self, context):
        scene = context.scene
        props = scene.ptmc_props
        ul_item = props.ul_coll[props.ul_idx]
        layout = self.layout
        box = layout.box()
        col = box.column(align = True)
        row = col.row(align = True)
        row.label(text = f'profile: {ul_item.cutter_profile}')
        row = col.row(align = True)
        row.label(text = f'boolean op: {ul_item.cutter_bool_op}')
        row = col.row(align = True)
        row.label(text = f'use frame: {ul_item.frame}')
        row = col.row(align = True)
        row.label(text = f'radial array: {ul_item.radial}')
        amod = False
        for mod in ul_item.arr_coll:
            if mod.count > 1:
                amod = True
                break
        row = col.row(align = True)
        row.label(text = f'modifier array: {amod}')
# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
#    REGISTER/UNREGISTER
# ------------------------------------------------------------------------------
classes = (
    CUT_array,
    UIL_item,
    MCUTTER_properties,
    MCUTTER_UL_lst,
    MCUTTER_PT_ui_start,
    MCUTTER_PT_ui_main,
    MCUTTER_PT_ui_display,
    MCUTTER_PT_ui_stack,
    MCUTTER_PT_ui_final,
    MCUTTER_PT_ui_info
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.ptmc_props = bpy.props.PointerProperty(type = 
                                                            MCUTTER_properties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.ptmc_props
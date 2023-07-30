bl_info = {
    "name": "COD MW2 2022 Autoshade",
    "description": "Auto texture COD MW2 2022 models",
    "author": "Core Janik",
    "version": (0, 4),
    "blender": (3, 5, 0),
    "support": "COMMUNITY",
    "category": "Import",
}

import os
import bpy
import math


# CHANGE THIS 2 PATHS TO THE SHADER.BLEND AND SEMODEL FILE YOU JUST EXPORTED ON YOUR PC
shader_blend = R"F:\Coding\GameShading-Blender\COD\MW2 2022\MW2_Shader.blend"
Path = R"E:\Game Porting\COD MW2 2022\Cat 1\head_mp_cat_iw9_1_1\head_mp_cat_iw9_1_1_LOD0.semodel"

#IMAGE FILEFORMAT
img_format = ".png"

# GLOBAL IMAGE SETTINGS
UseGlobalImages = False
GlobalImagePath = R"E:\Game Porting\COD MW2 2022\CDL\Faze\Away\body_mp_cdl_male_iw9_faze_away\_images"

# CDL SKIN SETTINGS
IsCDLskin = False
# [Red,Green,Blue,Alpha] 
# Color1 = Mask Red, Color2 = Mask Green, Color3 = Mask Blue
AlbedoTint = [0.1,0.1,0.1,1]
Color1 = [1,0,0,1]
Color2 = [1,1,1,1]
Color3 = [1,1,1,1]

with bpy.data.libraries.load(shader_blend) as (data_from, data_to):
    data_to.materials = data_from.materials 
if bpy.data.materials.get("Shader"):
    bpy.data.materials.remove(bpy.data.materials.get("Shader"))
if bpy.data.node_groups.get("COD.001"):
    bpy.data.node_groups.remove(bpy.data.node_groups.get("COD.001"))
if bpy.data.node_groups.get("COD Skin.001"):
    bpy.data.node_groups.remove(bpy.data.node_groups.get("COD Skin.001"))
if bpy.data.node_groups.get("NOG.001"):
    bpy.data.node_groups.remove(bpy.data.node_groups.get("NOG.001"))

def get_image(tex_name, tex_local_path):
    img = bpy.data.images.get(tex_name + img_format)
    if img is None:
        img = bpy.data.images.load(tex_local_path)
    return img

Folder = Path.rsplit("\\", 1)[0] + "\\"
for dirpath, dirnames, filenames in os.walk(Folder):
    for filename in [f for f in filenames if f.endswith(".txt")]:
        print("\n")
        MName = str(filename).split("_images", 1)[0]
        print(MName)
        Path = dirpath + "/" + filename
        if UseGlobalImages:
            img_folder = GlobalImagePath
        else:
            img_folder = dirpath + "/_images/" + filename.rsplit("_", 1)[0]
        
        if bpy.data.materials.get(MName):
            mat = bpy.data.materials.get(MName)
            mat.use_nodes = True
            link = mat.node_tree.links.new
            nodes = mat.node_tree.nodes
            for node in nodes:
                nodes.remove(node) 
            mat.blend_method = "OPAQUE"
            nodes = mat.node_tree.nodes
            
            Output = nodes.new('ShaderNodeOutputMaterial')
            Output.location = (200,325)
            shader = nodes.new("ShaderNodeGroup")
            shader.node_tree = bpy.data.node_groups.get("COD") 
            link(shader.outputs["BSDF"], Output.inputs["Surface"])
            shader.location = (0,300)
            UseDA_1, UseDA_2, UseDA_3, UseDN_1, UseDN_2, UseDN_3 = False, False, False, False, False, False
            
            with open(Path) as f:
                lines = f.readlines()

                lines = list(map(lambda s: s.strip(), lines))
                lines.remove("semantic,image_name")
                for i in range(len(lines)):
                    if lines[i].split(",")[0] == "unk_semantic_0x34":
                        shader.node_tree = bpy.data.node_groups.get("COD Skin") 

                for i in range(len(lines)):
                    if lines[i].split(",")[0] == "unk_semantic_0x0":
                        if lines[i].split(",")[1] == "ximage_3c29eeff15212c37":
                            shader.inputs["Albedo"].default_value = [1,1,1,1]
                            shader.inputs["Albedo Alpha"].default_value = [1,1,1,1]
                        elif lines[i].split(",")[1] == "ximage_4a882744bc523875":
                            shader.inputs["Albedo"].default_value = [0,0,0,1]
                            shader.inputs["Albedo Alpha"].default_value = [1,1,1,1]
                        elif lines[i].split(",")[1] == "ximage_7014a153542e798c":
                            shader.inputs["Albedo"].default_value = [0.017,0.017,0.023,1]
                            shader.inputs["Albedo Alpha"].default_value = [1,1,1,1]
                        elif lines[i].split(",")[1] == "ximage_18b3d69e4258c738":
                            UseDA_1 = True
                        else:
                            if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + img_format):
                                Albedo = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + img_format)
                                tex_image_node: bpy.types.Node
                                tex_image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                                tex_image_node.location = (-500,600)
                                tex_image_node.image = Albedo
                                tex_image_node.label = "Albedo"
                                tex_image_node.image.alpha_mode = "CHANNEL_PACKED"
                                link(tex_image_node.outputs["Color"], shader.inputs["Albedo"])
                                pixel_float = Albedo.size[0] * Albedo.size[1] * 4
                                test_num = (Albedo.size[0] + Albedo.size[1]) / 2 * 32
                                am =int(pixel_float/4/test_num)
                                alpha_px = 3
                                for i in range(am):
                                    if Albedo.pixels[alpha_px] < 0.9999:
                                        link(tex_image_node.outputs["Alpha"], shader.inputs["Albedo Alpha"])
                                        break
                                    alpha_px = alpha_px + int(test_num*4)    
                                shader.inputs["Albedo Alpha"].default_value = [0,0,0,1]
                    elif lines[i].split(",")[0] == "unk_semantic_0x1" and UseDA_1 == True:
                        if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + img_format):
                            Albedo = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + img_format)
                            tex_image_node: bpy.types.Node
                            tex_image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                            tex_image_node.location = (-500,600)
                            tex_image_node.image = Albedo
                            tex_image_node.label = "Albedo"
                            tex_image_node.image.alpha_mode = "CHANNEL_PACKED"
                            link(tex_image_node.outputs["Color"], shader.inputs["Albedo"])
                            pixel_float = Albedo.size[0] * Albedo.size[1] * 4
                            test_num = (Albedo.size[0] + Albedo.size[1]) / 2 * 32
                            am =int(pixel_float/4/test_num)
                            alpha_px = 3
                            for i in range(am):
                                if Albedo.pixels[alpha_px] < 0.9999:
                                    link(tex_image_node.outputs["Alpha"], shader.inputs["Albedo Alpha"])
                                    break
                                alpha_px = alpha_px + int(test_num*4)    
                            shader.inputs["Albedo Alpha"].default_value = [0,0,0,1]
                        else:
                            UseDA_2 = True
                        UseDA_1 = False
                    elif lines[i].split(",")[0] == "unk_semantic_0x4":
                        if lines[i].split(",")[1] == "ximage_3c29eeff15212c37":
                            shader.inputs["NRA"].default_value = [1,1,1,1]
                            shader.inputs["NRA Alpha"].default_value = [1,1,1,1]
                        elif lines[i].split(",")[1] == "ximage_4a882744bc523875":
                            shader.inputs["NRA"].default_value = [0,0,0,1]
                            shader.inputs["NRA Alpha"].default_value = [1,1,1,1]
                        elif lines[i].split(",")[1] == "ximage_5c2d1c3e952cb190":
                            UseDN_1 = True
                        else:
                            if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + img_format):
                                NM = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + img_format)
                                tex_image_node: bpy.types.Node
                                tex_image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                                tex_image_node.location = (-500,300)
                                tex_image_node.image = NM
                                tex_image_node.label = "NOG"
                                tex_image_node.image.alpha_mode = "CHANNEL_PACKED"
                                link(tex_image_node.outputs["Color"], shader.inputs["NRA"])
                                link(tex_image_node.outputs["Alpha"], shader.inputs["NRA Alpha"])
                                tex_image_node.image.colorspace_settings.name = "Non-Color"
                    elif lines[i].split(",")[0] == "unk_semantic_0x5" and UseDN_1 == True:
                        if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + img_format):
                            NM = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + img_format)
                            tex_image_node: bpy.types.Node
                            tex_image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                            tex_image_node.location = (-500,300)
                            tex_image_node.image = NM
                            tex_image_node.label = "NOG"
                            tex_image_node.image.alpha_mode = "CHANNEL_PACKED"
                            link(tex_image_node.outputs["Color"], shader.inputs["NRA"])
                            link(tex_image_node.outputs["Alpha"], shader.inputs["NRA Alpha"])
                            tex_image_node.image.colorspace_settings.name = "Non-Color"
                        else:
                            UseDN_2 = True
                        UseDN_1 = False
                    elif lines[i].split(",")[0] == "unk_semantic_0x8":
                        if "Emission" in shader.inputs:
                            if lines[i].split(",")[1] == "ximage_3c29eeff15212c37":
                                shader.inputs["Emission"].default_value = [1,1,1,1]
                            elif lines[i].split(",")[1] == "ximage_4a882744bc523875":
                                shader.inputs["Emission"].default_value = [0,0,0,1]
                            else:
                                if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + img_format):
                                    Emission = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + img_format)
                                    tex_image_node: bpy.types.Node
                                    tex_image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                                    tex_image_node.location = (-500,0)
                                    tex_image_node.image = Emission
                                    tex_image_node.label = "Emission"
                                    tex_image_node.image.alpha_mode = "CHANNEL_PACKED"
                                    link(tex_image_node.outputs["Color"], shader.inputs["Emission"])
                    elif lines[i].split(",")[0] == "unk_semantic_0xC":
                        if "Alpha" in shader.inputs:
                            if lines[i].split(",")[1] == "ximage_3c29eeff15212c37":
                                shader.inputs["Alpha"].default_value = 1
                            elif lines[i].split(",")[1] == "ximage_4a882744bc523875":
                                shader.inputs["Alpha"].default_value = 0
                                mat.blend_method = "HASHED"
                            else:
                                if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + img_format):
                                    mat.blend_method = "HASHED"
                                    Alpha = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + img_format)
                                    tex_image_node: bpy.types.Node
                                    tex_image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                                    tex_image_node.location = (-500,-300)
                                    tex_image_node.image = Alpha
                                    tex_image_node.label = "Alpha"
                                    tex_image_node.image.alpha_mode = "CHANNEL_PACKED"
                                    link(tex_image_node.outputs["Color"], shader.inputs["Alpha"])
                                    tex_image_node.image.colorspace_settings.name = "Non-Color"
                    elif lines[i].split(",")[0] == "unk_semantic_0x22":
                        if "Transparency" in shader.inputs:
                            if lines[i].split(",")[1] == "ximage_3c29eeff15212c37":
                                shader.inputs["Transparency"].default_value = 1
                                shader.inputs["Use Transparency"].default_value = 1
                                mat.blend_method = "BLEND"
                            elif lines[i].split(",")[1] == "ximage_4a882744bc523875":
                                shader.inputs["Transparency"].default_value = 0
                            else:
                                if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + img_format):
                                    Transparency = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + img_format)
                                    tex_image_node: bpy.types.Node
                                    tex_image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                                    tex_image_node.location = (-500,-600)
                                    tex_image_node.image = Transparency
                                    tex_image_node.label = "Transparency"
                                    tex_image_node.image.alpha_mode = "CHANNEL_PACKED"
                                    shader.inputs["Use Transparency"].default_value = 1
                                    mat.blend_method = "BLEND"
                                    link(tex_image_node.outputs["Color"], shader.inputs["Transparency"])
                    elif lines[i].split(",")[0] == "unk_semantic_0x26":
                        if "Specular" in shader.inputs:
                            if lines[i].split(",")[1] == "ximage_3c29eeff15212c37":
                                shader.inputs["Specular"].default_value = 1
                            elif lines[i].split(",")[1] == "ximage_4a882744bc523875":
                                shader.inputs["Specular"].default_value = 0
                                mat.blend_method = "HASHED"
                            else:
                                if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + img_format):
                                    Spec_Mask = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + img_format)
                                    tex_image_node: bpy.types.Node
                                    tex_image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                                    tex_image_node.location = (-500,-900)
                                    tex_image_node.image = Spec_Mask
                                    tex_image_node.image.alpha_mode = "CHANNEL_PACKED"
                                    tex_image_node.image.colorspace_settings.name = "Non-Color"
                                    link(tex_image_node.outputs["Color"], shader.inputs["Specular"])
                                    tex_image_node.label = "Specular_Mask"
                                    pixel_float = Spec_Mask.size[0] * Spec_Mask.size[1] * 4
                                    test_num = (Spec_Mask.size[0] + Spec_Mask.size[1]) / 2 * 32
                                    am =int(pixel_float/4/test_num)
                                    r_px = 0
                                    SSS = False
                                    for i in range(am):
                                        R = math.floor(Spec_Mask.pixels[r_px] *100)
                                        G = math.floor(Spec_Mask.pixels[r_px + 1] *100)
                                        B = math.floor(Spec_Mask.pixels[r_px + 2] *100)
                                        if B != 0:
                                            SSS = True
                                        if R != G:
                                            mat.node_tree.links.remove(shader.inputs["Specular"].links[0])
                                            if SSS:
                                                link(tex_image_node.outputs["Color"], shader.inputs["SSS"])
                                                link(tex_image_node.outputs["Alpha"], shader.inputs["SSS Alpha"])
                                                tex_image_node.label = "SSS"
                                                tex_image_node.image.colorspace_settings.name = "sRGB"
                                            else:
                                                tex_image_node.label = "0x26"
                                            break
                                        elif B != G:
                                            mat.node_tree.links.remove(shader.inputs["Specular"].links[0])
                                            if SSS:
                                                link(tex_image_node.outputs["Color"], shader.inputs["SSS"])
                                                link(tex_image_node.outputs["Alpha"], shader.inputs["SSS Alpha"])
                                                tex_image_node.label = "SSS"
                                                tex_image_node.image.colorspace_settings.name = "sRGB"
                                            else:
                                                tex_image_node.label = "0x26"
                                            break
                                        elif R != B:
                                            mat.node_tree.links.remove(shader.inputs["Specular"].links[0])
                                            if SSS:
                                                link(tex_image_node.outputs["Color"], shader.inputs["SSS"])
                                                link(tex_image_node.outputs["Alpha"], shader.inputs["SSS Alpha"])
                                                tex_image_node.label = "SSS"
                                                tex_image_node.image.colorspace_settings.name = "sRGB"
                                            else:
                                                tex_image_node.label = "0x26"
                                            break 
                                        r_px = r_px + int(test_num*4)
                    elif lines[i].split(",")[0] == "unk_semantic_0x32":
                        if IsCDLskin:
                            if lines[i].split(",")[1] == "ximage_3c29eeff15212c37":
                                pass
                            elif lines[i].split(",")[1] == "ximage_4a882744bc523875":
                                pass
                            else:
                                if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + img_format):
                                    CDLMask = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + ".png")
                                    tex_image_node: bpy.types.Node
                                    tex_image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                                    tex_image_node.location = (-500,-600)
                                    tex_image_node.image = CDLMask
                                    tex_image_node.label = "CDLMask"
                                    tex_image_node.image.alpha_mode = "CHANNEL_PACKED"
                                    link(tex_image_node.outputs["Color"], shader.inputs["Detail Mask"])
                                    shader.inputs["Albedo Tint"].default_value = AlbedoTint
                                    shader.inputs["Detail Color 3"].default_value = Color3
                                    shader.inputs["Detail Color 2"].default_value = Color2
                                    shader.inputs["Detail Color 1"].default_value = Color1
                                    pixel_float = CDLMask.size[0] * CDLMask.size[1] * 4
                                    test_num = (CDLMask.size[0] + CDLMask.size[1]) / 2 * 64
                                    am =int(pixel_float/4/test_num)
                                    r_px = 0
                                    for i in range(am):
                                        R = math.floor(CDLMask.pixels[r_px] *100)
                                        G = math.floor(CDLMask.pixels[r_px + 1] *100)
                                        B = math.floor(CDLMask.pixels[r_px + 2] *100)
                                        if R == 0:
                                            shader.inputs["Activate Color 1"].default_value = 1
                                        if G == 0:
                                            shader.inputs["Activate Color 2"].default_value = 1
                                        if B == 0:
                                            shader.inputs["Activate Color 3"].default_value = 1
                                        r_px = r_px + int(test_num*4)
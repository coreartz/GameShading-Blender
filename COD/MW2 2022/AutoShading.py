import os
import bpy
import math

# CHANGE THIS 2 PATHS TO THE SHADER.BLEND AND SEMODEL FILE YOU JUST EXPORTED ON YOUR PC
shader_blend = R"D:\Game Porting\COD MW2 2022\MW2_Shader.blend"
Path = R"D:\Game Porting\COD MW2 2022\grave_sp_mwII\head_hero_graves_lod\head_hero_graves_lod_LOD0.semodel"



with bpy.data.libraries.load(shader_blend) as (data_from, data_to):
    data_to.materials = data_from.materials 
if bpy.data.materials.get("Shader"):
    bpy.data.materials.remove(bpy.data.materials.get("Shader"))
if bpy.data.node_groups.get("COD.001"):
    bpy.data.node_groups.remove(bpy.data.node_groups.get("COD.001"))

def get_image(tex_name, tex_local_path):
    img = bpy.data.images.get(tex_name + ".png")
    if img is None:
        img = bpy.data.images.load(tex_local_path)
    return img

Folder = Path.rsplit("\\", 1)[0] + "\\"
for i in os.listdir(Folder):
    if ".txt" in i:
        print("\n")
        MName = str(i).split("_images", 1)[0]
        print(MName)
        Path = Folder + i
        img_folder = Folder + "_images\\" + str(i).rsplit("_", 1)[0]
        
        if bpy.data.materials.get(MName):
            mat = bpy.data.materials.get(MName)
            link = mat.node_tree.links.new
            nodes = mat.node_tree.nodes
            for node in nodes:
                nodes.remove(node) 
            mat.use_nodes = True
            mat.blend_method = "OPAQUE"
            nodes = mat.node_tree.nodes
            
            Output = nodes.new('ShaderNodeOutputMaterial')
            Output.location = (200,325)
            shader = nodes.new("ShaderNodeGroup")
            shader.node_tree = bpy.data.node_groups.get("COD") 
            link(shader.outputs["BSDF"], Output.inputs["Surface"])
            shader.location = (0,300)
            
            with open(Path) as f:
                lines = f.readlines()

                lines = list(map(lambda s: s.strip(), lines))
                lines.remove("semantic,image_name")
                
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
                        else:
                            if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + ".png"):
                                Albedo = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + ".png")
                                print(img_folder + "\\" + lines[i].split(",")[1] + ".png")
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
                    elif lines[i].split(",")[0] == "unk_semantic_0x4":
                        if lines[i].split(",")[1] == "ximage_3c29eeff15212c37":
                            shader.inputs["NRA"].default_value = [1,1,1,1]
                            shader.inputs["NRA Alpha"].default_value = [1,1,1,1]
                        elif lines[i].split(",")[1] == "ximage_4a882744bc523875":
                            shader.inputs["NRA"].default_value = [0,0,0,1]
                            shader.inputs["NRA Alpha"].default_value = [1,1,1,1]
                        else:
                            if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + ".png"):
                                NM = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + ".png")
                                tex_image_node: bpy.types.Node
                                tex_image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                                tex_image_node.location = (-500,300)
                                tex_image_node.image = NM
                                tex_image_node.label = "NOG"
                                tex_image_node.image.alpha_mode = "CHANNEL_PACKED"
                                link(tex_image_node.outputs["Color"], shader.inputs["NRA"])
                                link(tex_image_node.outputs["Alpha"], shader.inputs["NRA Alpha"])
                                tex_image_node.image.colorspace_settings.name = "Non-Color"
                    elif lines[i].split(",")[0] == "unk_semantic_0x8":
                        if lines[i].split(",")[1] == "ximage_3c29eeff15212c37":
                            shader.inputs["Emission"].default_value = [1,1,1,1]
                        elif lines[i].split(",")[1] == "ximage_4a882744bc523875":
                            shader.inputs["Emission"].default_value = [0,0,0,1]
                        else:
                            if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + ".png"):
                                Emission = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + ".png")
                                tex_image_node: bpy.types.Node
                                tex_image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                                tex_image_node.location = (-500,0)
                                tex_image_node.image = Emission
                                tex_image_node.label = "Emission"
                                tex_image_node.image.alpha_mode = "CHANNEL_PACKED"
                                link(tex_image_node.outputs["Color"], shader.inputs["Emission"])
                    elif lines[i].split(",")[0] == "unk_semantic_0xC":
                        if lines[i].split(",")[1] == "ximage_3c29eeff15212c37":
                            shader.inputs["Alpha"].default_value = 1
                        elif lines[i].split(",")[1] == "ximage_4a882744bc523875":
                            shader.inputs["Alpha"].default_value = 0
                            mat.blend_method = "BLEND"
                        else:
                            if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + ".png"):
                                mat.blend_method = "HASHED"
                                Alpha = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + ".png")
                                tex_image_node: bpy.types.Node
                                tex_image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                                tex_image_node.location = (-500,-300)
                                tex_image_node.image = Alpha
                                tex_image_node.label = "Alpha"
                                tex_image_node.image.alpha_mode = "CHANNEL_PACKED"
                                link(tex_image_node.outputs["Color"], shader.inputs["Alpha"])
                                tex_image_node.image.colorspace_settings.name = "Non-Color"
                    elif lines[i].split(",")[0] == "unk_semantic_0x22":
                        if lines[i].split(",")[1] == "ximage_3c29eeff15212c37":
                            shader.inputs["Transparency"].default_value = 1
                        elif lines[i].split(",")[1] == "ximage_4a882744bc523875":
                            shader.inputs["Transparency"].default_value = 0
                        else:
                            if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + ".png"):
                                Transparency = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + ".png")
                                tex_image_node: bpy.types.Node
                                tex_image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                                tex_image_node.location = (-500,-600)
                                tex_image_node.image = Transparency
                                tex_image_node.label = "Transparency"
                                tex_image_node.image.alpha_mode = "CHANNEL_PACKED"
                                link(tex_image_node.outputs["Color"], shader.inputs["Transparency"])
                    elif lines[i].split(",")[0] == "unk_semantic_0x26":
                        if lines[i].split(",")[1] == "ximage_3c29eeff15212c37":
                            shader.inputs["Specular"].default_value = 1
                        elif lines[i].split(",")[1] == "ximage_4a882744bc523875":
                            shader.inputs["Specular"].default_value = 0
                            mat.blend_method = "HASHED"
                        else:
                            if os.path.isfile(img_folder + "\\" + lines[i].split(",")[1] + ".png"):
                                Spec_Mask = get_image(lines[i].split(",")[1], img_folder + "\\" + lines[i].split(",")[1] + ".png")
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
                    elif lines[i].split(",")[0] == "unk_semantic_0x34":
                        shader.node_tree = bpy.data.node_groups.get("COD Skin") 
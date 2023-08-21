import pandas as pd
import numpy as np

class graph:

    def __init__(self, style_name, outStyle):
        # Format of any dictionary:
        # {node_id: property}



        self.outStyle = outStyle


        # Read style base:
        # with open(styleBase, 'r') as style_f:
        #     style_data = style_f.read()
        #last_top = '<dependency name="nodeSizeLocked" value="true"/>\n'
        top_style = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n \
        <vizmap documentVersion="3.0" id="VizMap-2018_03_04-23_32">\n\
        <visualStyle name="{}">\n\
            <network>\n\
                <visualProperty name="NETWORK_CENTER_Y_LOCATION" default="0.0"/>\n\
                <visualProperty name="NETWORK_NODE_SELECTION" default="true"/>\n\
                <visualProperty name="NETWORK_CENTER_Z_LOCATION" default="0.0"/>\n\
                <visualProperty name="NETWORK_SCALE_FACTOR" default="1.0"/>\n\
                <visualProperty name="NETWORK_BACKGROUND_PAINT" default="#FFFFFF"/>\n\
                <visualProperty name="NETWORK_EDGE_SELECTION" default="true"/>\n\
                <visualProperty name="NETWORK_TITLE" default=""/>\n\
                <visualProperty name="NETWORK_HEIGHT" default="400.0"/>\n\
                <visualProperty name="NETWORK_WIDTH" default="550.0"/>\n\
                <visualProperty name="NETWORK_CENTER_X_LOCATION" default="0.0"/>\n\
                <visualProperty name="NETWORK_DEPTH" default="0.0"/>\n\
            </network>\n\
            <node>\n\
                <dependency name="nodeCustomGraphicsSizeSync" value="true"/>\n\
                 <dependency name="nodeSizeLocked" value="true"/>\n'.format(style_name)
        #top_style = style_data.split(last_top)[0]
        self.outString = top_style
        self.bottom = "\t</visualStyle>\n</vizmap>"
        self.edge = False
        self.abundance_dict = {}
        self.type_dict = {} #dimond, ellipse, etc

    def set_graph_dict(self, gml_file):
        # Write graph to dictionary:
        graph_dict = {}
        with open(gml_file, "r") as f_gml:
            node = False
            edge = False

            for line in f_gml.readlines():
                if line == "node [\n":
                    node = True
                elif line == "edge [\n":
                    edge = True
                elif line == "]\n":
                    node = False
                    edge = False

                if node:
                    if "id " in line:
                        id = line.split(" ")[1].strip("\n").strip('"')
                        if id=="634":
                            pass
                            print()
                        graph_dict[id] = {}
                    elif "label " in line:
                        label = line.split(" ")[1].strip("\n").strip('"')
                        graph_dict[id]["label"] = label
                        graph_dict[id]["edges"] = []
                elif edge:
                    if "source " in line:
                        source = line.split(" ")[1].strip("\n").strip('"')
                    elif "target " in line:
                        target = line.split(" ")[1].strip("\n").strip('"')
                    elif "weight " in line:
                        weight = line.split(" ")[1].strip("\n").strip('"')
                        graph_dict[source]["edges"].append(
                            {"target": graph_dict[target]["label"], "weight": weight})
        self.graph_dict = graph_dict

    def set_abundance_dict(self, abundance_file):
        # abundance file in csv format
        taxa_id_dict = self.taxa_id_dict
        ab_df = pd.read_csv(abundance_file, index_col=0)
        taxa_list = list(ab_df.columns)
        ab_dict = {}
        for taxa in taxa_list:
            if taxa in taxa_id_dict.keys():
                value = np.log(ab_df[taxa].mean() + 0.0000001) - np.log(0.0000001) + 10
                ab_dict[taxa] = value

        # renormalize abundance:
        pass
        pass
        self.abundance_dict.update(ab_dict)

    def set_tax_id_dict(self):
        taxa_id_dict = {}
        for id in self.graph_dict.keys():
            taxa_id_dict[self.graph_dict[id]["label"]] = id
        self.taxa_id_dict = taxa_id_dict

    def set_type_dict(self, abundance_file, keyword_type_set={("HMDB","DIAMOND")}):
        ab_df = pd.read_csv(abundance_file, index_col=0)
        taxa_list = list(ab_df.columns)
        type_dict = {}
        for taxa in taxa_list:
            for keypair in keyword_type_set:
                if keypair[0] in taxa:
                    type_dict[taxa] = keypair[1]
        self.type_dict.update(type_dict)



    def add_property_node(self, prop, attribute_dict, default="40"):
        ident = "\t\t\t"
        outString = ident + '<visualProperty name="{}" default="{}">\n'.format(prop, default)
        ident += "\t"
        outString += ident + '<discreteMapping attributeType="string" attributeName="name">\n'
        ident += "\t"
        for taxa in attribute_dict:
            outString += ident + '<discreteMappingEntry value="{}" attributeValue="{}"/>\n'.format(
                attribute_dict[taxa], taxa)

        ident = "\t\t\t\t"
        outString += ident + '</discreteMapping>\n'
        outString += '\t\t\t</visualProperty>\n'.format(prop)
        self.outString+=outString

    def add_node_type(self):
        prop = "NODE_SHAPE"
        self.add_property_node(prop, self.type_dict, default="ELLIPSE")


    def add_node_size(self):
        property="NODE_SIZE"
        self.add_property_node(property, self.abundance_dict)

    def fix_node_label(self):
        # Add metabolite name to HMDB id
        def get_mapping_dict():
            metadata_path = "/Users/stebliankin/Desktop/SabrinaProject/metadata/metabolites_names.txt"

            name_col = 1  # started from 0
            metabolite_col = -1

            map_dict = {}

            with open(metadata_path, 'r') as f:
                f.readline()
                for line in f.readlines():
                    line = line.strip("\n")
                    row = line.split("\t")
                    id = row[metabolite_col]
                    if id != "":
                        map_dict[id] = id + "__" + row[name_col].replace(",", "").replace(" ", "_").replace('"','')
            return map_dict

        property="NODE_LABEL"
        name_dict = get_mapping_dict()
        self.add_property_node(property, name_dict)
        return

    def add_transparency_edge(self):
        return

    def close_node(self):
        self.outString += '\t\t </node>\n'

    def close_edge(self):
        self.outString += '\t\t </edge>\n'

    def write_style(self):
        with open(self.outStyle, 'w') as f:
            f.write(self.outString)
            f.write(self.bottom)


#
# in_gml = "/Users/stebliankin/Desktop/SabrinaProject/PlumaPipline/MultiOmics/results/spearman.multiomics.merged.filtered.users.gml"
# styleBase = "/Users/stebliankin/Desktop/GitProjects/NetworkVisScripts/styleBase.xml"
# outStyle = "/Users/stebliankin/Desktop/SabrinaProject/PlumaPipline/results/multiomicsNetwork/styleMultiomics.xml"
# abundance_file = "/Users/stebliankin/Desktop/SabrinaProject/PlumaPipline/MultiOmics/multiomics.users.csv"
#
#
# #graph_dict = get_graph_dict(in_gml)
#
# G = graph(in_gml, styleBase, outStyle, abundance_file)
# G.add_node_size()
# G.add_node_type({("HMDB", "DIAMOND")})
# G.close_node()
# G.write_style()

#
# Users
#

import PyIO
import PyPluMA

class CreateStylePlugin:
   def input(self, inputfile):
      self.parameters = PyIO.readParameters(inputfile)
      self.in_gml = PyPluMA.prefix()+"/"+self.parameters["in_gml"]
      self.styleName = self.parameters["style_name"]
      self.abundance_file = PyPluMA.prefix()+"/"+self.parameters["abundance_file"]
      self.metabolon_file = PyPluMA.prefix()+"/"+self.parameters["metabolon_file"]
      self.clinical_file = PyPluMA.prefix()+"/"+self.parameters["clinical_file"]

   def run(self):
      pass

   def output(self, outputfile):
      #in_gml = spearmanCorrectedNonUsers.gml"
      #styleName = "users_style1"
      outStyle = outputfile#"styleNonUsers.xml"

      #abundance_file = "abundance_normalized_nonUsers.csv"
      #metabolon_file = "metabolon_norm_nonUsers.csv"
      #clinical_file = "microbiome_average_filtered.csv"

      G = graph(self.styleName, outStyle)
      G.set_graph_dict(self.in_gml)
      G.set_tax_id_dict()
      G.set_abundance_dict(self.abundance_file)
      G.set_abundance_dict(self.metabolon_file)
      G.add_node_size()

      G.set_type_dict(self.metabolon_file,  {("HMDB", "DIAMOND")})
      G.set_type_dict(self.clinical_file,  {("", "TRIANGLE")})
      G.add_node_type()
      G.close_node()
      G.write_style()
#pass
#pass
# G.add_node_size()
# G.add_node_type({("HMDB", "DIAMOND")})
# G.close_node()
# G.fix_node_label()
# G.write_style()

# self.graph_dict = get_graph_dict(in_gml)
# self.taxa_id_dict = map_taxa_id(self.graph_dict)
#
# self.abundance_dict = get_abundance_dict(abundance_file, self.taxa_id_dict)


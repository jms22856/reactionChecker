import csv
import re

from dataclasses import dataclass

import networkx as nx

import logging

from helper.string_parsing import process_reaction_side

from pathlib import Path
import os
import tempfile

LOG_PATH = os.path.join(tempfile.gettempdir(), "calc_nodes.log")

logger = logging.getLogger(__name__)
logging.basicConfig(filename="PAC.log",
                    level=logging.DEBUG,
                    filemode="w")

def setup_logging():
    logging.basicConfig(
        filename="PAC.log",
        level=logging.DEBUG,
        filemode="w",
        format="%(asctime)s  %(levelname)-8s  %(message)s"
    )
@dataclass
class Reaction:
    raw_reaction: str
    LHS: dict[str, int|float]
    RHS: dict[str, int|float]
    catalysts: list[str]

def file_to_raw_reactions(reaction_file: str):
    #First get the file type
    reaction_path = Path(reaction_file)
    reaction_path_suffix = reaction_path.suffix
    file_type = None

    match reaction_path_suffix:
        case ".txt":
            file_type = "text"
        case ".csv":
            file_type = "csv"
        case _:
            file_type = None

    if file_type is None:
        raise ValueError(f"Unrecognized file type of uploaded file {reaction_file}. Make sure that this is a txt or csv file.")


    raw_reactions: list[str] = []
    with open(reaction_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        i=0
        for row in reader:
            i+=1
            if row:
                if row[0].strip():
                    raw_reactions.append(row[0])
                else:
                    logger.info(f"Row {i} is empty and will be ignored.")
            else:
                logger.info(f"Row {i} is empty and will be ignored")

    return raw_reactions

def raw_reactions_to_details(raw_reactions: list[str]):
    all_species: set[str] = set()
    all_cat: set[str] = set()
    all_reactions: list[Reaction] = []

    cat_pattern = r"=\(([^)]*)\)"

    for (i, raw_reaction) in enumerate(raw_reactions, start=1):
        raw_reaction = raw_reaction.strip()
        cat_matches = re.findall(cat_pattern, raw_reaction)
        cat_list = []

        if len(cat_matches) > 1:
            logger.error(f"(Reaction index {i}) Multiple =(...) catalysts detected in reaction: {raw_reaction}. This reaction will be ignored.")
            continue
        elif len(cat_matches) == 1:
            re_cat = cat_matches[0]

            cat_list = [cat.strip() for cat in cat_matches[0].split(",")]

            raw_no_cat = re.sub(cat_pattern, "", raw_reaction)
        else:
            raw_no_cat = raw_reaction

        all_cat.update(cat_list)

        reaction_sides = raw_no_cat.split("=")
        if len(reaction_sides) != 2:
            logger.error(f"(Reaction Number {i}) Reaction {raw_reaction} does not have one equal sign after cat removal. This reaction will be ignored.")
            continue
        LHS = reaction_sides[0]
        RHS = reaction_sides[1]
        
        LHS_terms = process_reaction_side(LHS, apply_multiplication=False, truncate_digits=3, reaction_index=i)
        RHS_terms = process_reaction_side(RHS, apply_multiplication=False, truncate_digits=3, reaction_index=i)

        all_species.update(LHS_terms.keys())
        all_species.update(RHS_terms.keys())

        all_reactions.append(Reaction(
            raw_reaction=raw_reaction,
            LHS=LHS_terms,
            RHS=RHS_terms,
            catalysts=cat_list
        ))

    return all_species, all_cat, all_reactions

def graph_analysis(all_species: set[str], all_cat: set[str], all_reactions: list[Reaction]):
    G = nx.DiGraph()
    G.add_nodes_from(all_species)
    G.add_nodes_from(all_cat)

    for reaction in all_reactions:
        substrate_set = set(reaction.LHS.keys())
        recipient_set = set(reaction.LHS.keys()).union(set(reaction.RHS.keys()))

        sr_edges = []

        for s in substrate_set:
            for r in recipient_set:
                if s != r:
                    if s in G and r in G:
                        G.add_edge(s, r, label=f"{reaction.raw_reaction}")
                    else:
                        if s not in G:
                            raise KeyError(f"{s} not in G, contact the developer.")
                        if r not in G:
                            raise KeyError(f"{r} not in G, contact the developer.")
                        
                        

        catalyst_set = set(reaction.catalysts)
        for c in catalyst_set:
            for r in recipient_set:
                if c != r:
                    if c in G and r in G:
                        G.add_edge(c, r, label=f"{reaction.raw_reaction}")
                    else:
                        if c not in G:
                            raise ValueError(f"{c} not in G, contact the developer.")
                        else:
                            raise ValueError(f"{r} not in G, contact the developer.")
                    
    isolated = []
    no_incoming = []
    no_outgoing = []

    node_colors: list[str] = []
    for n in G.nodes:
        indeg = G.in_degree(n)
        outdeg = G.out_degree(n)
        if indeg == 0 and outdeg == 0:
            isolated.append(n)
            G.nodes[n]["color"] = "gray"
        elif indeg == 0:
            no_incoming.append(n)
            G.nodes[n]["color"] = "red"
        elif outdeg == 0:
            no_outgoing.append(n)
            G.nodes[n]["color"] = "green"
        else:
            G.nodes[n]["color"] = "lightblue"

    return no_incoming, no_outgoing, isolated

def calc_nodes(fp: str):
    main_raw_reactions = file_to_raw_reactions(fp)
    main_species, main_cat, main_reactions = raw_reactions_to_details(main_raw_reactions)
    no_inc, no_out, iso = graph_analysis(main_species, main_cat, main_reactions)
    return_text = f"""
    Species without incoming influence:
    {no_inc}
    Species without outgoing influence:
    {no_out}
    Species without incoming or outgoing:
    {iso}
    """
    return return_text

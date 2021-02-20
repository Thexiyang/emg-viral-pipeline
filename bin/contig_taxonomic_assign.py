#!/usr/bin/env python3

import argparse
import csv
import glob
import operator
import os
import re
import sys
from collections import Counter

import pandas as pd
from ete3 import NCBITaxa


def contig_tax(annot_df, ncbi_db, min_prot, prop_annot, tax_thres):
    """This function takes the annotation table generated by viral_contig_maps.py and generates a table that
    provides the taxonomic lineage of each viral contig, based on the corresponding ViPhOG annotations"""

    ncbi = NCBITaxa(dbfile=ncbi_db)
    tax_rank_order = ["genus", "subfamily", "family", "order"]
    contig_set = set(annot_df["Contig"])

    for contig in contig_set:
        contig_lineage = [contig]
        contig_df = annot_df[annot_df["Contig"] == contig]
        total_prot = len(contig_df)
        annot_prot = sum(contig_df["Best_hit"] != "No hit")
        if annot_prot < prop_annot * total_prot:
            contig_lineage.extend([""] * 4)
        else:
            contig_hits = contig_df[pd.notnull(contig_df["Label"])]["Label"].values
            taxid_list = [
                ncbi.get_name_translator([item])[item][0] for item in contig_hits
            ]
            hit_lineages = [
                {
                    y: x
                    for x, y in ncbi.get_rank(ncbi.get_lineage(item)).items()
                    if y in tax_rank_order
                }
                for item in taxid_list
            ]
            for rank in tax_rank_order:
                taxon_list = [item.get(rank) for item in hit_lineages]
                total_hits = sum(pd.notnull(taxon_list))
                if total_hits < min_prot:
                    contig_lineage.append("")
                    continue
                else:
                    count_hits = Counter(
                        [item for item in taxon_list if pd.notnull(item)]
                    )
                    best_hit = sorted(
                        [(x, y) for x, y in count_hits.items()],
                        key=lambda x: x[1],
                        reverse=True,
                    )[0]
                    prop_hits = best_hit[1] / total_hits
                    if prop_hits < tax_thres:
                        contig_lineage.append(prop_hits)
                        continue
                    else:
                        best_lineage = ncbi.get_lineage(best_hit[0])
                        contig_lineage.extend(
                            [
                                ncbi.get_taxid_translator([key])[key]
                                if pd.notnull(key)
                                else ""
                                for key in [
                                    {
                                        y: x
                                        for x, y in ncbi.get_rank(best_lineage).items()
                                    }.get(item)
                                    for item in tax_rank_order[
                                        tax_rank_order.index(rank) :
                                    ]
                                ]
                            ]
                        )
                        break
        yield contig_lineage


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Generate tabular file with taxonomic assignment of viral contigs based on ViPhOG annotations"
    )
    parser.add_argument(
        "-d",
        "--db",
        dest="ncbi_db",
        help="path to the ete3 processed NCBI taxonomy db.",
    )
    parser.add_argument(
        "-i",
        "--input",
        dest="input_file",
        help="Annotation table generated with script viral_contig_maps.py",
        required=True,
    )
    parser.add_argument(
        "--minprot",
        dest="min_prot",
        type=int,
        help="Minimum number of proteins with ViPhOG annotations at each taxonomic level, required for taxonomic assignment (default: 2)",
        default=2,
    )
    parser.add_argument(
        "--prop",
        dest="prot_prop",
        type=float,
        help="Minimum proportion of proteins in a contig that must have a ViPhOG annotation in order to provide a taxonomic assignment (default: 0.1)",
        default=0.1,
    )
    parser.add_argument(
        "--taxthres",
        dest="tax_thres",
        type=float,
        help="Minimum proportion of annotated genes required for taxonomic assignment (default: 0.6)",
        default=0.6,
    )
    parser.add_argument(
        "-o",
        "--outdir",
        dest="outdir",
        help="Relative path to directory where you want the output file to be stored (default: cwd)",
        default=".",
    )
    args = parser.parse_args()
    input_df = pd.read_csv(args.input_file, sep="\t")
    file_header = ["contig_ID", "genus", "subfamily", "family", "order"]
    output_gen = contig_tax(
        input_df, args.ncbi_db, args.min_prot, args.prot_prop, args.tax_thres
    )
    print(args.input_file)

    out_file = re.split(r"\.[a-z]+$", os.path.basename(args.input_file))[0]

    with open(
        os.path.join(args.outdir, out_file + "_taxonomy.tsv"), "w", newline=""
    ) as output_file:
        tsv_writer = csv.writer(output_file, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        tsv_writer.writerow(file_header)
        for item in output_gen:
            tsv_writer.writerow(item)

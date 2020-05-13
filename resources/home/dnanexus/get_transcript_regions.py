#!/usr/bin/python2

import argparse
from collections import defaultdict
import gzip
import sys


def parse_exons(reg2transcript_file):
    """ Parse through the exons of nirvana 2.0.3 
    
    Returns dict of dict of dict:
    {
        refseq: {
            "position": {
                chrom: [
                    (start1, end1, exon_nb1),
                    (start2, end2, exon_nb2)
                ]
            }
        }
    }
    """

    exons = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    with open(reg2transcript_file) as f:
        for line in f:
            chrom, start, end, gene_symbol, refseq, exon_nb = line.strip().split()
            exons[refseq]["position"][chrom].append((start, end, exon_nb))

    return exons


def parse_coverage_file(coverage_file):
    """ Parse coverage file

    Returns dict:
    {
        chrom: [
            (start, end),
            (start, end),
        ]
    }
    """

    cov_data = {}

    with gzip.open(coverage_file, "rb") as f:
        for line in f:
            line = line.decode().strip("\n")

            if not line.startswith("#"):
                (chrom, start, end) = line.split("\t")[0:3]
                cov_data.setdefault(chrom, []).append((start, end))

    return cov_data        


def main(transcripts, cov_file, exon_file):
    """ Print the exons of given transcripts in a perl hash format

    Returns exons_covered
    """

    exons_covered = []

    exons_data = parse_exons(exon_file)
    coverage_data = parse_coverage_file(cov_file)

    for transcript in transcripts:
        if transcript in exons_data:
            for chrom, exons in exons_data[transcript]["position"].items():
                for exon in exons:
                    exon_start, exon_end, exon_nb = exon

                    for region in coverage_data[chrom]:
                        region_start, region_end = region

                        if (exon_start <= region_end and exon_end >= region_start):
                            data = {
                                "refseq": transcript,
                                "region": {
                                   "chrom": chrom,
                                   "start": exon_start,
                                   "end": exon_end
                                },
                                "exon_nr": exon_nb
                            }
                            exons_covered.append(data)

    print("(")
    for exon in exons_covered:
        print("\t{")

        for field, val in exon.items():
            if field == "region":
                print("\tregion=>{")

                for pos_field, pos_data in val.items():
                    print("\t\t\t{}=>\"{}\",".format(pos_field, pos_data))

                print("\t\t}")
            else:
                print("\t{}=>\"{}\",".format(field, val))

        print("\t},")

    print(")")

    return exons_covered



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Get the region coverage data from ref bed and transcripts")

    parser.add_argument("-c", "--coverage", help="Coverage file from region_coverage.py")
    parser.add_argument("-t", "--transcripts", nargs="+", help="Transcript(s) to define regions")
    parser.add_argument("-e", "--exon_file", help="Dump of nirvana GFF with all exons")

    args = parser.parse_args()

    transcripts = args.transcripts
    coverage_file = args.coverage
    exon_file = args.exon_file

    main(transcripts, coverage_file, exon_file)

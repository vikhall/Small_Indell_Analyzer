import find_mutation
from Bio import pairwise2
from Bio.pairwise2 import format_alignment
import os


def write_2_fastq(
        ref_seq, lines, resdir, spec_mut='',
        align_qual_threshold=0, alt_allele=None) -> None:
    """
    Эта функция производит поиск мутаций, внесенных эндонуклеазой Cas
    :param ref_seq: The reference sequence to which the reads were aligned
    :param lines: List with the lines of input file
    :param resdir: The directory where the results will be outputted
    :param align_qual_threshold: The threshold for the quality of alignments. Only alignments with a score higher than
    this value will be used to search for mutations.
    :param alt_allele: Alternative allele. If specified, the mutation search will be performed separately
    in the readings containing this allele
    :param spec_mut: Special mutation of interest. Reads with this mutation will be saved in separate file
    :return: None
    """
    #
    spec_mutations = spec_mut.split(',')
    spec_mutations_dict = {}
    #
    region_start = ref_seq[:5]
    region_end = ref_seq[-5:]
    #
    bad_reads, ideal_reads, mut_reads = [], [], []
    for line_list in lines:
        n = 0
        for c in range(len(line_list)):
            if line_list[c].startswith('@'):
                n = 1
                continue
            elif line_list[c].startswith('+'):
                n = 0
            if n == 1:
                seq = line_list[c].strip()
                #
                pam_end = seq.rfind(region_end)
                if pam_end != -1:
                    pam_start = seq.find(region_start)
                    #
                    if pam_start > 0:
                        modified_region = seq[pam_start:pam_end] + region_end
                        #
                        alignment = pairwise2.align.globalms(ref_seq, modified_region, 2, -1, -2, -1)
                        align_formated = format_alignment(*alignment[0])
                        #
                        ref_seq = align_formated.split('\n')[0]
                        ref_seq_wo_gaps = ref_seq.replace('-', '')
                        mod_seq = align_formated.split('\n')[2]
                        mod_seq_wo_gaps = mod_seq.replace('-', '')
                        score = int(align_formated.split('\n')[3].split('=')[1].strip())
                        #
                        if score > align_qual_threshold:
                            mutation_list, mutation_list_alt = [], []
                            mut_seq_dict, mut_seq_dict_alt = {}, {}

                            find_mutation.find_mutation(
                                mod_seq, mod_seq_wo_gaps, ref_seq, ref_seq_wo_gaps,
                                alt_allele, mutation_list, mutation_list_alt, region_end, mut_seq_dict,
                                mut_seq_dict_alt
                            )

                            if not mutation_list:
                                ideal_reads.append(line_list[c - 1:c + 3])
                            else:
                                mut_reads.append(line_list[c - 1:c + 3])
                                for m in spec_mutations:
                                    if m in mutation_list:
                                        if m not in spec_mutations_dict:
                                            spec_mutations_dict[m] = [line_list[c - 1:c + 3]]
                                        else:
                                            spec_mutations_dict[m].append(line_list[c - 1:c + 3])
                        else:
                            bad_reads.append(line_list[c-1:c+2])

        with open(os.path.join(resdir, 'Not_Aligned_Reads.fastq'), 'w') as notaligned:
            notaligned.write(''.join(['\n'.join(ele) for ele in bad_reads]))
        with open(os.path.join(resdir, 'Perfect_Aligned_Reads.fastq'), 'w') as perfect:
            perfect.write(''.join(['\n'.join(ele) for ele in ideal_reads]))
        with open(os.path.join(resdir, 'Mutated_Reads.fastq'), 'w') as mutated:
            mutated.write(''.join(['\n'.join(ele) for ele in mut_reads]))

        if spec_mutations_dict:
            for key in spec_mutations_dict:
                with open(os.path.join(resdir, key), 'w') as outfile:
                    outfile.write('\n'.join(['\n'.join(ele) for ele in spec_mutations_dict[key]]))

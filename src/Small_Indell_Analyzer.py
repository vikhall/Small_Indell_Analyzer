# -*- coding: utf-8 -*-
import xlwt
import argparse
import os
import get_indels
import filter_indels
import write_2_fastq


def main() -> None:
    """
    Выполняет запуск скрипта
    :return: None
    """
    # Парсинг аргументов
    parser = argparse.ArgumentParser()
    parser.add_argument("ref_seq", type=str, help='Reference sequence to which all reads will be aligned. '
                        'Might be string containing only A,T,G,C letters (in AnY cASe) or path to the fasta-file')
    parser.add_argument("case", type=str, help='Fastq file with case reads')
    parser.add_argument("control", type=str, help='Fastq file with control reads')
    parser.add_argument("pam", type=str, help='PAM sequence. This sequence is necessary for the correct '
                        'numbering of mutations')
    parser.add_argument("pam_orient", type=str, help='Orientation of the PAM in the reference sequence. '
                        'It can be "left" if mutations are located to the right of the pam sequence, '
                        'or "right" if mutations are located to the left of the pam sequence '
                        'Example: R/right/Right or L/left/Left')
    parser.add_argument("-w", "--workdir", type=str, help='Working directory with fastq files. '
                        'By default, all input files will be searched in this directory '
                        '(if only filenames without path given). '
                        'Default: directory with this script')
    parser.add_argument("-o", "--resdir", type=str, help='Directory to which results will be saved '
                        'If --resdir==workdir, directory will not be created and results will be saved in current '
                        'working directory. If only name of the directory given, the directory will be created '
                        'in working directory. If path/to/directory given, the directory will be created in this path. '
                        'If resdit not exist, it will be created. Default: Results',
                        default='Results')
    parser.add_argument("-e", "--excel_file", type=str, help='Excel file with main result. '
                        'If only name of the file given, '
                        'file with report will be created in workdir. If path to the file given, '
                        'report will be written in this file (file will be created if not exist (otherwise, file '
                        'will be overwritten)). Default: '
                        'Mutations_+{Name of the control file}.xls',
                        default='defolt')
    parser.add_argument("-b", "--bad_align_file", type=str, help='File with bad alignments '
                        '(with score < align_qual_threshold). Default: None')
    parser.add_argument("-r", "--report_file", type=str, help='File with brief report. If only name of the file given, '
                        'file with report will be created in workdir. If path to the file given, '
                        'report will be written in this file (file will be created if not exist (otherwise, report '
                        'will be written in the end of the existing file)).Default: '
                        'Report_+{Name of the control file}.txt',
                        default='defolt')
    parser.add_argument("-t", "--align_qual_threshold", type=int, help='The threshold for the quality of alignments. '
                        'Only alignments with a score higher than this value will be used to search for mutations. '
                        'Default: 0',
                        default=0)
    parser.add_argument("-с", "--count_threshold", type=int, help='Threshold of mutation frequency. '
                        'Only mutations with a frequency higher than this value will be saved after filtering '
                        'Default: 3', default=3)
    parser.add_argument("-a", "--alt_allele", type=str, help='Short unique sequence containing alternative allele. '
                        'If given, the mutation search will be performed separately in the reads containing this allele'
                        '. Must be short unique substring of the ref_seq, containing SNP. '
                        'Example: "ATGCA", where G is SNP of interest. Nucleotides around G is needed to found '
                        'this substring in ref_seq. Default: None')
    parser.add_argument("-f", "--write_fastq", type=str, help='If given (any string: yes/true etc), '
                        'three groups of reads will be written in resdir: aligned reads without mutations, '
                        'aligned reads with mutations and not aligned reads (with score < align_qual_threshold). '
                        'Default: None')
    parser.add_argument('-m', '--mutation_to_write', type=str, help='If given, reads with this mutation '
                        'will be written in fastq-files. Example: "--mutation_to_write=single_del_6". Default: None.')

    args = parser.parse_args()

    # Работа с директориями

    # Если в качестве пути передано слово, папка создастся в Workdir.
    # Если передан путь, папка будет создана по этому пути
    # Если передано слово workdir, папка создана не будет
    if args.resdir.lower() == 'workdir':
        res_path = args.workdir
    elif len(args.resdir.split(os.path.sep)) == 1:
        res_path = os.path.join(args.workdir, args.resdir)
    else:
        res_path = args.resdir
    # Если такой папки нет, она создастся. Если такая папка есть, результаты будут сохранены в нее
    if not os.path.exists(res_path):
        os.mkdir(res_path)

    # Если в качестве образца передан путь, то в функцию будет передан путь.
    # Если название файла, то путь будет объединен с workdir
    if len(args.case.split(os.path.sep)) == 1:
        case_path = os.path.join(args.workdir, args.case)
    else:
        case_path = args.case
    if len(args.control.split(os.path.sep)) == 1:
        control_path = os.path.join(args.workdir, args.control)
    else:
        control_path = args.control

    # Может быть считана последовательность напрямую, или из fasta-файла
    if all(i.upper() in 'ATGC' for i in args.ref_seq):
        reference_seq = args.ref_seq
    else:
        if len(args.ref_seq.split(os.path.sep)) == 1:
            ref_seq_path = os.path.join(args.workdir, args.ref_seq)
        else:
            ref_seq_path = args.ref_seq
        with open(ref_seq_path) as inf:
            reference_seq = ''
            for line in inf:
                if line.startswith('>'):
                    continue
                reference_seq += line.strip()

    # Если название выходных файлов дефолтное, к ним будут добавлено название файла с опытными образцами
    if args.excel_file == 'defolt':
        excel_file = f'Mutations_{args.case.split(".")[0]}.xls'
    else:
        excel_file = args.excel_file
    if args.report_file == 'defolt':
        report_file = f'Report_{args.case.split(".")[0]}.txt'
    else:
        report_file = args.report_file

    wb = xlwt.Workbook()
    muts, lines = get_indels.get_indels(
        ref_seq=reference_seq,
        case=case_path,
        control=control_path,
        pam=args.pam,
        pam_orient=args.pam_orient,
        resdir=res_path,
        excel_out_name=excel_file,
        bad_align_file=args.bad_align_file,
        report_file=report_file,
        align_qual_threshold=args.align_qual_threshold,
        alt_allele=args.alt_allele,
        write2fastq=args.write_fastq,
        wb=wb  # Служебный аргумент
    )

    filter_indels.filter_indels(
        wb,
        muts,
        count_threshold=args.count_threshold,
        alt_allele=args.alt_allele
    )

    if args.write_fastq:
        write_2_fastq.write_2_fastq(
            ref_seq=reference_seq,
            lines=lines,
            resdir=res_path,
            align_qual_threshold=args.align_qual_threshold,
            alt_allele=args.alt_allele,
            spec_mut=args.mutation_to_write
        )

    wb.save(os.path.join(res_path, excel_file))


if __name__ == '__main__':
    main()

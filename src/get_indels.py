from Bio import pairwise2
from Bio.pairwise2 import format_alignment
import os
import find_mutation

def get_indels(
        ref_seq, case, control, wb, resdir, pam, pam_orient,
        align_qual_threshold=0, alt_allele=None,
        excel_out_name='Mutations.xls', bad_align_file=None, report_file='Report.txt', write2fastq=False) -> tuple:
    """
    Эта функция производит поиск мутаций, внесенных эндонуклеазой Cas
    :param ref_seq: The reference sequence to which the reads are aligned
    :param case: Path to the fastq file with case sample
    :param control: Path to the file with control sample
    :param resdir: The directory where the results will be outputted
    :param pam: PAM sequence. This sequence is necessary for the correct numbering of mutations
    :param pam_orient: Orientation of the PAM in the reference sequence.
    It can be left if mutations are located to the right of the pam sequence,
    or right if mutations are located to the left of the pam sequence
    :param align_qual_threshold: The threshold for the quality of alignments. Only alignments with a score higher than
    this value will be used to search for mutations.
    :param alt_allele: Alternative allele. If specified, the mutation search will be performed separately
    in the readings containing this allele
    :param excel_out_name: The name of the out Excel file
    :param bad_align_file: The name of the out file with bad alignments
    :param report_file: The name of the out file with brief report
    :param wb: xlwt workbook object
    :param write2fastq: If set to True, all lines of the input fastq-file will be saved in list
    :return: all_mutation_list, all_lines_list: list with mutations and list with lines of input file
    (if write2fastq == True)
    """

    region_start = ref_seq[:5]
    region_end = ref_seq[-5:]

    all_mutation_list = []
    all_lines, all_lines_list = [], []
    for reads in [control, case]:

        # Получение последовательностей прочтений из fastq файла
        seq_list = []
        with open(reads) as infile:
            n = 0
            for line in infile:
                if write2fastq:  # Если нужно будет записывать fastq-файлы, все строки будут сохранены в список
                    all_lines.append(line.strip())
                if line.startswith('@'):
                    n = 1
                    continue
                elif line.startswith('+'):
                    n = 0
                if n == 1:
                    sequence = line.strip()
                    seq_list.append(sequence)
            all_lines_list.append(all_lines)

        # Получение последовательности модифицированного региона (от ref_seq[:5] до ref_seq[-5:])
        modified_region_list = []
        for seq in seq_list:
            pam_end = seq.rfind(region_end)
            if pam_end != -1:
                pam_start = seq.find(region_start)
                if pam_start != -1:
                    modified_region = seq[pam_start:pam_end] + region_end
                    modified_region_list.append(modified_region)

        # Выравнивание последовательности референса и модифицированного региона
        align_formated_list = []
        for region in modified_region_list:
            alignment = pairwise2.align.globalms(ref_seq, region, 2, -1, -2, -1)
            align_formated = format_alignment(*alignment[0])
            align_formated_list.append(align_formated)

        # Вытаскивание инделов из выравниваний
        c = 0
        mutation_list, mutation_list_alt = [], []
        mut_seq_dict, mut_seq_dict_alt = {}, {}
        bad_align_list = []
        for align in align_formated_list:
            ref_seq = align.split('\n')[0]
            ref_seq_wo_gaps = ref_seq.replace('-', '')
            mod_seq = align.split('\n')[2]
            mod_seq_wo_gaps = mod_seq.replace('-', '')
            score = int(align.split('\n')[3].split('=')[1].strip())

            if score > align_qual_threshold:
                c += 1

                find_mutation.find_mutation(
                    mod_seq, mod_seq_wo_gaps, ref_seq, ref_seq_wo_gaps, pam, pam_orient,
                    alt_allele, mutation_list, mutation_list_alt, mut_seq_dict, mut_seq_dict_alt
                )

            # Запись в отдельный список выравниваний с большими инделами
            if score < 40:
                bad_align_list.append(align)

        # Обработка делеций и создание словарей
        uniq_mutation_list = list(set(mutation_list))
        uniq_mutation_list_alt = list(set(mutation_list_alt))
        uniq_mutation_dict, uniq_mutation_dict_alt,  = {}, {}
        uniq_mutation_rate, uniq_mutation_rate_alt,  = {}, {}
        for u in uniq_mutation_list:
            uniq_mutation_dict[u] = mutation_list.count(u)
            uniq_mutation_rate[u] = mutation_list.count(u) / c
        for u in mutation_list_alt:
            uniq_mutation_dict_alt[u] = mutation_list_alt.count(u)
            uniq_mutation_rate_alt[u] = mutation_list_alt.count(u) / c

        all_mutation_list.append(mutation_list)
        all_mutation_list.append(mutation_list_alt)
        all_mutation_list.append(uniq_mutation_list)
        all_mutation_list.append(uniq_mutation_list_alt)
        all_mutation_list.append(uniq_mutation_dict)
        all_mutation_list.append(uniq_mutation_dict_alt)
        all_mutation_list.append(uniq_mutation_rate)
        all_mutation_list.append(uniq_mutation_rate_alt)
        all_mutation_list.append(mut_seq_dict)
        all_mutation_list.append(mut_seq_dict_alt)

        # Запись информации о мутациях в файл
        # Запись в файл excel
        sheetname = reads.split('.')[0].split(os.path.sep)[-1]
        wb = wb
        ws = wb.add_sheet(sheetname)
        ws.write(0, 0, 'Mutation')
        ws.write(0, 1, 'Total count')
        ws.write(0, 2, 'Total rate')
        if not alt_allele:
            ws.write(0, 3, 'Sequence')
        else:
            ws.write(0, 3, 'Alt allele count')
            ws.write(0, 4, 'Alt allele rate')
            ws.write(0, 5, 'Sequence')

        for i in range(len(uniq_mutation_list)):
            ws.write(i + 1, 0, uniq_mutation_list[i])
            ws.write(i + 1, 1, uniq_mutation_dict[uniq_mutation_list[i]])
            ws.write(i + 1, 2, uniq_mutation_rate[uniq_mutation_list[i]])
            if not alt_allele:
                ws.write(i + 1, 3, mut_seq_dict[uniq_mutation_list[i]])

            if alt_allele:
                if uniq_mutation_list[i] in uniq_mutation_dict_alt:
                    ws.write(i + 1, 3, uniq_mutation_dict_alt[uniq_mutation_list[i]])
                else:
                    ws.write(i + 1, 3, 0)
                if uniq_mutation_list[i] in uniq_mutation_rate_alt:
                    ws.write(i + 1, 4, uniq_mutation_rate_alt[uniq_mutation_list[i]])
                else:
                    ws.write(i + 1, 4, 0)
                ws.write(i + 1, 5, mut_seq_dict[uniq_mutation_list[i]] if uniq_mutation_list[i] in mut_seq_dict else '')

        # Запись отчета
        if report_file:
            with open(os.path.join(resdir, report_file), 'a') as report:
                report.write(f'Всего было проанализировано {len(seq_list)} прочтений в файле {reads}' + '\n')
                report.write(
                    f'Из них {len(modified_region_list)} ({(len(modified_region_list) / len(seq_list)) * 100}%) '
                    f'имеют участок для редактирования, содержащий PAM' + '\n')
                report.write(
                    f'Из них {c} ({(c / len(modified_region_list)) * 100}%) имеют хорошее выравнивание '
                    f'(score > {align_qual_threshold})' + '\n')
                report.write(
                    f'Всего было обнаружено {len(mutation_list)} мутаций (indel)' + '\n' + '\n')
                report.write(
                    f'Подробная информация о мутациях представлена в файле {excel_out_name} '
                    f'на странице {sheetname}' + '\n' + '\n')

        # Запись файла с плохими выравниваниями
        if bad_align_file:
            with open(os.path.join(resdir, bad_align_file), 'w') as outfile:
                outfile.write('\n'.join(bad_align_list))

    return all_mutation_list, all_lines_list

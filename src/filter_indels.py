def filter_indels(wb, all_mutation_list: list, count_threshold: int = 2, alt_allele=None) -> None:
    """
    Функция, которая фильтрует найденные мутации и записывает в файл только частые мутации (>count_threshold)
    :param wb: xlwt workbook object
    :param all_mutation_list: list with mutations from get_indels function
    :param count_threshold: Threshold of mutation frequency. Only mutations with a frequency higher than this value
    will be saved after filtering
    :param alt_allele: Alternative allele. If specified, the mutation search will be performed separately
    in the readings containing this allele
    :return: None
    """

    all_mutations = list(set((all_mutation_list[2] + all_mutation_list[12])))
    all_mutations_dict = {}
    for mutation in all_mutations:
        mut_control_count = all_mutation_list[4][mutation] if mutation in all_mutation_list[4] else 0
        mut_control_count_alt = all_mutation_list[5][mutation] if mutation in all_mutation_list[5] else 0
        mut_control_rate = all_mutation_list[6][mutation] if mutation in all_mutation_list[6] else 0
        mut_control_rate_alt = all_mutation_list[7][mutation] if mutation in all_mutation_list[7] else 0
        mut_control_seq = all_mutation_list[8][mutation] if mutation in all_mutation_list[8] else ''
        mut_control_seq_alt = all_mutation_list[9][mutation] if mutation in all_mutation_list[9] else ''
        mut_case_count = all_mutation_list[14][mutation] if mutation in all_mutation_list[14] else 0
        mut_case_count_alt = all_mutation_list[15][mutation] if mutation in all_mutation_list[15] else 0
        mut_case_rate = all_mutation_list[16][mutation] if mutation in all_mutation_list[16] else 0
        mut_case_rate_alt = all_mutation_list[17][mutation] if mutation in all_mutation_list[17] else 0
        mut_case_seq = all_mutation_list[18][mutation] if mutation in all_mutation_list[18] else ''
        mut_case_seq_alt = all_mutation_list[19][mutation] if mutation in all_mutation_list[19] else ''

        all_mutations_dict[mutation] = [mut_control_count, mut_control_rate, mut_control_seq,
                                        mut_control_count_alt, mut_control_rate_alt, mut_control_seq_alt,
                                        mut_case_count, mut_case_rate, mut_case_seq,
                                        mut_case_count_alt, mut_case_rate_alt, mut_case_seq_alt]

    sheetname = 'Mutations_filtered'
    ws = wb.add_sheet(sheetname)

    if alt_allele:
        ws.write(0, 1, 'Control total')
        ws.write(0, 2, 'Control total rate')
        ws.write(0, 3, 'Control total alt')
        ws.write(0, 4, 'Control total alt rate')
        ws.write(0, 5, 'Case total')
        ws.write(0, 6, 'Case total rate')
        ws.write(0, 7, 'Case total alt')
        ws.write(0, 8, 'Case total alt rate')
        ws.write(0, 9, 'Sequence')

    else:
        ws.write(0, 1, 'Control total')
        ws.write(0, 2, 'Control total rate')
        ws.write(0, 3, 'Case total')
        ws.write(0, 4, 'Case total rate')
        ws.write(0, 5, 'Sequence')

    j = 0
    for i in all_mutations_dict:
        if alt_allele:
            if int(all_mutations_dict[i][6]) > count_threshold:
                j += 1
                ws.write(j, 0, i)
                ws.write(j, 1, all_mutations_dict[i][0])
                ws.write(j, 2, all_mutations_dict[i][1])
                ws.write(j, 3, all_mutations_dict[i][3])
                ws.write(j, 4, all_mutations_dict[i][4])
                ws.write(j, 5, all_mutations_dict[i][6])
                ws.write(j, 6, all_mutations_dict[i][7])
                ws.write(j, 7, all_mutations_dict[i][9])
                ws.write(j, 8, all_mutations_dict[i][10])
                ws.write(j, 9, all_mutations_dict[i][8])

        else:
            if int(all_mutations_dict[i][6]) > count_threshold:
                j += 1
                ws.write(j, 0, i)
                ws.write(j, 1, all_mutations_dict[i][0])
                ws.write(j, 2, all_mutations_dict[i][1])
                ws.write(j, 3, all_mutations_dict[i][6])
                ws.write(j, 4, all_mutations_dict[i][7])
                ws.write(j, 5, all_mutations_dict[i][8])

def find_mutation(mod_seq, mod_seq_wo_gaps, ref_seq, ref_seq_wo_gaps, pam, pam_orient,
                  alt_allele, mutation_list, mutation_list_alt,
                  mut_seq_dict, mut_seq_dict_alt) -> None:
    """
    Функция, которая ищет мутации в результатах выравнивания
    :param mod_seq: The sequence of the read aligned to the reference
    :param mod_seq_wo_gaps: The sequence of the read aligned to the reference without gaps
    :param ref_seq: The reference sequence to which the reads were aligned
    :param ref_seq_wo_gaps: The reference sequence to which the reads were aligned without gaps
    :param pam:
    :param pam_orient:
    :param alt_allele: Alternative allele. If specified, the mutation search will be performed separately
    in the readings containing this allele
    :param mutation_list: List of the mutations. Found mutations will be appended to this list
    :param mutation_list_alt: List of the mutations for alt_allele. Found mutations in reads with alt_allele
    will be appended to this list
    :param mut_seq_dict Dictionary with sequence of the mutation
    :param mut_seq_dict_alt Dictionary with sequence of the mutation in reads with alt_allele
    :return: None
    """

    if alt_allele:
        alt_allele = alt_allele.upper()

    len_pam = len(pam)
    pam_orient = pam_orient.upper()[0]

    # Поиск делеций (всех)
    for i in range(len(mod_seq)):
        if mod_seq[i] == '-':
            if mod_seq[i-1] != '-':
                if mod_seq[i+1] != '-':
                    if pam_orient == 'R':
                        mutation = 'single_del_' + str(len(mod_seq)-len_pam - i)
                        mut_seq = ref_seq[i]
                    elif pam_orient == 'L':
                        mutation = 'single_del_' + str(i - len_pam + 1)
                        mut_seq = ref_seq[i]
                    mut_seq_dict[mutation] = mut_seq
                    mutation_list.append(mutation)
                else:
                    k = 1
                    while mod_seq[i+k] == '-':
                        k += 1
                    if pam_orient == 'R':
                        mutation = 'long_del_' + str(abs(len(mod_seq) - len_pam - i - k)) + '-' + str(len(mod_seq) - len_pam - i)
                        mut_seq = ref_seq[i:i + k]
                    elif pam_orient == 'L':
                        mutation = 'long_del_' + str(i - len_pam + 1) + '-' + str(i - len_pam + k)
                        mut_seq = ref_seq[i:i + k]
                    mut_seq_dict[mutation] = mut_seq
                    mutation_list.append(mutation)

    # Поиск делеций (для альтернативного аллеля)
    if alt_allele:
        if mod_seq_wo_gaps.count(alt_allele) != 0:
            for i in range(len(mod_seq)):
                if mod_seq[i] == '-':
                    if mod_seq[i - 1] != '-':
                        if mod_seq[i + 1] != '-':
                            if pam_orient == 'R':
                                mutation_alt = 'single_del_' + str(len(mod_seq) - len_pam - i)
                                mut_seq_alt = ref_seq[i]
                            elif pam_orient == 'L':
                                mutation_alt = 'single_del_' + str(i - len_pam + 1)
                                mut_seq_alt = ref_seq[i]
                            mutation_list_alt.append(mutation_alt)
                            mut_seq_dict_alt[mutation_alt] = mut_seq_alt
                        else:
                            k = 1
                            while mod_seq[i + k] == '-':
                                k += 1
                            if pam_orient == 'R':
                                mutation_alt = 'long_del_' + str(abs(len(mod_seq) - len_pam - i - k)) + '-' + str(len(mod_seq) - len_pam - i)
                                mut_seq_alt = ref_seq[i:i + k]
                            elif pam_orient == 'L':
                                mutation_alt = 'long_del_' + str(i - len_pam + 1) + '-' + str(i - len_pam + k)
                                mut_seq_alt = ref_seq[i:i + k]
                            mutation_list_alt.append(mutation_alt)
                            mut_seq_dict_alt[mutation_alt] = mut_seq_alt

    # Поиск инсерций (всех)
    for i in range(len(ref_seq)):
        if ref_seq[i] == '-':
            if ref_seq[i - 1] != '-':
                if ref_seq[i + 1] != '-':
                    if pam_orient == 'R':
                        mutation = 'single_ins_' + str(len(ref_seq) - len_pam - i)
                        mut_seq = mod_seq[i]
                    if pam_orient == 'L':
                        mutation = 'single_ins_' + str(i - len_pam + 1)
                        mut_seq = mod_seq[i]
                    mutation_list.append(mutation)
                    mut_seq_dict[mutation] = mut_seq
                else:
                    k = 1
                    while ref_seq[i + k] == '-':
                        k += 1
                    if pam_orient == 'R':
                        mutation = 'long_ins_' + str(abs(len(ref_seq) - len_pam - i + 1 - k)) + '-' + str(len(ref_seq) - len_pam - i)
                        mut_seq = mod_seq[i:i + k]
                    if pam_orient == 'L':
                        mutation = 'long_ins_' + str(i - len_pam + 1) + '-' + str(i - len_pam + k)
                        mut_seq = mod_seq[i:i + k]
                    mutation_list.append(mutation)
                    mut_seq_dict[mutation] = mut_seq

    # Поиск инсерций (для альтернативного аллеля)
    if alt_allele:
        if ref_seq_wo_gaps.count(alt_allele) != 0:
            for i in range(len(ref_seq)):
                if ref_seq[i] == '-':
                    if ref_seq[i - 1] != '-':
                        if ref_seq[i + 1] != '-':
                            if pam_orient == 'R':
                                mutation_alt = 'single_ins_' + str(len(ref_seq) - len_pam - i)
                                mut_seq_alt = mod_seq[i]
                            if pam_orient == 'L':
                                mutation_alt = 'single_ins_' + str(i - len_pam + 1)
                                mut_seq_alt = mod_seq[i]
                            mutation_list_alt.append(mutation_alt)
                            mut_seq_dict_alt[mutation_alt] = mut_seq_alt
                        else:
                            k = 1
                            while ref_seq[i + k] == '-':
                                k += 1
                            if pam_orient == 'R':
                                mutation_alt = 'long_ins_' + str(abs(len(ref_seq) - len_pam - i + 1 - k)) + '-' + str(len(ref_seq) - len_pam - i)
                                mut_seq_alt = mod_seq[i:i + k]
                            if pam_orient == 'L':
                                mutation_alt = 'long_ins_' + str(i - len_pam + 1) + '-' + str(i - len_pam + k)
                                mut_seq_alt = mod_seq[i:i + k]
                            mutation_list_alt.append(mutation_alt)
                            mut_seq_dict_alt[mutation_alt] = mut_seq_alt
    return None

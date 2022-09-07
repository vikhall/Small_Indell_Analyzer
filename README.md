# Small_Indell_Analyzer
Tool that performs analysis of the short indels introduced by Cas endonuclease. 

usage: 
«`{python} Small_Indell_Analyzer_new.py [-h] [-w WORKDIR] [-o RESDIR] [-e EXCEL_FILE] [-b BAD_ALIGN_FILE] [-r REPORT_FILE] [-t ALIGN_QUAL_THRESHOLD] [-с COUNT_THRESHOLD] [-a ALT_ALLELE] [-f WRITE_FASTQ] [-m MUTATION_TO_WRITE] ref_seq case control pam pam_orient«` 

positional arguments:

  ref_seq               Reference sequence to which all reads will be aligned. Might be string containing only A,T,G,C letters (in AnY cASe) or path to the fasta-file

  case                  Fastq file with case reads

  control               Fastq file with control reads

  pam                   PAM sequence. This sequence is necessary for the correct numbering of mutations

  pam_orient            Orientation of the PAM in the reference sequence. It can be "left" if mutations are located to the right of the pam sequence, or "right" if mutations are located to the left of the pam sequence Example: R/right/Right or L/left/Left

options:

  -h, --help            show this help message and exit

  -w WORKDIR, --workdir WORKDIR

                        Working directory with fastq files. By default, all input files will be searched in this directory (if only filenames without path given). Default: directory with this script

  -o RESDIR, --resdir RESDIR

                        Directory to which results will be saved If --resdir==workdir, directory will not be created and results will be saved in current working directory. If only name of the directory given, the directory will be created in working directory. If path/to/directory given, the directory will    

                        be created in this path. If resdit not exist, it will be created. Default: Results

  -e EXCEL_FILE, --excel_file EXCEL_FILE

                        Excel file with main result. If only name of the file given, file with report will be created in workdir. If path to the file given, report will be written in this file (file will be created if not exist (otherwise, file will be overwritten)). Default: Mutations_+{Name of the control    

                        file}.xls

  -b BAD_ALIGN_FILE, --bad_align_file BAD_ALIGN_FILE

                        File with bad alignments (with score < align_qual_threshold). Default: None

  -r REPORT_FILE, --report_file REPORT_FILE

                        File with brief report. If only name of the file given, file with report will be created in workdir. If path to the file given, report will be written in this file (file will be created if not exist (otherwise, report will be written in the end of the existing file)).Default:

                        Report_+{Name of the control file}.txt

  -t ALIGN_QUAL_THRESHOLD, --align_qual_threshold ALIGN_QUAL_THRESHOLD

                        The threshold for the quality of alignments. Only alignments with a score higher than this value will be used to search for mutations. Default: 0

  -с COUNT_THRESHOLD, --count_threshold COUNT_THRESHOLD

                        Threshold of mutation frequency. Only mutations with a frequency higher than this value will be saved after filtering Default: 3

  -a ALT_ALLELE, --alt_allele ALT_ALLELE

                        Short unique sequence containing alternative allele. If given, the mutation search will be performed separately in the reads containing this allele. Must be short unique substring of the ref_seq, containing SNP. Example: "ATGCA", where G is SNP of interest. Nucleotides around G is       

                        needed to found this substring in ref_seq. Default: None

  -f WRITE_FASTQ, --write_fastq WRITE_FASTQ

                        If given (any string: yes/true etc), three groups of reads will be written in resdir: aligned reads without mutations, aligned reads with mutations and not aligned reads (with score < align_qual_threshold). Default: None

  -m MUTATION_TO_WRITE, --mutation_to_write MUTATION_TO_WRITE

                        If given, reads with this mutation will be written in fastq-files. Example: "--mutation_to_write=single_del_6". Default: None.



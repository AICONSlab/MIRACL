import os
import sys
import argparse
import subprocess


def run_reg_clar(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if sys.argv[-2] == 'flow' and sys.argv[-1] == 'reg_clar':
        subprocess.Popen('%s/flow/miracl_workflow_registration_clarity-allen.sh' % miracl_home,
                         shell=True)
    else:
        if args['help']:
            subprocess.Popen('%s/flow/miracl_workflow_registration_clarity-allen.sh -h' % miracl_home,
                             shell=True)
        else:
            bash_args = '-f %s -n "%s" -r "%s"' % (args['folder'], args['conv_opts'][0], args['reg_opts'][0])

            print('Running CLARITY to Allen registration workflow with the following arguments: \n'
                  "miracl_workflow_registration_clarity-allen.sh %s " % bash_args)

            subprocess.check_call('%s/flow/miracl_workflow_registration_clarity-allen.sh %s' % (miracl_home,
                                                                                                   bash_args),
                                  shell=True,
                                  stderr=subprocess.STDOUT)


def run_seg(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if sys.argv[-2] == 'flow' and sys.argv[-1] == 'seg':
        subprocess.Popen('%s/flow/miracl_workflow_segmentation_clarity.sh' % miracl_home,
                         shell=True)
    else:
        if args['help']:
            subprocess.Popen('%s/flow/miracl_workflow_segmentation_clarity.sh -h' % miracl_home,
                             shell=True)
        else:
            bash_args = '-f %s -t %s -v %s -s "%s" -e "%s"' % (args['folder'], args['type'], args['vox_res'],
                                                               args['seg_opts'][0], args['ext_opts'][0])

            subprocess.check_call('%s/flow/miracl_workflow_segmentation_clarity.sh %s' % (miracl_home, bash_args),
                                  shell=True,
                                  stderr=subprocess.STDOUT)


def run_sta(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if sys.argv[-2] == 'flow' and sys.argv[-1] == 'sta':
        subprocess.Popen('%s/flow/miracl_workflow_sta.sh' % miracl_home,
                         shell=True)
    else:
        if args['help']:
            subprocess.Popen('%s/flow/miracl_workflow_sta.sh -h' % miracl_home,
                             shell=True)
        else:
            bash_args = '-f %s -o %s -l %s -r %s -m %s -g %s -k %s -a %s -d %s -c %s -q %s -b %s -u %s' % (
                args['folder'], args['out_nii'], args['seed_label'],
                args['clar_reg'], args['hemi'], args['dog'],
                args['sigma'], args['angle'], args['down'], args['chan'],
                args['out_dir'], args['brain_mask'], args['lbl_mask'])

            subprocess.check_call('%s/flow/miracl_workflow_sta.sh %s' % (miracl_home, bash_args), shell=True,
                                  stderr=subprocess.STDOUT)


def run_mul(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if args['help']:
        subprocess.Popen('%s/flow/miracl_workflow_multiple_mice.sh -h' % miracl_home,
                         shell=True)
    else:
        bash_args = '-st %s -sc %s -id %s -opt "%s" -nj %s -tj %s' % (args['smod'], args['sname'], args['in_dir'],
                                                                      args['fopts'][0], args['mnum'], args['stime'])

        subprocess.check_call('%s/flow/miracl_workflow_multiple_mice.sh %s' % (miracl_home, bash_args),
                              shell=True,
                              stderr=subprocess.STDOUT)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # reg_clarity
    parser_regclar = subparsers.add_parser('reg_clar', add_help=False,
                                           help="whole-brain clarity registration to Allen atlas")
    parser_regclar.add_argument('-f', '--folder', metavar='',
                                help="input registration folder")
    parser_regclar.add_argument('-n', '--conv_opts', nargs='+', metavar='',
                                help="file conversion options")
    parser_regclar.add_argument('-r', '--reg_opts', nargs='+', metavar='',
                                help="registration options")
    parser_regclar.add_argument('-h', '--help', action='store_true')

    parser_regclar.set_defaults(func=run_reg_clar)

    # sta
    parser_sta = subparsers.add_parser('sta', add_help=False, help="Structure Tensor Analysis (STA)")
    parser_sta.add_argument('-f', '--folder', metavar='',
                            help="input folder")
    parser_sta.add_argument('-o', '--out_nii', metavar='',
                            help="output nifti")
    parser_sta.add_argument('-l', '--seed_label', metavar='',
                            help="Seed label abbreviation (from Allen atlas ontology)")
    parser_sta.add_argument('-r', '--clar_reg', metavar='',
                            help="CLARITY final registration folder")
    parser_sta.add_argument('-m', '--hemi', metavar='',
                            help="Labels hemi")
    parser_sta.add_argument('-g', '--dog', metavar='',
                            help="Derivative of Gaussian (dog) sigma")
    parser_sta.add_argument('-k', '--sigma', metavar='',
                            help="Gaussian smoothing sigma")
    parser_sta.add_argument('-a', '--angle', metavar='',
                            help="Tracking angle threshold")
    parser_sta.add_argument('-d', '--down', metavar='',
                            help="Downsample ratio")
    parser_sta.add_argument('-c', '--chan', metavar='',
                            help="Output channel name")
    parser_sta.add_argument('-q', '--out_dir', metavar='',
                            help="Output directory")
    parser_sta.add_argument('-b', '--brain_mask', metavar='',
                            help="Brain mask")
    parser_sta.add_argument('-u', '--lbl_mask', metavar='',
                            help="Seed mask")
    parser_sta.add_argument('-h', '--help', action='store_true')

    parser_sta.set_defaults(func=run_sta)

    # seg
    parser_seg = subparsers.add_parser('seg', add_help=False, help="CLARITY segmentation")
    parser_seg.add_argument('-f', '--folder', metavar='',
                            help="input segmentation folder")
    parser_seg.add_argument('-t', '--type', metavar='',
                            help="segmentation type: virus, cfos, sparse or nuclear")
    parser_seg.add_argument('-v', '--vox_res', metavar='',
                            help="voxel resolution/size")
    parser_seg.add_argument('-s', '--seg_opts', nargs='+', metavar='',
                            help="segmentation options")
    parser_seg.add_argument('-e', '--ext_opts', nargs='+', metavar='',
                            help="feature extraction options")
    parser_seg.add_argument('-h', '--help', action='store_true')

    parser_seg.set_defaults(func=run_seg)

    # mul
    parser_mul = subparsers.add_parser('mul', add_help=False, help="Run multiple mice")
    parser_mul.add_argument('-st', '--smod', metavar='',
                            help="script module")
    parser_mul.add_argument('-sc', '--sname', metavar='',
                            help="script name")
    parser_mul.add_argument('-id', '--in_dir', metavar='',
                            help="input directory with multiple mice data")
    parser_mul.add_argument('-opt', '--fopts', nargs='+', metavar='',
                            help="input options for script to run")
    parser_mul.add_argument('-nj', '--mnum', metavar='',
                            help="number of mice to run simultaneously - in parallel")
    parser_mul.add_argument('-tj', '--stime', metavar='',
                            help="time for computer to sleep between parallel jobs")
    parser_mul.add_argument('-h', '--help', action='store_true')

    parser_mul.set_defaults(func=run_mul)

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()

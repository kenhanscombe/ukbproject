import click
import subprocess
import os
import re
import glob
import sys
import pandas as pd
import numpy as np
# import tempfile

from ukbproject.withdraw import withdraw_index
from datetime import date
from pathlib import Path

# import sqlite3
# import modin.pandas as pd
# from ukbproject.recdtype import record_col_types


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx):
    """
    Sets up a UKB project on Rosalind storing common data and utilities in the
    parent directory, at resources/ and bin/ respectively.
    """
    module_p = Path(__file__)
    pkg_dir = module_p.absolute().parent
    os.environ['PROJECT'] = str(pkg_dir)

    p = Path('/scratch/datasets/ukbiobank')
    ctx.ensure_object(dict)
    ctx.obj['ukbiobank'] = p.absolute()
    ctx.obj['genotyped'] = '/scratch/datasets/ukbiobank/June2017/Genotypes'
    ctx.obj['imputed'] = '/scratch/datasets/ukbiobank/June2017/Imputed'
    ctx.obj['pkg_dir'] = pkg_dir


@cli.command()
@click.option('--parent-dir', default=None,
              help='Absolute path to project parent directory')
@click.pass_context
def util(ctx, parent_dir):
    """Downloads UKB file handlers and utilities."""
    if parent_dir is None:
        ukb_dir = ctx.obj['ukbiobank']
    else:
        ukb_dir = Path(parent_dir).absolute()

    (ukb_dir / 'bin').mkdir(exist_ok=True)
    (ukb_dir / 'resources').mkdir(exist_ok=True)

    os.system(f'''
        # wget -O {ukb_dir}/resources/Codings_Showcase.csv http://biobank.ctsu.ox.ac.uk/~bbdatan/Codings_Showcase.csv
        wget -O {ukb_dir}/resources/Codings.csv https://biobank.ctsu.ox.ac.uk/~bbdatan/Codings.csv
        wget -nd -O {ukb_dir}/resources/encoding.ukb biobank.ctsu.ox.ac.uk/crystal/util/encoding.ukb

        wget -nd -O {ukb_dir}/bin/ukbmd5 biobank.ndph.ox.ac.uk/showcase/util/ukbmd5
        wget -nd -O {ukb_dir}/bin/ukbconv biobank.ndph.ox.ac.uk/showcase/util/ukbconv
        wget -nd -O {ukb_dir}/bin/ukbunpack biobank.ndph.ox.ac.uk/showcase/util/ukbunpack
        wget -nd -O {ukb_dir}/bin/ukbfetch biobank.ndph.ox.ac.uk/showcase/util/ukbfetch
        wget -nd -O {ukb_dir}/bin/ukblink biobank.ndph.ox.ac.uk/showcase/util/ukblink
        wget -nd -O {ukb_dir}/bin/ukbgene biobank.ctsu.ox.ac.uk/crystal/util/ukbgene

        chmod +x {ukb_dir}/bin/ukb*''')


@cli.command()
@click.option('-p', '--project-dir', help='Name of project directory')
@click.option('--parent-dir', default=None,
              help='Absolute path to project parent directory')
@click.argument('users', nargs=-1)
@click.pass_context
def clean(ctx, project_dir, users, parent_dir):
    """
    Deletes defunct file/dir(s) from projects, and sets permissions.

    USERS A whitespace separated list of uids to grant rwx permission.
    """
    if parent_dir is None:
        ukb_dir = ctx.obj['ukbiobank']
    else:
        ukb_dir = Path(parent_dir).absolute()

    prj_dir = ukb_dir / project_dir

    for x in ['src', 'R', 'resources', 'returns',
              'Snakefile', 'snake.py', 'project.py', 'link.py', 'fields.ukb']:
        os.system(f'rm -rf {prj_dir}/{x}')

    # setfacl
    if users:
        os.system(f'setfacl -R -b {prj_dir}')
        for u in users:
            os.system(
                f'setfacl -R -m u:{u}:rwX,d:u:{u}:rwX,g::r-X,d:g::r-X {prj_dir}')

    # add new subdirectories
    for d in ['withdrawals', 'records']:
        (ukb_dir / project_dir / d).mkdir(exist_ok=True)


@cli.command()
@click.option('-p', '--project-id', help='Project ID, e.g., 12345.')
@click.option('--parent-dir', default=None,
              help='Absolute path to project parent directory')
@click.argument('users', nargs=-1)
@click.pass_context
def create(ctx, project_id, users, parent_dir):
    """Creates a skeleton UKB project directory.

    Positional arguments:

    USERS A whitespace separated list of uids to grant rwx permission.
    """
    if parent_dir is None:
        ukb_dir = ctx.obj['ukbiobank']
    else:
        ukb_dir = Path(parent_dir).absolute()

    gen_target = ctx.obj['genotyped']
    imp_target = ctx.obj['imputed']
    project_dir = f'ukb{project_id}'

    if (ukb_dir / project_dir).exists():
        click.echo(
            'FileExistError: A project directory with this project ID already exists.')
        sys.exit()

    (ukb_dir / project_dir).mkdir()

    # setfacl
    os.system(f'setfacl -b {ukb_dir}/{project_dir}')

    for u in users:
        os.system(
            f'setfacl -R -m u:{u}:rwX,d:u:{u}:rwX,g::r-X,d:g::r-X {ukb_dir}/{project_dir}')

    # make subdirectories
    for d in ['genotyped', 'imputed', 'raw', 'logs', 'config',
              'phenotypes', 'withdrawals']:
        (ukb_dir / project_dir / d).mkdir()

    # symlink genetic data
    gen_dir = ukb_dir / project_dir / 'genotyped'
    imp_dir = ukb_dir / project_dir / 'imputed'

    os.system(f'''
        ln -s {gen_target}/ukb_binary_v2.bed {gen_dir}/ukb_binary_v2.bed
        ln -s {gen_target}/ukb_binary_v2.bim {gen_dir}/ukb_binary_v2.bim

        ln -s {imp_target}/ukb_sqc_v2.txt {imp_dir}/ukb_sqc_v2.txt
        ln -s {imp_target}/ukb_sqc_v2_fields.txt {imp_dir}/ukb_sqc_v2_fields.txt

        for i in X XY $(seq 1 22)
        do
        ln -s {imp_target}/ukb_imp_chr"$i"_v3.bgen {imp_dir}/ukb_imp_chr"$i".bgen
        ln -s {imp_target}/ukb_imp_chr"$i"_v3.bgen.bgi {imp_dir}/ukb_imp_chr"$i".bgen.bgi
        ln -s {imp_target}/ukb_mfi_chr"$i"_v3.txt {imp_dir}/ukb_mfi_chr"$i".txt
        done
        ''')


@cli.command()
@click.option('-p', '--project-dir', help='Name of project directory')
@click.option('-f', '--fam', default=None, help='Name of the fam file.')
@click.option('-s', '--sample', default=None, help='Name of the sample file.')
@click.option('-r', '--rel', default=None, help='Name of the relatedness file.')
@click.option('--parent-dir', default=None,
              help='Absolute path to project parent directory')
@click.pass_context
def link(ctx, project_dir, fam, sample, rel, parent_dir):
    """Makes links to sample information and relatedness files."""
    if parent_dir is None:
        ukb_dir = ctx.obj['ukbiobank']
    else:
        ukb_dir = Path(parent_dir).absolute()

    prj_dir = ukb_dir / project_dir
    raw_dir = ukb_dir / project_dir / 'raw'

    if fam:
        try:
            os.system(f'ln -s {raw_dir}/{fam} {prj_dir}/genotyped/')
        except FileExistsError:
            print("The named .fam file does not exist in the project subdirectory raw/.")

    if sample:
        try:
            os.system(f'ln -s {raw_dir}/{sample} {prj_dir}/imputed/')
        except FileExistsError:
            print(
                "The named .sample file does not exist in the project subdirectory raw/.")

    if rel:
        try:
            os.system(f'ln -s {raw_dir}/{rel} {prj_dir}/imputed/')
        except FileExistsError:
            print(
                "The named relatedness file does not exist in the project subdirectory raw/.")


@cli.command()
@click.option('-p', '--project-dir', help='Name of project directory')
@click.option('-n', '--dry-run', is_flag=True, default=False,
              help="Use option -n for a dry run.")
@click.option('-u', '--unlock', is_flag=True, default=False,
              help="Use option -u to unlock the directory.")
@click.option('--parent-dir', default=None,
              help='Absolute path to project parent directory')
@click.pass_context
def munge(ctx, project_dir, dry_run, unlock, parent_dir):
    """Runs rules described in the Snakefile to munge UKB data."""
    if parent_dir is None:
        ukb_dir = ctx.obj['ukbiobank']
    else:
        ukb_dir = Path(parent_dir).absolute()

    pkg_dir = ctx.obj['pkg_dir']
    prj_dir = ukb_dir / project_dir
    snake_file = pkg_dir / 'Snakefile'
    cfg_dir = prj_dir / 'config'
    cfg_dir.mkdir(parents=True, exist_ok=True)
    config_file = cfg_dir / "config.yml"
    config_file.touch(exist_ok=True)

    with open(config_file, 'w') as conf:
        conf.write(
            f'''
project_dir: {prj_dir}
pkg_dir: {pkg_dir}
output: {prj_dir}/logs/{{rule}}.{{wildcards.id}}.slurm.%j.out
error: {prj_dir}/logs/{{rule}}.{{wildcards.id}}.slurm.%j.err
''')

    cmd = f'snakemake --profile slurm --snakefile {snake_file} --configfile {config_file}'
    cmd = cmd.split()

    if dry_run:
        cmd += ['-n']

    if unlock:
        cmd += ['--unlock']

    subprocess.run(cmd)


@cli.command()
@click.option('-p', '--project-dir', help='Name of project directory')
@click.option('-o', '--out-dir', default='withdrawals',
              help='''Name of the directory to write withdrawal exclusions and
              log (default is "withdrawals")''')
@click.option('--parent-dir', default=None,
              help='Absolute path to project parent directory')
@click.pass_context
def withdraw(ctx, project_dir, out_dir, parent_dir):
    """
    Writes withdrawal IDs and corresponding indeces to be excluded.

    Listed IDs are a combination of project-specific IDs that
    appear in both the (latest) withdrawals file and in the sample information
    files (.fam and .sample), and negative IDs in the fam and sample files. A
    log of withdrawal and sample information counts is written.
    """
    if parent_dir is None:
        ukb_dir = ctx.obj['ukbiobank']
    else:
        ukb_dir = Path(parent_dir).absolute()

    prj_dir = ukb_dir / project_dir

    f_exclude, s_exclude, log_info = withdraw_index(prj_dir)

    (prj_dir / out_dir).mkdir(exist_ok=True)

    def write_excl(excl, gen, ext, out=out_dir,
                   date=date.today().strftime('%d%m%Y')):
        if (gen == 'genotyped') & (ext == 'id'):
            id_col = 'fid'
        elif (gen == 'imputed') & (ext == 'id'):
            id_col = 'ID_1'
        else:
            id_col = 'index'

        (excl
         .loc[excl['exclude'] == 1, id_col]
         .to_csv(f'{prj_dir}/{out}/wexcl_' + gen + f'_{date}.' + ext,
                 header=False, index=False))

    d1 = date.today().strftime('%d %B %Y')
    d2 = date.today().strftime('%d%m%Y')

    [write_excl(*i + (ext,))
        for i in zip([f_exclude, s_exclude], ['genotyped', 'imputed'])
        for ext in ['id', 'index']]

    # log
    with open(f'{prj_dir}/{out_dir}/wexcl_{d2}.log', 'w') as f:
        f.write(f'prj withdraw log {d1}' + '\n\n')
        f.write('project id: ' + log_info['project_id'] + '\n')
        f.write('-----------------\n')

        f.write(str(log_info['withdrawal_n']) + ' withdrawal file IDs\n\n')

        f.write(str(log_info['fam_n']) + ' fam file IDs\n')
        f.write(str(log_info['fam_negative_n']) + ' fam file negative IDs\n')
        f.write(str(log_info['fam_in_withdrawal_n']) +
                ' fam file IDs in withdrawal file\n')
        f.write(str(log_info['fam_exclusion_n']) +
                f' exclusion IDs for genotyped genetic data written to excl_gen_{d2}.id;' +
                f' indices written to excl_gen_{d2}.index' + '\n\n')

        f.write(str(log_info['sample_n']) + ' sample file IDs\n')
        f.write(str(log_info['sample_negative_n']) +
                ' sample file negative IDs\n')
        f.write(str(log_info['sample_in_withdrawal_n']) +
                ' sample file IDs in withdrawal file\n')
        f.write(str(log_info['sample_exclusion_n']) +
                f' exclusion IDs for imputed genetic data written to excl_imp_{d2}.id;' +
                f' indices written to excl_imp_{d2}.index' + '\n')


@cli.command()
@click.option('-p', '--project-dir', help='Name of project directory')
@click.option('--parent-dir', default=None,
              help='Absolute path to project parent directory')
@click.pass_context
def remove(ctx, project_dir, parent_dir):
    '''Removes withdrawals from latest sample information.

    Replaces withdrawal IDs in the fam and sample files with a negative
    integer sequence, and writes these to project subdirectories
    genotyped and imputed respectively with the prefix `w`.
    '''
    if parent_dir is None:
        ukb_dir = ctx.obj['ukbiobank']
    else:
        ukb_dir = Path(parent_dir).absolute()

    prj_dir = ukb_dir / project_dir
    rem_dir = prj_dir / 'withdrawals'
    gen_dir = prj_dir / 'genotyped'
    imp_dir = prj_dir / 'imputed'
    fam_prefix = re.sub('_.*$', '', project_dir) + '_cal'
    sample_prefix = re.sub('_.*$', '', project_dir) + '_imp'

    fam_file = max(glob.glob(
        str(prj_dir / f'raw/{fam_prefix}*fam')), key=os.path.getctime)
    fam_names = ['fid', 'iid', 'pid', 'mid', 'sex', 'phe']
    fam_dtypes = dict(
        zip(fam_names, (['Int64'] * (len(fam_names) - 1)) + ['string']))
    fam = pd.read_table(fam_file, header=None, sep=' ', names=fam_names,
                        dtype=fam_dtypes)

    sample_file = max(glob.glob(
        str(prj_dir / f'raw/{sample_prefix}*sample')), key=os.path.getctime)
    sample_names = ['ID_1', 'ID_2', 'missing', 'sex']
    sample_dtypes = dict(zip(sample_names, (['Int64'] * len(sample_names))))
    sample = pd.read_table(sample_file, sep=' ', skiprows=[
                           1], dtype=sample_dtypes)

    gen_rem_file = max(
        glob.glob(str(rem_dir / '*genotyped*id')), key=os.path.getctime)
    gen_rem = pd.read_table(gen_rem_file, header=None, names=['id'])

    imp_rem_file = max(
        glob.glob(str(rem_dir / '*imputed*id')), key=os.path.getctime)
    imp_rem = pd.read_table(imp_rem_file, header=None, names=['id'])

    def rem_id_dict(rem):
        """Returns a dict of replacement negative IDs"""
        id_min = rem.id.min()

        for row in range(rem.shape[0]):
            if rem.loc[row, 'id'] > 0:
                id_min -= 1
                rem.loc[row, 'new_id'] = id_min
            else:
                rem.loc[row, 'new_id'] = rem.loc[row, 'id']

        rem = rem.loc[rem.id.gt(0), ]
        return dict(zip(rem.id, rem.new_id.astype('Int64')))

    gen_rem_dict = rem_id_dict(gen_rem)
    imp_rem_dict = rem_id_dict(imp_rem)

    fam['new_id'] = fam.fid.map(gen_rem_dict).astype('Int64')
    fam['fid'] = np.where(fam['new_id'].isna(), fam['fid'], fam['new_id'])
    fam['iid'] = fam['fid']
    fam['sex'] = np.where(fam['fid'].gt(0), fam['sex'], 0)

    sample['new_id'] = sample.ID_1.map(imp_rem_dict).astype('Int64')
    sample['ID_1'] = np.where(sample['new_id'].isna(),
                              sample['ID_1'], sample['new_id'])
    sample['ID_2'] = sample['ID_1']
    sample['sex'] = np.where(sample['ID_1'].gt(0), sample['sex'], 0)

    fam_file_name = Path(fam_file).name
    f = fam.drop(columns='new_id')
    f.to_csv(str(gen_dir / f'w{fam_file_name}'),
             sep=' ', header=False, index=False)

    sample_file_name = Path(sample_file).name
    s = sample.drop(columns='new_id')
    s.columns = pd.MultiIndex.from_tuples(
        zip(sample_names, ['0', '0', '0', 'D']))
    s.to_csv(str(imp_dir / f'w{sample_file_name}'),
             sep=' ', header=True, index=False)


@cli.command()
@click.option('-p', '--project-dir', help='Name of project directory')
@click.argument('record', nargs=-1)
@click.pass_context
def recdisk(ctx, project_dir, record):
    """Converts UKB record-level data to R disk.frame.

    Positional arguments:

    RECORD whitespace separated list of record-level data file names
    """
    pkg_dir = ctx.obj['pkg_dir']
    prj_dir = pkg_dir.parent / project_dir
    rec_files_pos_arg = ' '.join(record)

    os.system(f'''
        module load apps/R/3.6.0
        Rscript --vanilla {pkg_dir}/recdisk.R -p {prj_dir} {rec_files_pos_arg}
        ''')

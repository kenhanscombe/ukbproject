import click
import os
import re
import glob
import sys
import sqlite3
import pandas as pd
import numpy as np

from withdraw import withdraw_index
from recdtype import record_col_types
from datetime import date
from pathlib import Path


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
@click.pass_context
def util(ctx):
    """Downloads UKB file handlers and utilities."""
    ukb_dir = ctx.obj['ukbiobank']
    (ukb_dir / 'bin').mkdir(exist_ok=True)
    (ukb_dir / 'resources').mkdir(exist_ok=True)

    os.system(f'''
        wget -O {ukb_dir}/resources/Codings_Showcase.csv http://biobank.ctsu.ox.ac.uk/~bbdatan/Codings_Showcase.csv
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
@click.argument('users', nargs=-1)
@click.pass_context
def clean(ctx, project_dir, users):
    """
    Removes defunct file/dir(s) from projects, and sets permissions.

    USERS A whitespace separated list of uids to grant rwx permission.
    """
    ukb_dir = ctx.obj['ukbiobank']
    prj_dir = ukb_dir / project_dir

    for x in ['src', 'R', 'resources', 'returns',
              'Snakefile', 'snake.py', 'project.py', 'link.py', 'fields.ukb']:
        os.system(f'rm -rf {prj_dir}/{x}')

    # setfacl
    if users:
        os.system(f'setfacl -R -b {prj_dir}')
        for u in users:
            os.system(f'setfacl -R -m u:{u}:rw-,d:u:{u}:rw-,g::r--,m::rw- {prj_dir}')

    # add new subdirectories
    for d in ['withdrawals', 'records']:
        (ukb_dir / project_dir / d).mkdir(exist_ok=True)


@cli.command()
@click.option('-p', '--project-id', help='Project ID, e.g., 12345.')
@click.argument('users', nargs=-1)
@click.pass_context
def create(ctx, project_id, users):
    """Creates a skeleton UKB project directory.

    USERS A whitespace separated list of uids to grant rwx permission.    
    """
    ukb_dir = ctx.obj['ukbiobank']
    gen_target = ctx.obj['genotyped']
    imp_target = ctx.obj['imputed']
    project_dir = f'ukb{project_id}'
    
    if (ukb_dir / project_dir).exists():
        click.echo('FileExistError: A project directory with this project ID already exists.')
        sys.exit()

    (ukb_dir / project_dir).mkdir()
    
    # setfacl
    os.system(f'setfacl -b {ukb_dir}/{project_dir}')

    for u in users:
        os.system(f'setfacl -R -m u:{u}:rw-,d:u:{u}:rw-,g::r--,m::rw- {ukb_dir}/{project_dir}')

    # make subdirectories
    for d in ['genotyped', 'imputed', 'raw',
              'log', 'phenotypes', 'withdrawals']:
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
@click.pass_context
def link(ctx, project_dir, fam, sample, rel):
    """Makes links to sample information and relatedness files."""
    ukb_dir = ctx.obj['ukbiobank']
    raw_dir = ukb_dir / project_dir / 'raw'

    if fam:
        try:
            os.system(f'ln -s {raw_dir}/{fam} genotyped/')
        except FileExistsError:
            print("The named .fam file does not exist in the project subdirectory raw/.")

    if sample:
        try:
            os.system(f'ln -s {raw_dir}/{sample} imputed/')
        except FileExistsError:
            print(
                "The named .sample file does not exist in the project subdirectory raw/.")

    if rel:
        try:
            os.system(f'ln -s {raw_dir}/{rel} imputed/')
        except FileExistsError:
            print(
                "The named relatedness file does not exist in the project subdirectory raw/.")


@cli.command()
@click.option('-p', '--project-dir', help='Name of project directory')
@click.option('-n', '--dry-run', is_flag=True, default=False, help="Use option -n for a dry run.")
@click.pass_context
def munge(ctx, project_dir, dry_run):
    """Runs rules described in the Snakefile to munge UKB data."""

    pkg_dir = ctx.obj['pkg_dir']
    snake_file = pkg_dir / 'Snakefile'
    project_dir = pkg_dir.parent / project_dir
    log_dir = project_dir / 'log'

    snakemake_call = f'snakemake \
                      --profile slurm \
                      --snakefile {snake_file} \
                      --use-envmodules \
                      --jobs 100 \
                      --rerun-incomplete \
                      --config \
                        project_dir={project_dir} \
                        pkg_dir={pkg_dir}'

    if dry_run:
        os.system(snakemake_call + ' -n')
    else:
        os.system(snakemake_call)


@cli.command()
@click.option('-w', '--withdrawal',
              help='Path to the withdrawal file.')
@click.option('-f', '--fam', help='Path to the fam file.')
@click.option('-s', '--sample', help='Path to the sample file.')
@click.option('-o', '--out-dir', default='withdrawals',
              help='''Name of the directory to write withdrawal exclusions and
              log (default is "withdrawals")''')
# @click.option('-r', '--remove', is_flag=True,
#               help='''Remove withdrawals from genetic analysis. IDs in fam and
#               sample files changed to sequence of negative integers''')
def withdraw(withdrawal, fam, sample, out_dir):
    """
    Writes withdrawal IDs and corresponding indeces to be excluded.
    
    Listed IDs are a combination of project-specific IDs that
    appear in both the (latest) withdrawals file and in the sample information
    files (.fam and .sample), and negative IDs in the fam and sample files. A
    log of withdrawal and sample information counts is written.
    """
    f_exclude, s_exclude, log_info = withdraw.withdraw_index(
        withdrawal, fam, sample)

    # Assuming the fam file is in genotyped/ (as it should be)
    p = Path(fam)
    project_dir = p.absolute().parent
    (project_dir / out_dir).mkdir(exist_ok=True)
    # out = str(project_dir / out_dir)
    
    def write_excl(excl, gen, ext, out=out_dir, date=date.today().strftime('%d%m%Y')):
        if (gen == 'genotyped') & (ext == 'id'):
            id_col = 'fid'
        elif (gen == 'imputed') & (ext == 'id'):
            id_col = 'ID_1'
        else:
            id_col = 'index'

        (excl
         .loc[excl['exclude'] == 1, id_col]
         .to_csv(f'{out}/wexcl_' + gen + f'_{date}.' + ext,
                 header=False, index=False))


    d1 = date.today().strftime('%d %B %Y')
    d2 = date.today().strftime('%d%m%Y')

    [write_excl(*i + (ext,))
        for i in zip([f_exclude, s_exclude], ['genotyped', 'imputed'])
        for ext in ['id', 'index']]

    # log
    with open(f'{out_dir}/wexcl_{d2}.log', 'w') as f:
        f.write(f'exclude.py log {d1}' + '\n\n')
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
@click.option('-r', '--record', multiple=True,
              help='Name of the record – x will match x*')
@click.pass_context
def recdb(ctx, project_dir, record):
    """Adds UKB record-level data to sqlite DB."""
    pkg_dir = ctx.obj['pkg_dir']
    project_dir = pkg_dir.parent / project_dir
    raw_dir = project_dir / 'raw'
    record_dir = project_dir / 'records'
    record_files = []

    for rec in record:
        record_files.extend(glob.glob(str(raw_dir / f'{rec}*')))
        
    con_rec = sqlite3.connect(record_dir / 'records.db')

    includes_covid = any(['covid' in f for f in record_files])
    if includes_covid:
        con_cov = sqlite3.connect(record_dir / 'covid.db')
    
    for f in record_files:
        table_name = re.sub(str(raw_dir) + '\/|\.txt', '', f)
        print('Reading', table_name + '...')
        
        if table_name.startswith('gp_'):
            df = pd.read_table(raw_dir / f, header=0, encoding='latin1')
        else:
            df = pd.read_table(raw_dir / f, header=0)

        if table_name.startswith('covid'):
            df.to_sql(table_name, con_cov, if_exists='replace', index=False,
                      dtype=record_col_types[table_name])
        else:
            df.to_sql(table_name, con_rec, if_exists='replace', index=False,
                      dtype=record_col_types[table_name])

    con_rec.close()
    if includes_covid:
        con_cov.close()

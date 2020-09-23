import click
import withdraw
from datetime import date


@click.command()
@click.option('-w', '--withdrawal',
              help='Path to the withdrawal file.')
@click.option('-f', '--fam', help='Path to the fam file.')
@click.option('-s', '--sample', help='Path to the sample file.')
@click.option('-o', '--out-dir', default='.')
def exclude(withdrawal, fam, sample, out_dir):
    """Writes a file of withdrawal ids (wexcl*.id) and a corresponding
    file of indeces (wexcl*.index), to remove from the genotyped and imputed
    data. These withdrawal ids are a combination of ids in the
    withdrawals file and negtive ids in the fam and sample files. A
    log of withdrawal id and sample information counts is written to
    (wexcl*.log) The wexcl*.id files are accepted by PLINK --remove and
    QCTOOL --excl-samples, for genotyped and imputed files respectively. Both
    wexcl*.id and wexcl*.index files are one-per-line no header."""
    f_exclude, s_exclude, log_info = withdraw.withdraw_index(
        withdrawal, fam, sample)

    def write_excl(excl, gen, ext, date=date.today().strftime('%d%m%Y')):
        if (gen == 'genotyped') & (ext == 'id'):
            id_col = 'fid'
        elif (gen == 'imputed') & (ext == 'id'):
            id_col = 'ID_1'
        else:
            id_col = 'index'

        (excl
         .loc[excl['exclude'] == 1, id_col]
         .to_csv(f'{out_dir}/wexcl_' + gen + f'_{date}.' + ext,
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

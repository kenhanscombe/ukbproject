import click
import withdraw


@click.command()
@click.option('-p', '--project-id',
              help='UKB project ID number (used to name files written to disk).')
@click.option('-w', '--withdrawal',
              help='Path to the withdrawal file.')
@click.option('-f', '--fam', help='Path to the fam file.')
@click.option('-s', '--sample', help='Path to the sample file.')
@click.option('-o', '--out-dir', default='./')
def exclude(project_id, withdrawal, fam, sample, out_dir):
    """Writes a file of withdrawal ids (.exclude) and a corresponding
    file of indeces (.index), to remove from the genotyped and imputed
    data. These withdrawal ids are a combination of ids in the
    withdrawals file and ids with the values 'dropout' or 'redacted'
    in the phenotype column of the fam file. The *_withdrawals.exclude
    file is accepted by PLINK --remove and QCTOOL --excl-samples, for
    genotyped and imputed files respectively. Both .exclude and .index
    files are one-per-line no header."""
    f_exclude, s_exclude = withdraw.withdraw_index(
        withdrawal, fam, sample)

    def write_excl(excl, gen, ext):
        if (gen == 'genotyped') & (ext == 'exclude'):
            id_col = 'fid'
        elif (gen == 'imputed') & (ext == 'exclude'):
            id_col = 'id1'
        else:
            id_col = 'index'

        (excl
         .loc[excl['exclude'] == 1, id_col]
         .to_csv('ukb' + project_id + '_' + gen + '_withdrawals.' + ext,
                 header=False, index=False))

    [write_excl(*i + (ext,))
        for i in zip([f_exclude, s_exclude], ['genotyped', 'imputed'])
        for ext in ['exclude', 'index']]


if __name__ == "__main__":
    exclude()

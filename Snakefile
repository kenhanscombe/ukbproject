import os
import glob
import re
import pandas as pd

from pathlib import Path


project_dir = config['project_dir']
pkg_dir = config['pkg_dir']

resources = Path(project_dir).parent / 'resources'
bin_dir = Path(project_dir).parent / 'bin'

ukbunpack = f'{bin_dir}/ukbunpack'
ukbconv = f'{bin_dir}/ukbconv'

dataset_ids = [re.sub(r'^.*ukb|\.enc', '', d) for d in glob.glob(f'{project_dir}/raw/*.enc')]

rule all:
    input:
        expand(f'{project_dir}/raw/ukb{{id}}.enc_ukb', id=dataset_ids),
        expand(f'{project_dir}/phenotypes/ukb{{id}}.csv', id=dataset_ids),
        expand(f'{project_dir}/phenotypes/ukb{{id}}.html', id=dataset_ids),
        expand(f'{project_dir}/phenotypes/ukb{{id}}_field_finder.txt', id=dataset_ids)
        # f'{project_dir}/phenotypes/ukb.field'


rule ukbunpack_decrypt:
    input:
        enc = f'{project_dir}/raw/ukb{{id}}.enc',
        key = f'{project_dir}/raw/ukb{{id}}.key'
    output:
        temp(f'{project_dir}/raw/ukb{{id}}.enc_ukb')
    shell:
        '''
        {ukbunpack} {input.enc} {input.key}
        '''


rule ukbconv_convert:
    input:
        f'{project_dir}/raw/ukb{{id}}.enc_ukb'
    output:
        csv = f'{project_dir}/phenotypes/ukb{{id}}.csv',
        html = f'{project_dir}/phenotypes/ukb{{id}}.html'
    params:
        out = f'{project_dir}/phenotypes/ukb{{id}}',
        enc = f'{resources}/encoding.ukb'
    shell:
        '''
        {ukbconv} {input} csv -o{params.out} -e{params.enc}
        {ukbconv} {input} docs -o{params.out} -e{params.enc}
        '''


rule munge_ukb_html:
    input:
        html = f'{project_dir}/phenotypes/ukb{{id}}.html'
    output:
        finder = f'{project_dir}/phenotypes/ukb{{id}}_field_finder.txt'
    params:
        basket = 'ukb{id}',
        out_dir = f'{project_dir}/phenotypes/'
    envmodules:
        "devtools/anaconda/2019.3-python3.7.3"
    shell:
        f'''
        {pkg_dir}/munge.py \
            --html {{input.html}} \
            --basket {{params.basket}} \
            --out-dir {{params.out_dir}}
        '''


# rule concatenate_field_finders:
#     input:
#         expand('phenotypes/ukb{id}_field_finder.txt', id=dataset_ids)
#     output:
#         'phenotypes/ukb.field'
#     run:
#         with open('phenotypes/ukb.field', "wb") as wf:

#             with open(
#                     "phenotypes/ukb{}_field_finder.txt".format(dataset_ids[0]),
#                     "rb") as rf:
#                 header = [next(rf) for lines in range(1)]
#                 wf.write(header[0])

#             for id in dataset_ids:
#                 with open(
#                         "phenotypes/ukb{}_field_finder.txt".format(id),
#                         "rb") as rf:
#                     next(rf)
#                     wf.write(rf.read())
